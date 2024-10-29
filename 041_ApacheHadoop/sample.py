import os
import configparser
from pprint import pprint
from hdfs import InsecureClient

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

CONF = os.path.join(ROOT, "config.ini")
config_ini = configparser.ConfigParser()
config_ini.read(CONF, encoding='utf-8')
NAMENODE = 'http://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'], '9870')
#NAMENODE2 = 'http://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'], '50070')

FILE_NAME  = "TestFile.txt"
PATH_LOCAL = ROOT
PATH_HDFS  = "/user/hadoop/"

def main():
    client = InsecureClient(NAMENODE, user='hadoop')

    print("check dir")
    if not client.status(PATH_HDFS, strict=False):
        print("make dir")
        client.makedirs(PATH_HDFS)

    print("show dir")
    print(client.list(PATH_HDFS))


    print("upload file")
    filepath_local = os.path.join(PATH_LOCAL, FILE_NAME)
    filepath_hdfs  = os.path.join(PATH_HDFS , FILE_NAME)
    client.upload(filepath_hdfs, filepath_local)

    # print("read file")
    # with client.read(filepath_hdfs, encoding='utf-8') as reader:
    #     print(reader.read())


if __name__ == "__main__":
    main()
