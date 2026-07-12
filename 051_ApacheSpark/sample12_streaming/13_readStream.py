import os
import shutil
import sys
import six
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from pyspark.sql import SparkSession
import pyspark
from pyspark import SparkConf
from pyspark.sql.functions import from_json, col, window, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType

# create workdir
DIR_ROOT   = os.path.dirname(os.path.abspath(__file__))
DIR_OUTPUT = os.path.join(DIR_ROOT,"readStream_output")
DIR_CHECKPOINT = os.path.join(DIR_ROOT,"readStream_checkpoint")
if os.path.exists(DIR_OUTPUT):      shutil.rmtree(DIR_OUTPUT)
if os.path.exists(DIR_CHECKPOINT):  shutil.rmtree(DIR_CHECKPOINT)
os.makedirs(DIR_OUTPUT,exist_ok=True)
os.makedirs(DIR_CHECKPOINT,exist_ok=True)

# kafka setting
TOPIC_NAME = "text_topic"
PARTITIONS = 1
REPLICATION = 3

# Match the Kafka connector to the running Spark. Spark 4.x is built on Scala
# 2.13, Spark 3.x on Scala 2.12; mixing them raises NoSuchMethodError. Derive the
# coordinates from pyspark.__version__ so this works on both the 3系 (env358) and
# 4系 (env412) lines.
SPARK_VERSION = pyspark.__version__
SCALA_VERSION = "2.13" if SPARK_VERSION.startswith("4") else "2.12"
KAFKA_PACKAGE = f"org.apache.spark:spark-sql-kafka-0-10_{SCALA_VERSION}:{SPARK_VERSION}"

# Ignore any stale shell SPARK_HOME (e.g. the 3系 install /opt/spark-3-5-8 while
# running under env412) and use the Spark jars bundled with the active pyspark.
# Without this, a 4.x pyspark driving 3.x jars fails at getOrCreate() with
# "'JavaPackage' object is not callable". This makes the script run under
# whichever venv is active — 3系 or 4系 — with no manual SPARK_HOME setup.
os.environ["SPARK_HOME"] = os.path.dirname(pyspark.__file__)

# Spark configuration
conf = SparkConf() \
    .setAppName("KafkaConsumer") \
    .setMaster('local') \
    .set("spark.local.ip", "localhost") \
    .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
    .set("spark.pyspark.python", "/usr/bin/python3.12") \
    .set("spark.jars.packages", KAFKA_PACKAGE) \
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

    # Stop after 60 seconds. awaitTermination(timeout) only returns; stop the
    # query (and context) explicitly and silence the expected teardown-abort
    # logs, so the sample exits cleanly instead of dumping an ERROR stack.
    query.awaitTermination(60)
    spark.sparkContext.setLogLevel("OFF")
    query.stop()
    spark.stop()

if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()
