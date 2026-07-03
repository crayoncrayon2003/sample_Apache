# =============================================================
#  PySpark + PyTorch: 分散学習（TorchDistributor / DDP）
#
#  Spark 3.4+ の pyspark.ml.torch.distributor.TorchDistributor を使い、
#  PyTorch の DistributedDataParallel(DDP) 学習を複数プロセス/ノードで走らせる。
#  Spark は「学習ワーカーの起動・配置・環境変数(RANK等)の設定」を担い、
#  実際の学習ループは通常の PyTorch DDP コードのまま。
#
#  比較のため、同じモデルを
#    A) 単一ノード（1プロセス）で学習       -> baseline
#    B) TorchDistributor で分散(num_processes) -> distributed
#  それぞれの所要時間を SUMMARY 行で出力する。
#
#  末尾に SUMMARY 行:
#    SUMMARY,single_node_train,<rows>,<total_s>
#    SUMMARY,distributed_train,<rows>,<total_s>
#
#    python3.12 04_torch_distributor_train.py --rows 200000 --epochs 5 --procs 2
# =============================================================
import argparse
import os
import sys
import time

# Spark の worker と driver で同じ Python を使う（バージョン不一致エラー対策）。
# シェルに古い PYSPARK_PYTHON が残っていても勝てるよう、無条件で上書きする。
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# TorchDistributor が起動する子プロセスでも model.py を import できるよう、
# このスクリプトのディレクトリを PYTHONPATH に通す（子プロセスへ継承される）。
ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ["PYTHONPATH"] = ROOT + os.pathsep + os.environ.get("PYTHONPATH", "")


def make_dataset(rows, seed):
    """既知の線形関係に基づく合成データ（学習が収束することを確認できる）。"""
    import torch
    g = torch.Generator().manual_seed(seed)
    dist_ = torch.rand(rows, generator=g) * 19.5 + 0.5
    passengers = (torch.rand(rows, generator=g) * 5 + 1).round()
    duration = torch.rand(rows, generator=g) * 55 + 5
    X = torch.stack([dist_, passengers, duration], dim=1)
    y = dist_ * 2.75 + duration * 0.35 + 3.0 + torch.randn(rows, generator=g) * 2.0
    return X, y


def train_single_node(rows, epochs):
    """単一プロセス学習（比較のベースライン）。"""
    import torch
    import torch.nn as nn
    from model import FarePredictor

    torch.manual_seed(0)
    X, y = make_dataset(rows, seed=0)
    model = FarePredictor()
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    loss_fn = nn.MSELoss()
    for _ in range(epochs):
        opt.zero_grad()
        loss = loss_fn(model(X), y)
        loss.backward()
        opt.step()
    return float(loss.item())


def train_ddp(rows, epochs):
    """DDP 学習関数。TorchDistributor から各ワーカーで実行される。

    Spark が RANK / WORLD_SIZE / MASTER_ADDR 等を環境変数で渡すので、
    init_process_group はそれを読んで初期化する（通常の PyTorch DDP と同じ）。
    """
    import os
    import torch
    import torch.nn as nn
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel as DDP
    from model import FarePredictor

    dist.init_process_group(backend="gloo")  # CPU 向けバックエンド
    rank = dist.get_rank()
    world = dist.get_world_size()

    # データをランクごとに分割（データ並列）
    X, y = make_dataset(rows, seed=rank)

    torch.manual_seed(0)
    model = FarePredictor()
    ddp_model = DDP(model)
    opt = torch.optim.Adam(ddp_model.parameters(), lr=1e-2)
    loss_fn = nn.MSELoss()

    last = 0.0
    for _ in range(epochs):
        opt.zero_grad()
        loss = loss_fn(ddp_model(X), y)
        loss.backward()   # DDP が全ワーカーの勾配を all-reduce で同期
        opt.step()
        last = float(loss.item())

    dist.destroy_process_group()
    return {"rank": rank, "world": world, "loss": last}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=200_000)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--procs", type=int, default=2, help="分散学習のプロセス数")
    args = parser.parse_args()

    # A) 単一ノード
    t0 = time.perf_counter()
    loss = train_single_node(args.rows, args.epochs)
    single_s = time.perf_counter() - t0
    print("====  A) single-node training  ====")
    print("final loss = {0:.4f}  time = {1:.3f}s".format(loss, single_s))
    print("SUMMARY,single_node_train,{0},{1:.3f}".format(args.rows, single_s))

    # B) 分散（TorchDistributor）
    # TorchDistributor はアクティブな Spark セッションを必要とするため、先に生成する。
    from pyspark.sql import SparkSession
    from pyspark.ml.torch.distributor import TorchDistributor

    spark = SparkSession.builder.master("local[*]").appName("TorchDistributorTrain").getOrCreate()

    t1 = time.perf_counter()
    # local_mode=True: ドライバのマシン上で procs 個のワーカーを起動
    result = TorchDistributor(
        num_processes=args.procs, local_mode=True, use_gpu=False
    ).run(train_ddp, args.rows, args.epochs)
    dist_s = time.perf_counter() - t1
    print("====  B) distributed training (TorchDistributor)  ====")
    print("workers={0}  result={1}  time = {2:.3f}s".format(args.procs, result, dist_s))
    print("SUMMARY,distributed_train,{0},{1:.3f}".format(args.rows, dist_s))

    spark.stop()

    print()
    print("読み方: 小データ/1ノードでは分散のオーバーヘッド(プロセス起動・勾配同期)で")
    print("        単一ノードの方が速いこともある。データ量とノード数が増えるほど、")
    print("        1エポックあたりの実効スループットで分散学習が有利になる。")


if __name__ == "__main__":
    main()
