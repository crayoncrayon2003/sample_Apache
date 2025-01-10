import os
from flask import Flask, request, jsonify
import pandas as pd
from apache_atlas.client.base_client import AtlasClient

# Flask Server
APP = Flask(__name__)

# Apache Atlas client
ATLAS_CLIENT = AtlasClient("http://localhost:21000", ("admin", "admin"))

# スキーマ取得関数 (Apache Atlasからスキーマを取得)
def get_entities_from_atlas(atlas_client:AtlasClient, schema_name, table_qualified_name):
    try:
        table_entity = atlas_client.entity.get_entity_by_attribute(
            type_name="hive_table",
            uniq_attributes={"qualifiedName": table_qualified_name}
        )
        table_attributes = table_entity["entity"]["attributes"]

        if table_attributes.get("name") != schema_name:
            raise ValueError(f"Schema name mismatch: Expected {schema_name}, Found {table_attributes.get('name')}")

        column_guids = [col["guid"] for col in table_attributes.get("columns", [])]
        schema = {}

        for column_guid in column_guids:
            column_entity = atlas_client.entity.get_entity_by_guid(column_guid)
            column_name = column_entity["entity"]["attributes"]["name"]
            column_type = column_entity["entity"]["attributes"].get("type", "string").lower()
            schema[column_name] = column_type

        return schema

    except Exception as e:
        print(f"Failed to retrieve schema from Atlas: {e}")
        return None

# スキーマ変換関数
def schema_transform(data, source_schema, target_schema):
    df = pd.DataFrame(data)
    transformed_data = {}

    for column, target_type in target_schema.items():
        if column in df.columns:
            if target_type == "int":
                transformed_data[column] = df[column].astype(int)
            elif target_type == "string":
                transformed_data[column] = df[column].astype(str)
        else:
            transformed_data[column] = None  # 欠損列に対処

    return pd.DataFrame(transformed_data)

# Flaskエンドポイント
@APP.route('/transform', methods=['POST'])
def transform_data():
    try:
        # 入力JSONの取得
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

        # スキーマ変換
        transformed_df = schema_transform(input_data, schema_source, schema_target)

        # 出力形式のJSONを構築
        output_data = transformed_df.to_dict(orient="records")
        output_json = {
            "table_source": input_table_source,
            "schema_source": input_schema_source_name,
            "table_target": input_table_target,
            "schema_target": input_schema_target_name,
            "data": output_data
        }

        return jsonify(output_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flaskサーバ起動
def run_flask():
    APP.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", 5000)))

# メイン関数
if __name__ == "__main__":
    run_flask()
