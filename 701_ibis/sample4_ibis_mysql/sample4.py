import os
import ibis

ROOT = os.path.dirname(os.path.abspath(__file__))

# Load SQL query from file
def load_sql_query(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("\033[31m{0}\033[0m".format("under development"))

    # MySQL connection via Ibis
    conn = ibis.mysql.connect(
        host="your_localhost",   # MySQL host
        user="your_username",    # MySQL user
        password="your_password",# MySQL pass
        database="your_database" # MySQL database
    )

    table_name = "your_table"
    mysql_table = conn.table(table_name)

    # Query data using Ibis expressions
    filtered_expr = mysql_table.filter(mysql_table.key1 == 2)
    result = filtered_expr.execute()
    print("Queried Data (Key1 = 2):")
    print(result)

    conn.close()

if __name__ == '__main__':
    main()
