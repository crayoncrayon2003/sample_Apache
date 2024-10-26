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
            "paymentType",
            "totalAmount"
        )
        .withColumnRenamed("totalAmount", "Amount")
        .orderBy("pickupDateTime")
        .withColumn("pickupYear", year(col("pickupDateTime")))
        .withColumn("pickupMonth", month(col("pickupDateTime")))
        .withColumn("pickupDay", dayofmonth(col("pickupDateTime")))
        .where("pickupDateTime >= '2024-01-01' AND pickupDateTime < '2024-04-30'")
    )
    print("====  Read Data ====")
    df_result.show(10,truncate=False)

    print("====  Cast DateTime ====")
    df_result = df_result.withColumn("pickupDateTime", df_result["pickupDateTime"].cast("timestamp"))
    df_result = df_result.withColumn("dropoffDateTime", df_result["dropoffDateTime"].cast("timestamp"))
    df_result.show(10,truncate=False)

    print("====  Dataa Info  ====")
    num = df_result.filter((col('paymentType') == 'Cash')).count()
    print('cash num {0}'.format(num) )
    num = df_result.filter((col('paymentType') == 'Cash') | (col('paymentType') == 'Card') ).count()
    print('cash and card num {0}'.format(num) )


    # Get ChannelID List
    paymentTypes = df_result.select('paymentType').distinct()
    paymentTypes = paymentTypes.select("paymentType").select(collect_list("paymentType")).first()[0]
    for type  in paymentTypes:
        print("====  "+ str(type) +"  ====")
        typegrupe = df_result.filter(col('paymentType') == type)
        typegrupe.show(10,truncate=False)


if __name__ == "__main__":
    main()
