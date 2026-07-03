# =============================================================
#  スケール可変のデータ生成（MLlib vs scikit-learn 比較用）
#
#  件数を --rows で可変にして parquet を出力する。
#  totalAmount は tripDistance / durationMin に対して既知の線形関係
#  （+ノイズ）を持たせているので、両ライブラリの回帰係数が一致する
#  はずで、「正しさの一致(parity)」を確認できる。
#
#  生成自体を Spark で行うことで、単一マシンのメモリに載らない規模の
#  データも分割して書き出せる（scikit-learn 側の限界を作るのが狙い）。
#
#    python3.12 01_generate_scalable_data.py --rows 1000000
# =============================================================
import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, randn, col


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1_000_000, help="生成する行数")
    parser.add_argument("--out", default=None, help="出力parquetパス（省略時は data/rows_<n>.parquet）")
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(root, "data", "rows_{0}.parquet".format(args.rows))

    spark = SparkSession.builder.master("local[*]").appName("GenScalableData").getOrCreate()

    df = (
        spark.range(args.rows)
        .withColumn("tripDistance", rand(seed=1) * 19.5 + 0.5)          # 0.5〜20.0
        .withColumn("passengerCount", (rand(seed=2) * 5 + 1).cast("int"))  # 1〜6
        .withColumn("durationMin", rand(seed=3) * 55 + 5)               # 5〜60
        # 既知の線形関係 totalAmount = 2.75*dist + 0.35*dur + 3.0 + noise
        .withColumn(
            "totalAmount",
            col("tripDistance") * 2.75 + col("durationMin") * 0.35 + randn(seed=4) * 2.0 + 3.0,
        )
        .select("tripDistance", "passengerCount", "durationMin", "totalAmount")
    )

    df.write.mode("overwrite").parquet(out)
    print("wrote {0} rows -> {1}".format(args.rows, out))
    spark.stop()


if __name__ == "__main__":
    main()
