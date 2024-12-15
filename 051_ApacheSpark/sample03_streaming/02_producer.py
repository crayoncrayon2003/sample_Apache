import sys
import six
import random
from datetime import datetime
import time
# Compatibility with python3.12
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka import KafkaProducer

# kafka setting
TOPIC_NAME = "text_topic"
PARTITIONS = 1
REPLICATION = 3

def main():
    # Create Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        client_id='message_sender'
    )

    while True:
        # make topic
        message = {
            "value": random.randint(0, 10),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        value = str(message).encode('utf-8')
        key = str(1).encode('utf-8')

        # send topic
        producer.send(TOPIC_NAME, key=key, value=value)
        producer.flush()
        print(f"Sent message to {TOPIC_NAME}: key={key}, value={value}")
        time.sleep(4)

if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    print('\033[31m{0}\033[0m'.format("Keep it running and proceed to the next step."))
    main()

