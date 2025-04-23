import apache_beam as beam
import requests
import json

# REST API GET
def get_api(url):
    print("this is get")
    response = requests.get(url)
    # throw exception if the response is not 200
    response.raise_for_status()
    return response.json()

# Transform 1
def transform1(data):
    print("this is transform1")
    print(json.dumps(data, indent=2))

    if "name" not in data or "temperature" not in data or "humidity" not in data:
        raise ValueError("Missing required data in input")

    transformed_data = {
        "id": "endpoint2",
        "type": "sampletype",
        "name": {
            "value": data["name"],
            "type": "TEXT"
        },
        "temp": {
            "value": str(data["temperature"]),
            "type": "Integer"
        },
        "humi": {
            "value": str(data["humidity"]),
            "type": "Integer"
        }
    }

    return transformed_data

def transform2(data):
    print("this is transform2")
    print(json.dumps(data, indent=2))

    if "temp" not in data or "humi" not in data:
        raise ValueError("Missing required data in input")

    transformed_data = {
        "name": "endpoint1",
        "temperature": str(data["temp"]["value"]),
        "humidity": str(data["humi"]["value"])
    }

    return transformed_data

# REST API POST
def post_api(data, url):
    print("this is post")
    print(json.dumps(data, indent=2))
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

# Apache Beam pipeline for data flow
def run1(input_url, output_url, pipeline_options=None):
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | 'Step 0: Get API Data' >> beam.Create([input_url])
            | 'Step 1: Get data from endpoint1' >> beam.Map(get_api)
            | 'Step 2: Transform data to Item2 format' >> beam.Map(transform1)
            | 'Step 3: POST transformed data to endpoint2' >> beam.Map(lambda data: post_api(data, output_url))
        )

def run2(input_url, output_url, pipeline_options=None):
    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | 'Step 0: Get API Data' >> beam.Create([input_url])
            | 'Step 1: Get data from endpoint1' >> beam.Map(get_api)
            | 'Step 2: Transform data to Item2 format' >> beam.Map(transform2)
            | 'Step 3: POST transformed data to endpoint2' >> beam.Map(lambda data: post_api(data, output_url))
        )


def main():
    endpoint1 = "http://127.0.0.1:5050/endpoint1"
    endpoint2 = "http://127.0.0.1:5050/endpoint2"

    print(" -- Pipeline 1 --")
    run1(endpoint1, endpoint2, None)

    print(" -- Pipeline 2 --")
    run2(endpoint2, endpoint1, None)

if __name__ == "__main__":
    main()
