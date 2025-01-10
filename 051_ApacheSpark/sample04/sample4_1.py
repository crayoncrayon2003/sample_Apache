from apache_atlas.client.base_client import AtlasClient
from apache_atlas.model.instance import AtlasEntity, AtlasEntitiesWithExtInfo
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

def create_schema_entities_in_atlas(atlas_client, schema_name, schema_fields, table_qualified_name):
    # Provisional GUIDs for table and columns
    table_guid = f"-{hash(schema_name) % 10000}"
    column_guids = [f"-{hash(field['name']) % 10000}" for field in schema_fields]

    # Define table entity
    table_entity = AtlasEntity()
    table_entity.guid = table_guid
    table_entity.typeName = "hive_table"
    table_entity.attributes = {
        "name": schema_name,
        "qualifiedName": table_qualified_name,
        "owner": "admin",
        "description": f"Schema for table {schema_name}",
    }

    # Define column entities
    column_entities = []
    for guid, field in zip(column_guids, schema_fields):
        column_entity = AtlasEntity()
        column_entity.guid = guid
        column_entity.typeName = "hive_column"
        column_entity.attributes = {
            "name": field["name"],
            "qualifiedName": f"{table_qualified_name}.{field['name']}",
            "type": field["type"],
            "owner": "admin",
            "table": {"guid": table_guid}
        }
        column_entities.append(column_entity)

    # Combine entities
    entities_with_ext_info = AtlasEntitiesWithExtInfo()
    entities_with_ext_info.entities = [table_entity] + column_entities

    # Send to Atlas
    try:
        response = atlas_client.entity.create_entities(entities_with_ext_info)
        print(f"Entities for {schema_name} successfully created in Apache Atlas.")
        # print("Response:", response)
    except Exception as e:
        print(f"Failed to create entities for {schema_name}:", e)
        raise


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


# show schema
def show_schema(schema, name):
    print(f"Schema of {name}:")
    for field in schema.fields:
        print(f" - {field.name}: {field.dataType}")

def main():
    # Define Atlas client
    atlas_client = AtlasClient("http://localhost:21000", ("admin", "admin"))

   # Define schemas
    schema_source = StructType([
        StructField("Name", StringType(), True),
        StructField("Age", IntegerType(), True)
    ])
    schema_target = StructType([
        StructField("Name", StringType(), True),
        StructField("Age", StringType(), True)
    ])
    show_schema(schema_source, "schema_source")
    show_schema(schema_target, "schema_target")

    # Define Atlas schema fields
    source_fields = [{"name": field.name, "type": field.dataType.simpleString()} for field in schema_source.fields]
    target_fields = [{"name": field.name, "type": field.dataType.simpleString()} for field in schema_target.fields]

    # Register schemas in Apache Atlas
    create_schema_entities_in_atlas(atlas_client, "source_schema", source_fields, "default.source_schema@hive")
    create_schema_entities_in_atlas(atlas_client, "target_schema", target_fields, "default.target_schema@hive")

    # Retrieve and print entities from Apache Atlas
    get_schema_source = get_entities_from_atlas(atlas_client, "source_schema", "default.source_schema@hive")
    get_schema_target = get_entities_from_atlas(atlas_client, "target_schema", "default.target_schema@hive")

    show_schema(get_schema_source, "get_schema_source")
    show_schema(get_schema_target, "get_schema_target")

if __name__ == "__main__":
    main()
