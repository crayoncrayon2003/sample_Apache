import os
import pyarrow.csv as pcsv
import duckdb

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load query
def load_sql_query(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Load CSV file
def load_csv():
    file_path = os.path.join(ROOT, 'data.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
    table = pcsv.read_csv(file_path)
    return table

def main():
    table = load_csv()
    if table is None:
        return

    # Establish DuckDB connection
    conn = duckdb.connect()

    # Register Arrow Table to DuckDB
    conn.register("arrow_table", table)

    # Execute SQL query directly in DuckDB
    result = conn.execute("SELECT * FROM arrow_table WHERE key1 = 2").fetch_arrow_table()
    print("Queried Data (Key1 = 2):\n", result)

    # Load and execute SQL from file
    sql_path = os.path.join(ROOT, "query_duck.sql")
    sql_query = load_sql_query(sql_path)
    result = conn.execute(sql_query).df()
    print("Queried Data from SQL file:\n", result)

    conn.close()

if __name__ == '__main__':
    main()
