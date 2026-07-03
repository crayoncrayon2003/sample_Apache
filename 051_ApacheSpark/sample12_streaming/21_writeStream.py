import os
import shutil
import sys
import six
import random
from datetime import datetime
import time
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import col, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


# create workdir
DIR_ROOT   = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUT = os.path.join(DIR_ROOT,"writeStream_output")
DIR_CHECKPOINT = os.path.join(DIR_ROOT,"writeStream_checkpoint")
if os.path.exists(DIR_OUTPUT):      shutil.rmtree(DIR_OUTPUT)
if os.path.exists(DIR_CHECKPOINT):  shutil.rmtree(DIR_CHECKPOINT)
os.makedirs(DIR_OUTPUT,exist_ok=True)
os.makedirs(DIR_CHECKPOINT,exist_ok=True)

# kafka setting
TOPIC_NAME = "text_topic"
PARTITIONS = 1
REPLICATION = 3

# Spark configuration
conf = SparkConf() \
    .setAppName("KafkaProducer") \
    .setMaster('local') \
    .set("spark.local.ip", "localhost") \
    .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
    .set("spark.pyspark.python", "/usr/bin/python3.12") \
    .set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,org.apache.kafka:kafka-clients:2.3.0") \
    .set("spark.sql.adaptive.enabled", "false") \
    .set("spark.executor.memory", "2g") \
    .set("spark.driver.memory", "2g") \
    .set("spark.executor.cores", "4")

# conf = SparkConf() \
#     .setAppName("KafkaProducer") \
#     .setMaster('local') \
#     .setMaster("spark://localhost:7077") \
#     .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
#     .set("spark.pyspark.python", "/usr/bin/python3.12") \
#     .set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,org.apache.kafka:kafka-clients:2.3.0") \
#     .set("spark.sql.adaptive.enabled", "false") \
#     .set("spark.executor.memory", "2g") \
#     .set("spark.driver.memory", "2g") \
#     .set("spark.executor.cores", "4")

spark = SparkSession.builder.config(conf=conf).getOrCreate()

# Set log level to INFO to reduce verbosity
spark.sparkContext.setLogLevel("INFO")

def generate_data():
    return [(1, random.randint(0, 10), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]

def main():
    schema = StructType([
        StructField("key", IntegerType(), True),
        StructField("value", IntegerType(), True),
        StructField("time", StringType(), True)
    ])

    # Create DataFrame from generated data
    df = spark.createDataFrame(generate_data(), schema)

    # Convert DataFrame to Kafka compatible format
    kafka_df = df \
        .selectExpr("CAST(key AS STRING)", "to_json(struct(*)) AS value")

    # Write stream to Kafka
    query = kafka_df \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", TOPIC_NAME) \
        .option("checkpointLocation", DIR_CHECKPOINT) \
        .start()

    query.awaitTermination(60)


if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()

