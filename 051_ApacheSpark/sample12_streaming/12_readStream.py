import sys
import six
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import from_json, col, window, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType

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

    # Perform windowed aggregation
    windowedCounts = df \
        .groupBy(
            window(col("time"), "20 seconds"),
            col("key")
        ) \
        .count()

    # Start running the query that prints the running counts to the console
    query = windowedCounts.writeStream \
        .format("console") \
        .outputMode("update") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()
