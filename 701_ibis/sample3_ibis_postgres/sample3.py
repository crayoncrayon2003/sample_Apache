import os
import pyarrow.csv as pcsv
import ibis

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load SQL query
def load_sql_query(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Load CSV file into PyArrow Table
def load_csv():
    file_path = os.path.join(ROOT, 'data.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
    table = pcsv.read_csv(file_path)
    return table

def main():
    print("\033[31m{0}\033[0m".format("under development"))

    table = load_csv()
    if table is None:
        return

    # PostgreSQL connection via Ibis
    conn = ibis.postgres.connect(
        host="your_localhost",     # PostgreSQL host
        port=5432,                 # PostgreSQL port
        user="your_username",      # PostgreSQL user
        password="your_password",  # PostgreSQL pass
        database="your_database"   # PostgreSQL database
    )

    table_name = "your_table"
    pg_table = conn.table(table_name)

    # Query data using Ibis expressions
    expr = pg_table.filter(pg_table.key1 == 2)
    result = expr.execute()
    print("Queried Data (Key1 = 2):\n", result)

    conn.close()

if __name__ == '__main__':
    main()
