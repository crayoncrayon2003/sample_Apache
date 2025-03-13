import os
import configparser
import requests

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding='utf-8')

KAFKA_CONNECT = 'http://{}:{}/connectors'.format(config_ini['DEFAULT']['HOST_IP'], '8083')

def main():
    # Setting
    custom_sink_config = {
        "name": "custom-sink-connector",
        "config": {
            "connector.class": "com.example.CustomSinkConnector",
            "tasks.max": "1",
            "topics": "my-kafka-topic",
            "api.url": "http://172.28.164.85:8082/",
            "poll.interval.ms":"1000"
        }
    }

    # Regist Connector
    response = requests.post(
        KAFKA_CONNECT,
        json=custom_sink_config,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        print("Connector is started")
    elif response.status_code == 409:
        print("Connector with the same name already exists.")
    else:
        print("error:", response.status_code, response.text)

if __name__ == "__main__":
    main()