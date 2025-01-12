import os
import json
import avro.schema
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from io import BytesIO

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_schema(path):
    schema = None
    with open(path, "r") as schema_file:
        schema = avro.schema.parse(schema_file.read())
    return schema

def validation(data, schema):
    writer = DatumWriter(schema)
    try:
        with BytesIO() as buffer:
            encoder = BinaryEncoder(buffer)
            writer.write(data, encoder)
        print("Valid data:", data)
    except Exception as e:
        print(f"Validation Error: {e}")

def main():
    schema_json = load_schema(os.path.join(ROOT,"json_schema.avsc"))
    schema_ngsi = load_schema(os.path.join(ROOT,"ngsi_schema.avsc"))

    data_source = {
        "name": "Sample Entity",
        "temperature": 20,
        "humidity": 50
    }
    validation(data_source, schema_json)

    # Serialize(schema_json)
    source_buffer = BytesIO()
    source_writer  = DatumWriter(schema_json)
    source_encoder = BinaryEncoder(source_buffer)
    source_writer.write(data_source, source_encoder)

    # Insert custom conversion logic
    source_buffer.seek(0)
    source_custum_reader  = DatumReader(schema_json)
    source_custum_decoder = BinaryDecoder(source_buffer)
    source_data_custum_read = source_custum_reader.read(source_custum_decoder)

    # mapping for schema_ngsi
    mapping = {
        "id": "generated-id",
        "type": "EntityType",
        "name": {
            "type": "Text",
            "value": source_data_custum_read["name"],
            "metadata": {}
        },
        "temperature": {
            "type": "Integer",
            "value": source_data_custum_read["temperature"],
            "metadata": {}
        },
        "humidity": {
            "type": "Integer",
            "value": source_data_custum_read["humidity"],
            "metadata": {}
        }
    }
    # ReSerialize(schema_ngsi)
    target_buffer  = BytesIO()
    target_custum_writer  = DatumWriter(schema_ngsi)
    target_custum_encoder = BinaryEncoder(target_buffer)
    target_custum_writer.write(mapping, target_custum_encoder)

    # Deserialize(schema_ngsi)
    target_buffer.seek(0)
    target_reader = DatumReader(schema_ngsi)
    target_decoder = BinaryDecoder(target_buffer)
    target_data = target_reader.read(target_decoder)

    validation(target_data, schema_ngsi)

    print("Data mapped from Schema A to Schema B:")
    print(target_data)

if __name__ == "__main__":
    main()
