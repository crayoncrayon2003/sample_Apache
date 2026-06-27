import os
import pyarrow.csv as pcsv
import ibis

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load CSV file into PyArrow Table
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

    # PostgreSQL connection via Ibis (matches docker-compose.yaml)
    conn = ibis.postgres.connect(
        host="localhost",   # PostgreSQL host
        port=5432,          # PostgreSQL port
        user="ibis",        # PostgreSQL user
        password="ibis",    # PostgreSQL pass
        database="ibis",    # PostgreSQL database
    )

    # Load the CSV data into a PostgreSQL table (re-created on each run)
    table_name = "recode"
    conn.create_table(table_name, ibis.memtable(table), overwrite=True)

    # Query data using Ibis expressions
    pg_table = conn.table(table_name)
    expr = pg_table.filter(pg_table.key1 == 2)
    result = expr.execute()
    print("Queried Data (Key1 = 2):\n", result)

    conn.disconnect()

if __name__ == '__main__':
    main()
