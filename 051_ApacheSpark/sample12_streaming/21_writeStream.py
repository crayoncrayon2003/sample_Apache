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
import pyspark
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
    .setAppName("KafkaProducer") \
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

def main():
    # Use the built-in "rate" source to get a true streaming DataFrame (one row
    # per second). writeStream requires a streaming source; calling it on a
    # static createDataFrame(...) raises WRITE_STREAM_NOT_ALLOWED on Spark 4.x.
    df = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 1) \
        .load()

    # Convert to Kafka key/value. value % 11 keeps it in the original 0-10 range.
    # Format "time" as "yyyy-MM-dd HH:mm:ss" (no milliseconds) to match 02_producer
    # and what 11/12/13 parse; a raw CAST(timestamp AS STRING) adds ".SSS" and
    # trips Spark 4's strict (ANSI) to_timestamp with CANNOT_PARSE_TIMESTAMP.
    kafka_df = df.selectExpr(
        "CAST(1 AS STRING) AS key",
        "to_json(struct(CAST(value % 11 AS INT) AS value, date_format(timestamp, 'yyyy-MM-dd HH:mm:ss') AS time)) AS value",
    )

    # Write stream to Kafka
    query = kafka_df \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", TOPIC_NAME) \
        .option("checkpointLocation", DIR_CHECKPOINT) \
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

