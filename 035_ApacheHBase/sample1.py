import happybase
import random
import datetime
from time import sleep

TABLE = b"sensor"


def main():
    # Connect to HBase via the Thrift API
    connection = happybase.Connection("localhost", port=9090)

    # Create table (if not exists)
    if TABLE not in connection.tables():
        connection.create_table(
            "sensor",
            {"data": dict()},  # single column family "data"
        )

    table = connection.table("sensor")

    # Insert data
    temperature = 10
    humidity = 10
    battery = 10
    dt = datetime.datetime.now() + datetime.timedelta(days=-2)

    try:
        for i in range(10):
            for item in ["device1", "device2", "device3"]:
                row_key = f"{item}#{dt.isoformat()}".encode()
                table.put(
                    row_key,
                    {
                        b"data:device": item.encode(),
                        b"data:temperature": str(temperature).encode(),
                        b"data:humidity": str(humidity).encode(),
                        b"data:battery": str(battery).encode(),
                        b"data:updateday": dt.isoformat().encode(),
                    },
                )

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
        for key, data in table.scan():
            print(key, data)

        connection.close()


if __name__ == '__main__':
    main()
