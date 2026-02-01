import os
from monitor import Monitor
from pyspark.sql.functions import *
from pyspark.sql.session import SparkSession
from pyspark.context import SparkContext
from pyspark.conf import SparkConf

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT,"DummyTaxiData.csv")

mon = Monitor()
mon.start()

conf = SparkConf()
conf.set("spark.driver.memory", "4g")
conf.set("spark.executor.memory", "4g")
conf.set("spark.sql.shuffle.partitions", "8")

sc = SparkContext("local[*]", conf=conf)
spark = SparkSession(sc)

# CSVを読み込み（スキーマ推論を使用）
df = spark.read.load(
    DUMMY_TAXIDATA,
    format='csv',
    header=True,
    inferSchema=True
)

mon.sample()

# 日付型に変換してフィルタリング
df_filtered = (
    df
    .withColumn("pickupDateTime", col("pickupDateTime").cast("timestamp"))
    .where("pickupDateTime >= '2024-01-01' AND pickupDateTime < '2024-04-30'")
)

mon.sample()

# 集計（遅延評価のため、ここで実際の計算が走る）
result = (
    df_filtered
    .groupBy("paymentType")
    .agg(
        count("paymentType").alias("count"),
        sum("totalAmount").alias("sales")
    )
)

# 結果を取得（アクションをトリガー）
result_data = result.collect()

mon.sample()

elapsed, mem = mon.stop()
print("SPARK elapsed={:.2f}s  peak_mem={:.1f}MB".format(elapsed, mem))
print("\nResults:")
for row in result_data:
    print(f"  {row['paymentType']}: count={row['count']}, sales={row['sales']:.2f}")

spark.stop()