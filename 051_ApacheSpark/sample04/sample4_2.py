import os
import sys
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from flask import Flask, request, jsonify
from threading import Thread
from apache_atlas.client.base_client import AtlasClient

# Spark Config
CONF = SparkConf() \
    .setAppName("AtlasSchemaStreamingApp") \
    .set("spark.pyspark.python", "/usr/bin/python3") \
    .set("spark.pyspark.driver.python", "/usr/bin/python3")
os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3.12"
os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python3.12"
SPARK = SparkSession.builder.config(conf=CONF).getOrCreate()

# Flask Server
APP = Flask(__name__)

# Atlas client
ATLAS_CLIENT = AtlasClient("http://localhost:21000", ("admin", "admin"))

# Apache Atlas client settings
def atlas_type_to_spark_type(atlas_type):
    mapping = {
        "string": StringType(),
        "int": IntegerType(),
        "integer": IntegerType(),
    }
    return mapping.get(atlas_type.lower(), StringType())

def atlas_type_to_spark_type(atlas_type):
    """
    Convert Apache Atlas data types to Spark data types.
    Add more types if needed.
    """
    type_mapping = {
        "string": StringType(),
        "int": IntegerType(),
    }
    return type_mapping.get(atlas_type.lower(), StringType())

def get_entities_from_atlas(atlas_client: AtlasClient, schema_name, table_qualified_name):
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
        print(f"Failed to retrieve schema for '{schema_name}' (table: '{table_qualified_name}'):", e)
        raise

# schema transform
def schema_transform(df, target_schema):
    def convert_row(row):
        return (row["Name"], str(row["Age"]))
    return df.rdd.map(convert_row).toDF(target_schema)


# Flask REST APIエンドポイント
@APP.route('/transform', methods=['POST'])
def transform_data():
    try:
        # 入力JSONを取得
        input_json = request.get_json()
        input_table_source = input_json.get("table_source")
        input_schema_source_name = input_json.get("schema_source")
        input_table_target = input_json.get("table_target")
        input_schema_target_name = input_json.get("schema_target")
        input_data = input_json.get("data")

        if not all([input_table_source, input_schema_source_name, input_table_target, input_schema_target_name, input_data]):
            return jsonify({"error": "Missing required input parameters"}), 400

        # スキーマの取得
        schema_source = get_entities_from_atlas(ATLAS_CLIENT, input_schema_source_name, input_table_source)
        schema_target = get_entities_from_atlas(ATLAS_CLIENT, input_schema_target_name, input_table_target)
        if not schema_source or not schema_target:
            return jsonify({"error": "Failed to retrieve schemas from Apache Atlas"}), 500

        # 入力データフレームの作成
        df_source = SPARK.createDataFrame(input_data, schema_source)

        # Transform to target schema from source schema
        df_target = schema_transform(df_source, schema_target)

        # DataFrameをJSON形式に変換
        transformed_data = df_target.toJSON().collect()

        # 出力形式のJSONを構築
        output_json = {
            "table_source": input_table_source,
            "schema_source": input_schema_source_name,
            "table_target": input_table_target,
            "schema_target": input_schema_target_name,
            "data": [eval(record) for record in transformed_data]
        }

        return jsonify(output_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Flaskサーバ起動
def run_flask():
    APP.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))


# メイン関数
if __name__ == "__main__":
    Thread(target=run_flask).start()
