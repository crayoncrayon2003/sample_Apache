import os
import configparser
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import random

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"), encoding='utf-8')
HOST = config_ini['DEFAULT']['HOST_IP']
PORT = 8081

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        ###############################################################################################
        # RX HTTP request data
        parsed_path = urlparse(self.path)
        print(parsed_path.path)
        print(parse_qs(parsed_path.query))
        print(self.headers)

        ###############################################################################################
        # TX HTTP response data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        value1 = random.randint(50, 100)
        value2 = random.randint(50, 100)
        value3 = random.randint(50, 100)

        body = {
            "data": {
                "records": [
                    { "key1": None,   "key2": value1, "key3": str(value1) },
                    { "key1": value2, "key2": value2, "key3": str(value2) },
                    { "key1": value3, "key2": value3, "key3": None        }
                ],
                "fields": [
                    { "id": "key1", "type": "int"     },
                    { "id": "key2", "type": "numeric" },
                    { "id": "key3", "type": "text"    }
                ]
            }
        }
        print(json.dumps(body, indent=2))
        self.wfile.write( json.dumps(body).encode('utf-8') )


if __name__ == "__main__":
    print("Start the Source server.")
    print("Keep it running and proceed to the next step.")
    
    server = HTTPServer((HOST, PORT), HTTPHandler)
    server.serve_forever()