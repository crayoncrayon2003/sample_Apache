# =============================================================
#  Spark SQL (1) : DataFrame API アプローチ
#
#  select / withColumn / where / orderBy などを「メソッドチェーン」で
#  記述するスタイル。同じ処理を SQL 文字列で書いた例は 03_spark_sql.py。
#  結果は parquet / csv に書き出す。
# =============================================================
import os
from pyspark.sql.functions import*
from pyspark.sql.session import SparkSession
from pyspark.context import SparkContext

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT,"DummyTaxiData.csv")
DUMMY_TYPEDATA = os.path.join(ROOT,"DummyPaymentType.csv")

OUTPUT_DIR      = os.path.join(ROOT,"result")
OUTPUT_PARQUET  = os.path.join(OUTPUT_DIR,"result.parquet")
OUTPUT_CSVFILE1 = os.path.join(OUTPUT_DIR,"result1.csv")
OUTPUT_CSVFILE2 = os.path.join(OUTPUT_DIR,"result2.csv")

sc = SparkContext("local")
spark = SparkSession(sc)

def main():
    df = spark.read.load(DUMMY_TAXIDATA, format='csv', header=True)

    df_result = (
        df
        .select(
            "pickupDateTime",
            "dropoffDateTime",
            "passengerCount",
            "tripDistance",
            "totalAmount"
        )
        .withColumnRenamed("totalAmount", "Amount")
        .orderBy("pickupDateTime")
        .withColumn("pickupYear", year(col("pickupDateTime")))
        .withColumn("pickupMonth", month(col("pickupDateTime")))
        .withColumn("pickupDay", dayofmonth(col("pickupDateTime")))
        .where("pickupDateTime >= '2024-01-01' AND pickupDateTime < '2024-04-30'")
    )

    print(df_result.head())

    os.makedirs(OUTPUT_DIR,exist_ok=True)

    (
        df_result
            .write
            .mode("overwrite")
            .partitionBy("pickupYear", "pickupMonth", "pickupDay")
            .parquet(OUTPUT_PARQUET)
    )

    (
        df_result
            .coalesce(1)
            .write
            .mode("overwrite")
            .csv(OUTPUT_CSVFILE1)
    )

    pdf = df_result.toPandas()
    pdf.to_csv(OUTPUT_CSVFILE2, header=True, index=False)

if __name__ == "__main__":
    main()
