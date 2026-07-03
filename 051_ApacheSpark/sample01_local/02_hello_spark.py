import os
from pyspark.sql.functions import col, avg, count
from pyspark.sql import SparkSession

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

# Start Spark in local mode (“local”).
spark = SparkSession.builder.master("local").appName("HelloSpark").getOrCreate()


def main():
    # 1) Load a CSV file as a DataFrame
    df = spark.read.load(DUMMY_TAXIDATA, format="csv", header=True, inferSchema=True)

    # 2) Check the schema (columns and data types)
    print("====  Schema  ====")
    df.printSchema()

    # 3) Display the first few entries
    print("====  Show 5 rows  ====")
    df.show(5, truncate=False)

    # 4) Count the total number of items
    print("====  Row count  ====")
    print("rows = {0}".format(df.count()))

    # 5) Aggregate by paymentType (first aggregation experience)
    print("====  Aggregate by paymentType  ====")
    (
        df.groupBy("paymentType")
          .agg(
              count("*").alias("num"),
              avg(col("totalAmount")).alias("avgAmount"),
          )
          .orderBy(col("num").desc())
          .show(truncate=False)
    )


if __name__ == "__main__":
    main()
    spark.stop()
