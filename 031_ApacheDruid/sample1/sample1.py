import requests
import json
import time

DRUID_URL = "http://localhost:8888"
DATASOURCE = "wikipedia_inline"

def ingest_inline_json(records: list[dict]):
    """
    input data
    """
    task = {
        "type": "index",
        "spec": {
            "ioConfig": {
                "type": "index",
                "inputSource": {
                    "type": "inline",
                    "data": "\n".join(json.dumps(rec) for rec in records)
                },
                "inputFormat": {
                    "type": "json"
                }
            },
            "dataSchema": {
                "dataSource": DATASOURCE,
                "timestampSpec": {
                    "column": "timestamp",
                    "format": "iso"
                },
                "dimensionsSpec": {
                    "dimensions": ["channel", "cityName", "comment"]
                },
                "granularitySpec": {
                    "type": "uniform",
                    "segmentGranularity": "DAY",
                    "queryGranularity": "NONE",
                    "rollup": False
                }
            },
            "tuningConfig": {
                "type": "index"
            }
        }
    }

    res = requests.post(f"{DRUID_URL}/druid/indexer/v1/task", json=task)
    if res.status_code != 200:
        raise Exception(f"Ingest failed: {res.status_code} {res.text}")
    task_id = res.json()["task"]
    print(f"✅ Ingest task submitted: {task_id}")
    return task_id


def run_sql(sql: str):
    """
    run sql
    """
    res = requests.post(f"{DRUID_URL}/druid/v2/sql", json={"query": sql})
    if res.status_code != 200:
        raise Exception(f"SQL failed: {res.status_code} {res.text}")
    return res.json()


def main():
    # create sample data
    sample_data = [
        {"timestamp": "2024-01-01T00:00:00Z", "channel": "#en.wikipedia", "cityName": "Tokyo", "comment": "edit A"},
        {"timestamp": "2024-01-02T00:00:00Z", "channel": "#en.wikipedia", "cityName": "Osaka", "comment": "edit B"}
    ]

    # send sample data
    try:
        task_id = ingest_inline_json(sample_data)
    except Exception as e:
        print(f"❌ {e}")
        exit(1)

    print("⏳ Waiting 30s for ingestion to complete...")
    time.sleep(30)

    # exec query
    try:
        result = run_sql(f"SELECT * FROM {DATASOURCE} LIMIT 10")
        print("✅ Query Result:")
        for row in result:
            print(row)
    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
