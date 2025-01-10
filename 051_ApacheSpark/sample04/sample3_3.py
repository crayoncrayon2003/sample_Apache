import os
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from apache_atlas.client.base_client import AtlasClient

# スキーマ表示用関数
def show_schema(schema, name):
    print(f"Schema of {name}:")
    for field in schema.fields:
        print(f" - {field.name}: {field.dataType}")

# Apache Atlasのデータ型をPySparkのデータ型に変換
def atlas_type_to_spark_type(atlas_type):
    type_mapping = {
        "string": StringType(),
        "int": IntegerType(),
    }
    return type_mapping.get(atlas_type.lower(), StringType())

# Apache Atlasからスキーマを取得する関数
def get_schema_from_atlas(atlas_client, schema_name, table_qualified_name):
    try:
        # get table info
        table_entity = atlas_client.entity.get_entity_by_attribute(
            type_name="hive_table",
            uniq_attributes={"qualifiedName": table_qualified_name}
        )
        table_attributes = table_entity["entity"]["attributes"]

        if table_attributes.get("name") != schema_name:
            print(f"Schema name mismatch. Expected: {schema_name}, Found: {table_attributes.get('name')}")
            return None

        # get columns info
        column_guids = [col["guid"] for col in table_attributes.get("columns", [])]
        struct_fields = []

        # get detail
        for column_guid in column_guids:
            column_entity = atlas_client.entity.get_entity_by_guid(column_guid)
            column_name = column_entity["entity"]["attributes"]["name"]
            column_type = column_entity["entity"]["attributes"].get("type", "string")
            spark_type = atlas_type_to_spark_type(column_type)
            struct_fields.append(StructField(column_name, spark_type, True))

        # create schema
        return StructType(struct_fields)
    except Exception as e:
        print(f"Error retrieving schema from Atlas for table {table_qualified_name}: {e}")
        return None

# schema transform
def schema_transform(df, target_schema):
    def convert_row(row):
        return (row["Name"], str(row["Age"]))
    return df.rdd.map(convert_row).toDF(target_schema)

def main():
    # SparkConfの設定
    conf = SparkConf() \
            .setAppName("AtlasSchemaTransformationExample") \
            .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
            .set("spark.pyspark.python", "/usr/bin/python3.12")
    os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3.12"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python3.12"
    spark = SparkSession \
            .builder \
            .config(conf=conf) \
            .getOrCreate()

    # Define Atlas client
    atlas_client = AtlasClient("http://localhost:21000", ("admin", "admin"))

    # Load schemas from Apache Atlas
    schema_source = get_schema_from_atlas(atlas_client, "source_schema", "default.source_schema@hive")
    schema_target = get_schema_from_atlas(atlas_client, "target_schema", "default.target_schema@hive")

    if schema_source is None or schema_target is None:
        print("Failed to retrieve schemas from Apache Atlas. Ensure that the tables exist in the catalog.")
        return

    # show loaded schemas
    show_schema(schema_source, "Loaded SOURCE_SCHEMA")
    show_schema(schema_target, "Loaded TARGET_SCHEMA")

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
