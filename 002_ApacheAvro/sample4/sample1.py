import os
import re
import json
import avro.schema
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from io import BytesIO


class DataModelTransformer:
    def __init__(self, source_schema_path, target_schema_path, mapping_path):
        self.source_schema = self._load_schema(source_schema_path)
        self.target_schema = self._load_schema(target_schema_path)
        self.mapping = self._load_json(mapping_path)
        self.pattern = re.compile(r'^source\[(["\'])(.+?)\1\]$')

    def _load_schema(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema file '{path}' not found.")
        with open(path, "r") as file:
            return avro.schema.parse(file.read())

    def _load_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"JSON file '{path}' not found.")
        try:
            with open(path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in '{path}': {e}")

    def _process_mapping(self, data, source):
        # self._process_mapping_recursion(data, source)
        self._process_mapping_loop(data, source)

    def _process_mapping_recursion(self, data, source):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._process_mapping_recursion(value, source)
                elif isinstance(value, str):
                    match = self.pattern.match(value)
                    if match:
                        source_key = match.group(2)
                        if source_key in source:
                            data[key] = source[source_key]
                        else:
                            raise KeyError(f"Key '{source_key}' not found in source.")
        elif isinstance(data, list):
            for item in data:
                self._process_mapping_recursion(item, source)

    def _process_mapping_loop(self, data, source):
        stack = [(data, source)]

        while stack:
            current_data, current_source = stack.pop()

            if isinstance(current_data, dict):
                for key, value in current_data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        stack.append((value, current_source))
                    elif isinstance(value, str):
                        match = self.pattern.match(value)
                        if match:
                            source_key = match.group(2)
                            if source_key in current_source:
                                current_data[key] = current_source[source_key]
                            else:
                                raise KeyError(f"Key '{source_key}' not found in source.")
            elif isinstance(current_data, list):
                for item in current_data:
                    stack.append((item, current_source))

    def validate(self, data, schema):
        writer = DatumWriter(schema)
        schema_name = schema.fullname if hasattr(schema, 'fullname') else "Unknown Schema"
        try:
            with BytesIO() as buffer:
                encoder = BinaryEncoder(buffer)
                writer.write(data, encoder)
            return True
        except Exception as e:
            print(f"Validation Error in '{schema_name}': {e}")
            return False

    def transform(self, source_data):
        if not self.validate(source_data, self.source_schema):
            raise ValueError("Source data validation failed.")

        # Serialize source data
        source_buffer = BytesIO()
        source_writer = DatumWriter(self.source_schema)
        source_encoder = BinaryEncoder(source_buffer)
        source_writer.write(source_data, source_encoder)

        # Deserialize source data
        source_buffer.seek(0)
        source_reader = DatumReader(self.source_schema)
        source_decoder = BinaryDecoder(source_buffer)
        source = source_reader.read(source_decoder)

        # Apply mapping to generate target data
        target_data = self.mapping.copy()
        self._process_mapping(target_data, source)

        # Validate transformed target data
        if not self.validate(target_data, self.target_schema):
            raise ValueError("Target data validation failed.")

        return target_data

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    source_schema_path = os.path.join(root, "json_schema.avsc")
    target_schema_path = os.path.join(root, "ngsi_schema.avsc")
    mapping_path = os.path.join(root, "mapping.json")

    source_data = {
        "name": "Sample Entity",
        "temperature": 20,
        "humidity": 50
    }

    try:
        transformer = DataModelTransformer(source_schema_path, target_schema_path, mapping_path)

        # Source data validation
        if not transformer.validate(source_data, transformer.source_schema):
            print("Source data validation failed.")
            return

        # Data Model Transformer
        target_data = transformer.transform(source_data)

        # Target data validation
        if not transformer.validate(target_data, transformer.target_schema):
            print("Target data validation failed.")
            return

    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"Error: {e}")

    print("Source data:")
    print(json.dumps(source_data, indent=2))
    print("Target data:")
    print(json.dumps(target_data, indent=2))

if __name__ == "__main__":
    main()
