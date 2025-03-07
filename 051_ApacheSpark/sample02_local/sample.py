import os
import json
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

# load query
def load_sql_query(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# save schema/data
def save_spark_df(df, folder_path):
    os.makedirs(folder_path, exist_ok=True)

    # save schema
    schema_json_path = os.path.join(folder_path, "schema.json")
    with open(schema_json_path, "w") as f:
        f.write(df.schema.json())

    # save data
    data_path = os.path.join(folder_path, "data.parquet")
    df.write.mode("overwrite").parquet(data_path)

# load schema/data
def load_spark_df(spark, folder_path):
    schema_json_path = os.path.join(folder_path, "schema.json")
    data_path = os.path.join(folder_path, "data.parquet")

    # load schema
    with open(schema_json_path, "r") as f:
        schema_json = f.read()
    schema = StructType.fromJson(json.loads(schema_json))

    # load data
    return spark.read.schema(schema).parquet(data_path)


# get fields/records for data.json 
def extract_fields_and_records_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        fields = data["data"]["fields"]
        records = data["data"]["records"]
        return [fields, records]

# data mapping
type_mapping = {
    "int": IntegerType(),
    "numeric": FloatType(),
    "text": StringType()
}

# create schema from fields
def create_schema(fields):
    return StructType([
        StructField(field["id"], type_mapping.get(field["type"], StringType()), True)
        for field in fields
    ])

# create data from recode
def create_records(records, schema):
    def cast_value(value, data_type):
        if value is None:
            return None
        elif isinstance(data_type, IntegerType):
            return int(value)
        elif isinstance(data_type, FloatType):
            return float(value)
        elif isinstance(data_type, StringType):
            return str(value)
        return value

    casted_records = []
    for record in records:
        casted_record = {}
        for field in schema.fields:
            field_name = field.name
            field_type = field.dataType
            casted_record[field_name] = cast_value(record.get(field_name), field_type)
        casted_records.append(casted_record)
    return casted_records

# convert data
def convert(df, file_path_sql, query):
    sql_query = load_sql_query(file_path_sql)

    df.createOrReplaceTempView(query)
    transformed_df = spark.sql(sql_query)
    
    return transformed_df

def clean_json_values(data):
    if isinstance(data, dict):
        return {
            k: clean_json_values(v) if k != "value" else v.replace('\\"', '"') if isinstance(v, str) else v
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [clean_json_values(item) for item in data]
    else:
        return data

if __name__ == "__main__":
    # ###########################
    # setting spark
    os.environ["PYSPARK_PYTHON"] = "python3"
    os.environ["PYSPARK_DRIVER_PYTHON"] = "python3"
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"

    conf = SparkConf() \
            .setAppName("SchemaTransformationExample") \
            .set("spark.local.ip", "localhost") \
            .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
            .set("spark.pyspark.python", "/usr/bin/python3.12") \
            .set("spark.executor.memory", "2g") \
            .set("spark.driver.memory", "2g") \
            .set("spark.executor.cores", "4")
    
    spark = SparkSession \
        .builder \
        .config(conf=conf) \
        .getOrCreate()

    # ###########################
    # base dir
    directory = os.path.dirname(os.path.abspath(__file__))

    # ###########################
    # convert csv
    # load CSV
    file_path = os.path.join(directory, "data.csv")
    
    # create spark df
    spark_df = spark.read.option("header", "true").csv(file_path)

    # optional
    save_path = os.path.join(directory, "save_csv")
    save_spark_df(spark_df, save_path)               # save schema/data
    spark_df = load_spark_df(spark, save_path)       # load schema/data

    # convert
    file_path_sql = os.path.join(directory, "query.sql")
    cnv_df = convert(spark_df, file_path_sql, "recode")
    cnv_data = cnv_df.toJSON().collect()

    # save json
    cnv_data_parsed = [clean_json_values(json.loads(record)) for record in cnv_data]
    output = os.path.join(directory, "output_csv.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(cnv_data_parsed, f, ensure_ascii=False, indent=4)

    # ###########################
    # convert json
    # load CSV
    file_path = os.path.join(directory, "data.json")
    [fields, records] = extract_fields_and_records_from_json(file_path)

    schema = create_schema(fields)
    records = create_records(records, schema)

    # create spark df
    spark_df = spark.createDataFrame(records, schema)

    # optional
    save_path = os.path.join(directory, "save_json")
    save_spark_df(spark_df, save_path)               # save schema/data
    spark_df = load_spark_df(spark, save_path)       # load schema/data

    # convert
    file_path_sql = os.path.join(directory, "query.sql")
    cnv_df = convert(spark_df, file_path_sql, "recode")
    cnv_data = cnv_df.toJSON().collect()

    # save json
    cnv_data_parsed = [clean_json_values(json.loads(record)) for record in cnv_data]
    output = os.path.join(directory, "output_json.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(cnv_data_parsed, f, ensure_ascii=False, indent=4)


    spark.stop()