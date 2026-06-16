from pinotdb import connect


def main():
    # Connect to the Pinot broker
    conn = connect(host="localhost", port=8000, path="/query/sql", scheme="http")

    cursor = conn.cursor()

    # The QuickStart (-type batch) ships with the "baseballStats" table
    cursor.execute(
        """
        SELECT playerName, sum(runs) AS total_runs
        FROM baseballStats
        GROUP BY playerName
        ORDER BY total_runs DESC
        LIMIT 10
        """
    )

    for row in cursor:
        print(row)

    conn.close()


if __name__ == '__main__':
    main()
