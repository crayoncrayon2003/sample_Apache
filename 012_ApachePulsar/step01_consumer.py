import os
import configparser
from pulsar import Client, ConsumerType
from multiprocessing import Process

# Config ini ファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding='utf-8')
SERVERS = 'pulsar://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'], '6650')

def test(name):
    client = Client(SERVERS)
    consumer = client.subscribe('test-topic', subscription_name='my-subscription', consumer_type=ConsumerType.Shared)

    while True:
        msg = consumer.receive()
        try:
            print(name, "received: ", msg.data().decode())
            consumer.acknowledge(msg)
        except:
            consumer.negative_acknowledge(msg)

    client.close()

def main():
    t1 = Process(target=test, args=("t1",))
    t1.start()

if __name__ == '__main__':
    main()