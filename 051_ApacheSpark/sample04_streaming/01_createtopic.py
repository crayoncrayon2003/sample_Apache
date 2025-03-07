import sys
import six
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka.admin import NewTopic, KafkaAdminClient

# kafka setting
TOPIC_NAME = "text_topic"
PARTITIONS = 1
REPLICATION = 3

def main():
    # Create Kafka AdminClient
    admin_client = KafkaAdminClient(
        bootstrap_servers="localhost:9092",
        client_id='topic_creator'
    )

    # Create NewTopic to Kafka
    topic_list = [NewTopic(name=TOPIC_NAME, num_partitions=PARTITIONS, replication_factor=REPLICATION)]
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print("Success to create topic")
    except Exception as e:
        print(f"Failed to create topic: {e}")


if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()
