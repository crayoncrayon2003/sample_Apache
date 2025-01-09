import os
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Save schema to Hive Metastore
def save_schema_to_hive(spark, table_name, schema):
    # delete table
    spark.sql(f"""DROP TABLE IF EXISTS {table_name}""")

    # create table
    df = spark.createDataFrame([], schema)
    df.write.mode("overwrite").saveAsTable(table_name)

def main():
    conf = SparkConf() \
            .setAppName("SchemaTransformationExample") \
            .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
            .set("spark.pyspark.python", "/usr/bin/python3.12")
    os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3.12"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python3.12"
    spark = SparkSession \
        .builder \
        .config(conf=conf) \
        .enableHiveSupport() \
        .getOrCreate()

    # Save source schema to Hive Metastore
    schema_source = StructType([
        StructField("Name", StringType(), True),
        StructField("Age", IntegerType(), True)
    ])
    save_schema_to_hive(spark, "source_schema", schema_source)

    # Save target schema to Hive Metastore
    schema_target = StructType([
        StructField("Name", StringType(), True),
        StructField("Age", StringType(), True)
    ])
    save_schema_to_hive(spark, "target_schema", schema_target)

    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main()



