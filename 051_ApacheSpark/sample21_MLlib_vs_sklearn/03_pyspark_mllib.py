# =============================================================
#  PySpark MLlib（分散・パーティション処理）
#
#  同じ parquet を Spark で読み、LinearRegression を学習する。
#  - データはパーティション単位で処理されるため、単一マシンのメモリに
#    載らない規模でも動く。Python ドライバの RSS はほぼ一定のまま。
#  - 小データでは起動/シリアライズのオーバーヘッドで sklearn より遅い。
#
#  末尾に機械可読な SUMMARY 行を出力する:
#    SUMMARY,mllib,<rows>,<load_s>,<fit_s>,<total_s>,<peakRSS_MB>,<r2>
#
#    python3.12 03_pyspark_mllib.py --data data/rows_1000000.parquet
# =============================================================
import argparse
import resource
import time

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

FEATURES = ["tripDistance", "passengerCount", "durationMin"]
LABEL = "totalAmount"


def peak_rss_mb():
    # Python ドライバプロセスのピーク RSS。実データは JVM/executor 側にあるため
    # sklearn と違ってここはほぼ増えない（=メモリ優位の可視化）。
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="入力parquetパス")
    args = parser.parse_args()

    spark = SparkSession.builder.master("local[*]").appName("MLlibRegression").getOrCreate()

    # ---- 読み込み（遅延評価。実際の読みは後続のアクションで走る） ----
    t0 = time.perf_counter()
    df = spark.read.parquet(args.data)
    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

    assembler = VectorAssembler(inputCols=FEATURES, outputCol="features")
    lr = LinearRegression(featuresCol="features", labelCol=LABEL)

    # ---- 学習（ここで初めてデータが読まれ、分散処理される） ----
    t1 = time.perf_counter()
    model = lr.fit(assembler.transform(train_df))
    fit_s = time.perf_counter() - t1

    predictions = model.transform(assembler.transform(test_df))
    r2 = RegressionEvaluator(labelCol=LABEL, predictionCol="prediction", metricName="r2").evaluate(predictions)

    rows = df.count()  # レポート用（全件を1パス）
    total_s = time.perf_counter() - t0
    load_s = total_s - fit_s  # 参考値（読み込みは遅延のため厳密ではない）

    print("====  PySpark MLlib  ====")
    print("rows       = {0:,}".format(rows))
    print("coef       = {0}".format(model.coefficients))
    print("intercept  = {0:.4f}".format(model.intercept))
    print("fit   time = {0:.3f}s".format(fit_s))
    print("total time = {0:.3f}s".format(total_s))
    print("peak  RSS  = {0:.1f} MB (Python driver)".format(peak_rss_mb()))
    print("R2         = {0:.4f}".format(r2))
    print("SUMMARY,mllib,{0},{1:.3f},{2:.3f},{3:.3f},{4:.1f},{5:.4f}".format(
        rows, load_s, fit_s, total_s, peak_rss_mb(), r2))

    spark.stop()


if __name__ == "__main__":
    main()
