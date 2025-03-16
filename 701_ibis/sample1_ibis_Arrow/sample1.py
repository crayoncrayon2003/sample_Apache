import os
import pyarrow.csv as pcsv
import ibis

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load SQL query
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

    # Connect to DuckDB via ibis
    conn = ibis.duckdb.connect()

    # Convert the PyArrow Table into an ibis MemTable
    arrow_memtable = ibis.memtable(table)

    # Register the MemTable with a name for SQL queries
    conn.create_table("recode", arrow_memtable)

    # Run a query directly on the MemTable
    expr = arrow_memtable.filter(arrow_memtable.key1 == 2)
    result = expr.execute()
    print("Queried Data (Key1 = 2):\n", result)

    # Load and execute SQL from a file
    sql_path = os.path.join(ROOT, "query.sql")
    sql_query = load_sql_query(sql_path)
    result_from_file = conn.sql(sql_query).execute()

    print("Queried Data from SQL file:\n", result_from_file)

if __name__ == '__main__':
    main()