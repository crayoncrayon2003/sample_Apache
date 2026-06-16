from pyflink.table import EnvironmentSettings, TableEnvironment

# Statistics over a (bounded) stream using Flink's Table API: count, average and
# population standard deviation per device. This mirrors the kind of streaming
# statistics Flink ML / Flink SQL is used for.


def main():
    env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

    env.execute_sql("""
        CREATE TABLE sensor (
            device      STRING,
            temperature INT,
            humidity    INT
        ) WITH (
            'connector' = 'datagen',
            'number-of-rows' = '30',
            'fields.device.length' = '4',
            'fields.temperature.min' = '5',
            'fields.temperature.max' = '20',
            'fields.humidity.min' = '0',
            'fields.humidity.max' = '25'
        )
    """)

    result = env.sql_query("""
        SELECT
            device,
            COUNT(*)            AS n,
            AVG(temperature)    AS avg_temp,
            STDDEV_POP(temperature) AS stddev_temp
        FROM sensor
        GROUP BY device
    """)

    result.execute().print()


if __name__ == '__main__':
    main()
