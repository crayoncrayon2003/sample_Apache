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
    schemaA = load_schema(os.path.join(ROOT,"schemaA.avsc"))
    schemaB = load_schema(os.path.join(ROOT,"schemaB.avsc"))

    source_data = {
        "name": "Sample Entity",
        "temperature": 20,
        "humidity": 50
    }
    validation(source_data, schemaA)

    # Serialize
    buffer = BytesIO()
    source_writer  = DatumWriter(schemaA)
    source_encoder = BinaryEncoder(buffer)
    source_writer.write(source_data, source_encoder)


    # deserialize
    buffer.seek(0)
    target_reader = DatumReader(schemaB)
    target_decoder = BinaryDecoder(buffer)
    target_data = target_reader.read(target_decoder)

    validation(target_data, schemaB)

    print("Data mapped from Schema A to Schema B:")
    print(target_data)

if __name__ == "__main__":
    main()
