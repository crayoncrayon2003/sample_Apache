import os
import pyarrow.csv as pcsv
from pyspark.sql import SparkSession
import ibis

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load SQL query from file
def load_sql_query(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Load CSV file
def load_csv(spark):
    file_path = os.path.join(ROOT, 'data.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
    # Read CSV into Spark DataFrame
    df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(file_path)
    return df

def main():
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Ibis with PySpark Integration") \
        .getOrCreate()

    # Load CSV data into a Spark DataFrame
    spark_df = load_csv(spark)
    if spark_df is None:
        return

    # Convert Spark DataFrame to Pandas DataFrame (needed for Ibis)
    pandas_df = spark_df.toPandas()

    # Initialize Ibis with Pandas backend
    ibis_table = ibis.memtable(pandas_df)

    # Query data using Ibis
    filtered_expr = ibis_table.filter(ibis_table["key1"] == 2)
    result = filtered_expr.execute()
    print("Queried Data (Key1 = 2):")
    print(result)

    # Register Spark DataFrame as a temporary SQL view
    spark_df.createOrReplaceTempView("recode")

    # Execute raw SQL query with PySpark
    sql_path = os.path.join(ROOT, "query.sql")
    sql_query = load_sql_query(sql_path)
    queried_df = spark.sql(sql_query)
    print("Queried Data from SQL file:")
    queried_df.show()

    # Stop Spark session
    spark.stop()

if __name__ == '__main__':
    main()
