# =============================================================
#  ベースライン: PyTorch 単独（単一プロセスでバッチ推論）
#
#  parquet を pandas で全件ロードし、1プロセスでミニバッチを回して推論する。
#  - データ読み込みも前処理も推論も自分で手書きループする。
#  - 単一マシン(1CPU/1GPU)ぶんのスループットが上限。
#  - データが大きいと全件ロードでメモリを圧迫する。
#
#  末尾に SUMMARY 行を出力:
#    SUMMARY,pytorch,<rows>,<total_s>,<rows_per_s>
#
#    python3.12 02_pytorch_only.py --data data/rows_5000000.parquet
# =============================================================
import argparse
import time

import pandas as pd
import torch

from model import build_model, FEATURES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--batch", type=int, default=100_000)
    args = parser.parse_args()

    # 全件インメモリロード（単一マシンの制約）
    pdf = pd.read_parquet(args.data)
    rows = len(pdf)

    model = build_model()
    model.eval()

    X = torch.tensor(pdf[FEATURES].values, dtype=torch.float32)

    t0 = time.perf_counter()
    outputs = []
    with torch.no_grad():
        for i in range(0, rows, args.batch):
            outputs.append(model(X[i:i + args.batch]))
    _ = torch.cat(outputs)  # 実体化
    total_s = time.perf_counter() - t0
    rps = rows / total_s if total_s > 0 else float("inf")

    print("====  PyTorch only (single process)  ====")
    print("rows          = {0:,}".format(rows))
    print("total time    = {0:.3f}s".format(total_s))
    print("throughput    = {0:,.0f} rows/s".format(rps))
    print("SUMMARY,pytorch,{0},{1:.3f},{2:.0f}".format(rows, total_s, rps))


if __name__ == "__main__":
    main()
