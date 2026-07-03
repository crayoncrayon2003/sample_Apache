# =============================================================
#  推論/学習用のダミー特徴量データ生成（件数可変）
#
#  Spark で parquet を生成する。tripDistance / passengerCount /
#  durationMin と、既知の線形関係に基づく totalAmount を持つ。
#
#    python3.12 01_generate_data.py --rows 5000000
# =============================================================
import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, randn, col


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5_000_000)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(root, "data", "rows_{0}.parquet".format(args.rows))

    spark = SparkSession.builder.master("local[*]").appName("GenFeatureData").getOrCreate()

    df = (
        spark.range(args.rows)
        .withColumn("tripDistance", rand(seed=1) * 19.5 + 0.5)
        .withColumn("passengerCount", (rand(seed=2) * 5 + 1).cast("int"))
        .withColumn("durationMin", rand(seed=3) * 55 + 5)
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
