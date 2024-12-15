import os
import shutil
import sys
import six
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import from_json, col, window, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType

# create workdir
DIR_ROOT   = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUT = os.path.join(DIR_ROOT,"output")
DIR_CHECKPOINT = os.path.join(DIR_ROOT,"checkpoint")
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
    .setAppName("KafkaConsumer") \
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
#     .setAppName("KafkaConsumer") \
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

def main():
    # Define schema for the messages
    schema = StructType([
        StructField("value", StringType()),
        StructField("time", StringType())
    ])

    # Create DataFrame representing the stream of input lines from Kafka
    df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("startingOffsets", "earliest") \
            .option("enable.auto.commit", "true") \
            .option("group.id", "my-group") \
            .option("subscribe", TOPIC_NAME) \
            .load()

    # Extract the fields and cast them to the right types
    df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    # Convert JSON 'value' field to struct and extract the fields
    df = df.withColumn("jsonData", from_json(col("value"), schema)).select("key", "jsonData.*")

    # Convert 'time' field to timestamp
    df = df.withColumn("time", to_timestamp(col("time"), "yyyy-MM-dd HH:mm:ss"))

    # Add watermark to handle late data
    df = df.withWatermark("time", "1 minute")

    # Perform windowed aggregation
    windowedCounts = df \
        .groupBy(
            window(col("time"), "20 seconds"),
            col("key")
        ) \
        .count() \
        .selectExpr("window.start as window_start", "window.end as window_end", "key", "count")

    # Start running the query that prints the running counts to the file
    query = windowedCounts.writeStream \
        .format("csv") \
        .option("path", DIR_OUTPUT) \
        .option("checkpointLocation", DIR_CHECKPOINT) \
        .outputMode("append") \
        .start()

    # setting to stop after 60 seconds
    query.awaitTermination(60)

if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()
