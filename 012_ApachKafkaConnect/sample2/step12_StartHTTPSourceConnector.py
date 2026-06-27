import os
import configparser
import requests

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding='utf-8')

KAFKA_CONNECT = 'http://{}:{}/connectors'.format(config_ini['DEFAULT']['HOST_IP'], '8083')

def main():
    # Setting
    custom_source_config = {
        "name": "custom-source-connector",
        "config": {
            "connector.class": "com.example.CustomSourceConnector",
            "tasks.max": "1",
            "topics": "my-kafka-topic",
            "transforms": "customTransform",
            "transforms.customTransform.type": "com.example.CustomTransform",
            "api.url": "http://{}:8081/".format(config_ini['DEFAULT']['DOCKER_HOST_IP']),
            "poll.interval.ms": "1000"
        }
    }

    # Regist Connector
    response = requests.post(
        KAFKA_CONNECT,
        json=custom_source_config,
        headers={"Connector with the same name already exists."}
    )

    if response.status_code == 201:
        print("Connector is started")
    elif response.status_code == 409:
        print("Connector with the same name already exists.")
    else:
        print("error:", response.status_code, response.text)

if __name__ == "__main__":
    main()