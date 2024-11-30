from pyhive import hive
import pandas as pd


def main():
    # Connection Hive
    conn = hive.Connection(host="localhost", port=10000, username="hive", database="default")
    cursor = conn.cursor()

    # CREATE TABLE
    query = "CREATE TABLE IF NOT EXISTS sample_table (key INT, name STRING, age INT)"
    cursor.execute(query)

    # SELECT DATE
    query = "SELECT * FROM sample_table"
    df = pd.read_sql(query, conn)
    print(df)

    # close connection
    conn.close()

if __name__ == "__main__":
    main()


