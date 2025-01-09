import os
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

SCHEMA_SOURCE = StructType([
    StructField("Name", StringType(), True),
    StructField("Age", IntegerType(), True)
])

SCHEMA_TARGET = StructType([
    StructField("Name", StringType(), True),
    StructField("Age", StringType(), True)
])

# show schema
def show_schema(schema, name):
    print(f"Schema of {name}:")
    for field in schema.fields:
        print(f" - {field.name}: {field.dataType}")

# Define schema transformation function
def schema_transform(df, target_schema):
    def convert_row(row):
        return (row["Name"], str(row["Age"]))
    return df.rdd.map(convert_row).toDF(target_schema)


def main():
    conf = SparkConf() \
            .setAppName("SchemaTransformationExample") \
            .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
            .set("spark.pyspark.python", "/usr/bin/python3.12")
    os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3.12"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python3.12"

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # create sample data
    data = [
        ("Alice", 25),
        ("Bob", 30),
        ("Cathy", 28)
    ]

    # create DataFrame
    df_source = spark.createDataFrame(data, SCHEMA_SOURCE)

    # show DataFrame
    df_source.show()

    # show source schema
    show_schema(SCHEMA_SOURCE, "SCHEMA_SOURCE")

    # Transform to target schema from source schema
    df_target = schema_transform(df_source, SCHEMA_TARGET)

    # show DataFrame
    df_target.show()

    # show target schema
    show_schema(SCHEMA_TARGET, "SCHEMA_TARGET")


    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main()
