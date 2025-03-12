import os
import configparser
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"), encoding='utf-8')
HOST = config_ini['DEFAULT']['HOST_IP']
PORT = 8082

class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        ###############################################################################################
        # RX HTTP request data
        parsed_path = urlparse(self.path)
        print(parsed_path.path)
        print(parse_qs(parsed_path.query))
        print(self.headers)
        body = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
        print(json.dumps(json.loads(body), indent=2))

        ###############################################################################################
        # TX HTTP response data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

if __name__ == "__main__":
    print("Start the Sink server.")
    print("Keep it running and proceed to the next step.")

    server = HTTPServer((HOST, PORT), HTTPHandler)
    server.serve_forever()