import os
import configparser
from kafka import KafkaProducer
import time
import datetime

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"), encoding='utf-8')

SERVERS = '{}:{}'.format(config_ini['DEFAULT']['HOST_IP'],'9092')

def main():
    producer = KafkaProducer(bootstrap_servers=SERVERS)
    while True:
        dt_now = datetime.datetime.now()
        print("send : ",str(dt_now))
        result = producer.send('test', str(dt_now).encode()).get(timeout=10)
        print(result)
        time.sleep(3)

if __name__ == '__main__':
    main()