# =============================================================
#  PySpark + PyTorch: 分散バッチ推論
#
#  「モデルは PyTorch、データの並列処理は Spark」という王道パターン。
#    1) 学習済みモデルの重みを broadcast で各 executor に配る
#    2) mapInPandas でパーティションごとに PyTorch 推論を並列実行
#    3) 「読み込み→前処理→推論→書き出し」を1本の分散パイプラインに融合
#
#  単独版(02)との差：
#    - 複数コア/複数executorで並列 → スループットが伸びる
#    - データはパーティション単位なので単一マシンのメモリに載らなくてよい
#    - Spark のデータパイプライン(ETL)にそのまま組み込める
#
#  末尾に SUMMARY 行を出力:
#    SUMMARY,spark_pytorch,<rows>,<total_s>,<rows_per_s>
#
#    python3.12 03_pyspark_pytorch_inference.py --data data/rows_5000000.parquet
# =============================================================
import argparse
import os
import sys
import time

# Spark の worker と driver で同じ Python を使う（バージョン不一致エラー対策）。
# シェルに古い PYSPARK_PYTHON が残っていても勝てるよう、無条件で上書きする。
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType

from model import build_model, FEATURES

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default=os.path.join(ROOT, "data", "predictions.parquet"))
    args = parser.parse_args()

    spark = SparkSession.builder.master("local[*]").appName("SparkPyTorchInference").getOrCreate()
    # executor 側でも model.py を import できるよう配布（クラスタでも有効）
    spark.sparkContext.addPyFile(os.path.join(ROOT, "model.py"))

    # 学習済みモデルの重みを broadcast（ここでは初期化済みモデルを推論に使用）
    model = build_model()
    model.eval()
    state = {k: v.cpu() for k, v in model.state_dict().items()}
    bc_state = spark.sparkContext.broadcast(state)

    df = spark.read.parquet(args.data).select(*FEATURES)

    # 出力スキーマ = 入力特徴量 + prediction(double)
    out_schema = StructType(df.schema.fields + [StructField("prediction", DoubleType())])

    def predict_partition(iterator):
        # このブロックは各 executor 上で実行される
        import torch
        from model import build_model as _build

        m = _build()
        m.load_state_dict(bc_state.value)
        m.eval()
        with torch.no_grad():
            for pdf in iterator:
                x = torch.tensor(pdf[FEATURES].values, dtype=torch.float32)
                out = pdf.copy()
                out["prediction"] = m(x).numpy().astype("float64")
                yield out

    t0 = time.perf_counter()
    predictions = df.mapInPandas(predict_partition, schema=out_schema)
    # アクションで実体化（書き出し＝ETLの一部として）
    predictions.write.mode("overwrite").parquet(args.out)
    total_s = time.perf_counter() - t0

    rows = spark.read.parquet(args.out).count()
    rps = rows / total_s if total_s > 0 else float("inf")

    print("====  Spark + PyTorch (distributed inference)  ====")
    print("rows          = {0:,}".format(rows))
    print("total time    = {0:.3f}s".format(total_s))
    print("throughput    = {0:,.0f} rows/s".format(rps))
    print("wrote -> {0}".format(args.out))
    print("SUMMARY,spark_pytorch,{0},{1:.3f},{2:.0f}".format(rows, total_s, rps))

    spark.stop()


if __name__ == "__main__":
    main()
