import sys
import six
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka import KafkaConsumer

# kafka setting
TOPIC_NAME = "text_topic"
PARTITIONS = 1
REPLICATION = 3

def main():
    # Create Kafka KafkaConsumer
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="my-group",
        value_deserializer=lambda x: x.decode('utf-8')
    )

    # Received topic
    for message in consumer:
        print(f"Received message: {message.value}")

if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    print('\033[31m{0}\033[0m'.format(
        "This sample is a KafkaConsumer for testing a KafkaProducer.\n"+
        "Confirm to receive the topic, and does the following.\n"+
        " * stop running KafkaConsumer\n"+
        " * keep running KafkaProducer\n"
    ))
main()
