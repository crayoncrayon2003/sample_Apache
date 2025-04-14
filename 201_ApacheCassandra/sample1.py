from cassandra.cluster import Cluster
from time import sleep
import random
import datetime

def main():
    # Connect to the Cassandra cluster
    cluster = Cluster(["localhost"])
    session = cluster.connect()

    # Create keyspace (if not exists)
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS testdb
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)

    # Connect to the keyspace
    session.set_keyspace("testdb")

    # Create table (if not exists)
    session.execute("""
        CREATE TABLE IF NOT EXISTS test_collection (
            device TEXT,
            temperature INT,
            humidity INT,
            battery INT,
            updateday TIMESTAMP,
            PRIMARY KEY (device, updateday)
        );
    """)

    # Insert data
    temperature = 10
    humidity = 10
    battery  = 10
    dt = datetime.datetime.now() + datetime.timedelta(days=-2)

    try:
        for i in range(10):
            for item in ['device1', 'device2', 'device3']:
                session.execute("""
                    INSERT INTO test_collection (device, temperature, humidity, battery, updateday) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (item, temperature, humidity, battery, dt))

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
        rows = session.execute("SELECT * FROM test_collection")
        for row in rows:
            print(row)

        cluster.shutdown()


if __name__ == '__main__':
    main()
