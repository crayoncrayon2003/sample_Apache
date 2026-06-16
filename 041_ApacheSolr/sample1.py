import pysolr
import random
import datetime

CORE = "sensor"
SOLR_URL = f"http://localhost:8983/solr/{CORE}"


def main():
    # Connect to the Solr core
    solr = pysolr.Solr(SOLR_URL, always_commit=True)

    # Insert data
    temperature = 10
    humidity = 10
    battery = 10
    dt = datetime.datetime.now() + datetime.timedelta(days=-2)

    docs = []
    for i in range(10):
        for item in ["device1", "device2", "device3"]:
            doc = {
                "id": f"{item}#{dt.isoformat()}",
                "device": item,
                "temperature": temperature,
                "humidity": humidity,
                "battery": battery,
                "updateday": dt.isoformat() + "Z",
            }
            docs.append(doc)

            print(f"device: {item}, temperature: {temperature}, humidity: {humidity}, battery: {battery}, time: {dt}")

            temperature += random.randint(-3, 3)
            humidity += random.randint(-3, 3)
            battery += random.randint(-3, 3)
            dt = dt + datetime.timedelta(milliseconds=5)
        dt = dt + datetime.timedelta(milliseconds=30)

    try:
        solr.add(docs)
    except Exception as e:
        print(f"データ登録失敗: {e}")

    # Search data
    results = solr.search("device:device1", rows=100)
    print(f"\nhits (device1): {results.hits}")
    for row in results:
        print(row)


if __name__ == '__main__':
    main()
