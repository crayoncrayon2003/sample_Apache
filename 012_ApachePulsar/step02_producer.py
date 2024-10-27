import os
import configparser
from pulsar import Client
import time
import datetime

# Config ini ファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding='utf-8')
SERVERS = 'pulsar://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'], '6650')

def main():
    client = Client(SERVERS)
    producer = client.create_producer('test-topic')

    while True:
        dt_now = datetime.datetime.now()
        print("send : ", str(dt_now))
        producer.send(str(dt_now).encode('utf-8'))
        time.sleep(3)

    client.close()

if __name__ == '__main__':
    main()