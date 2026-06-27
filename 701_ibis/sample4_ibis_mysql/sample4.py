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

    # MySQL connection via Ibis (matches docker-compose.yaml)
    conn = ibis.mysql.connect(
        host="localhost",   # MySQL host
        port=3306,          # MySQL port
        user="ibis",        # MySQL user
        password="ibis",    # MySQL pass
        database="ibis",    # MySQL database
    )

    # Load the CSV data into a MySQL table (re-created on each run).
    # Drop-then-create instead of overwrite=True: the ibis MySQL backend's
    # overwrite path emits a RENAME statement that MySQL rejects.
    table_name = "recode"
    conn.drop_table(table_name, force=True)
    conn.create_table(table_name, ibis.memtable(table))

    # Query data using Ibis expressions
    mysql_table = conn.table(table_name)
    filtered_expr = mysql_table.filter(mysql_table.key1 == 2)
    result = filtered_expr.execute()
    print("Queried Data (Key1 = 2):")
    print(result)

    conn.disconnect()

if __name__ == '__main__':
    main()
