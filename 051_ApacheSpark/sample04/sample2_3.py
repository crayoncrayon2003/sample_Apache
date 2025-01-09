import os
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

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

# Load schema from Hive Metastore
def load_schema_from_hive(spark, table_name):
    try:
        df = spark.table(table_name)
        return df.schema
    except Exception as e:
        print(f"Error loading schema from Hive: {e}")
        return None

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

    # Load schemas from Hive Metastore
    schema_source = load_schema_from_hive(spark, "source_schema")
    schema_target = load_schema_from_hive(spark, "target_schema")

    if schema_source is None or schema_target is None:
        print("Failed to load schemas from Hive. Ensure that the tables exist in the Hive Metastore.")
        return

    # show loaded schemas
    show_schema(schema_source, "Loaded SCHEMA_SOURCE")
    show_schema(schema_target, "Loaded SCHEMA_TARGET")

    # create sample data
    data = [
        {"Name": "Alice", "Age": 25},
        {"Name": "Bob", "Age": 30},
        {"Name": "Cathy", "Age": 28}
    ]

    # create DataFrame
    df_source = spark.createDataFrame(data, schema_source)

    # show DataFrame
    df_source.show()

    # Transform to target schema from source schema
    df_target = schema_transform(df_source, schema_target)

    # show transformed DataFrame
    df_target.show()

    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main()
