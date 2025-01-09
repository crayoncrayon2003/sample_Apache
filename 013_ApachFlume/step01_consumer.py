import os
import configparser

from kafka import KafkaConsumer
from multiprocessing import Process

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"), encoding='utf-8')

SERVERS = '{}:{}'.format(config_ini['DEFAULT']['HOST_IP'],'9092')
#SERVERS = 'localhost:9092'

def test(name):
    consumer = KafkaConsumer('test', bootstrap_servers=[SERVERS])
    for message in consumer:
        print(name,"receive :" , message.value.decode())

def main():
    t1 = Process(target=test, args=("t1",))
    t1.start()

if __name__ == '__main__':
    main()