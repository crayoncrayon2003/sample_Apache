import couchdb
import random
import datetime
from time import sleep

USER = "admin"
PASSWORD = "password"
DBNAME = "testdb"


def main():
    # Connect to the CouchDB server
    server = couchdb.Server(f"http://{USER}:{PASSWORD}@localhost:5984/")

    # Create database (if not exists)
    if DBNAME in server:
        db = server[DBNAME]
    else:
        db = server.create(DBNAME)

    # Insert data
    temperature = 10
    humidity = 10
    battery = 10
    dt = datetime.datetime.now() + datetime.timedelta(days=-2)

    try:
        for i in range(10):
            for item in ["device1", "device2", "device3"]:
                doc = {
                    "device": item,
                    "temperature": temperature,
                    "humidity": humidity,
                    "battery": battery,
                    "updateday": dt.isoformat(),
                }
                db.save(doc)

                print(f"device: {item}, temperature: {temperature}, humidity: {humidity}, battery: {battery}, time: {dt}")

                temperature += random.randint(-3, 3)
                humidity += random.randint(-3, 3)
                battery += random.randint(-3, 3)
                dt = dt + datetime.timedelta(milliseconds=5)

            dt = dt + datetime.timedelta(milliseconds=30)
            sleep(3)
    except Exception as e:
        print(f"データ登録失敗: {e}")
    finally:
        # Retrieve and print data
        for doc_id in db:
            print(db[doc_id])


if __name__ == '__main__':
    main()
