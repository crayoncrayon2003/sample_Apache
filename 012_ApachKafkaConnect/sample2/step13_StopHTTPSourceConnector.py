import os
import configparser
import requests

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding='utf-8')

KAFKA_CONNECT = 'http://{}:{}/connectors'.format(config_ini['DEFAULT']['HOST_IP'], '8083')

def main():
    connector_name = "custom-source-connector"

    # Delete Connector
    response = requests.delete(
        "{}/{}".format(KAFKA_CONNECT, connector_name),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 204:
        print("Connector is stop")
    elif response.status_code == 404:
        print("Connector is not found.")
    else:
        print("error:", response.status_code, response.text)

if __name__ == "__main__":
    main()