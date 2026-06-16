from SPARQLWrapper import SPARQLWrapper, JSON, POST
import random
import datetime

DATASET = "ds"
BASE = f"http://localhost:3030/{DATASET}"
UPDATE_URL = f"{BASE}/update"
QUERY_URL = f"{BASE}/query"

EX = "http://example.org/sensor#"


def update(sparql_update: str):
    sparql = SPARQLWrapper(UPDATE_URL)
    sparql.setMethod(POST)
    # Fuseki default admin credentials
    sparql.setCredentials("admin", "password")
    sparql.setQuery(sparql_update)
    sparql.query()


def main():
    # Insert data as RDF triples
    temperature = 10
    humidity = 10
    battery = 10
    dt = datetime.datetime.now() + datetime.timedelta(days=-2)

    triples = []
    for i in range(10):
        for item in ["device1", "device2", "device3"]:
            s = f"<{EX}{item}-{i}>"
            triples.append(
                f'{s} <{EX}device> "{item}" ; '
                f'<{EX}temperature> {temperature} ; '
                f'<{EX}humidity> {humidity} ; '
                f'<{EX}battery> {battery} ; '
                f'<{EX}updateday> "{dt.isoformat()}" .'
            )

            print(f"device: {item}, temperature: {temperature}, humidity: {humidity}, battery: {battery}, time: {dt}")

            temperature += random.randint(-3, 3)
            humidity += random.randint(-3, 3)
            battery += random.randint(-3, 3)
            dt = dt + datetime.timedelta(milliseconds=5)
        dt = dt + datetime.timedelta(milliseconds=30)

    try:
        update("INSERT DATA { " + " ".join(triples) + " }")
    except Exception as e:
        print(f"データ登録失敗: {e}")

    # Query data with SPARQL
    sparql = SPARQLWrapper(QUERY_URL)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(
        f"""
        PREFIX ex: <{EX}>
        SELECT ?s ?temperature ?updateday
        WHERE {{ ?s ex:device "device1" ; ex:temperature ?temperature ; ex:updateday ?updateday . }}
        """
    )
    results = sparql.query().convert()
    print("\nQuery Result (device1):")
    for row in results["results"]["bindings"]:
        print(row)


if __name__ == '__main__':
    main()
