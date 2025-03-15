import os
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.json as pjson
import pyarrow.parquet as pq
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))

# Create Arrow Table
def create_arrow_table():
    data = {
        "id": pa.array([1, 2, 3, 4, 5]),
        "name": pa.array(["Alice", "Bob", "Charlie", "David", "Eve"]),
        "age": pa.array([25, 30, 35, 40, 45])
    }
    return pa.table(data)

# Save as JSON
def save_json(table):
    file_path = os.path.join(ROOT, "data.json")
    # Convert Arrow Table to Pandas DataFrame
    df = table.to_pandas()
    # Save as JSON using Pandas
    df.to_json(file_path, orient="records", lines=True)
    print(f"JSON file saved: {file_path}")

# Load JSON file
def load_json():
    file_path = os.path.join(ROOT, 'data.json')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    table = pjson.read_json(file_path)
    print("JSON Data:\n", table)

# Save as CSV
def save_csv(table):
    file_path = os.path.join(ROOT, "data.csv")
    pcsv.write_csv(table, file_path)
    print(f"CSV file saved: {file_path}")

# Load CSV file
def load_csv():
    file_path = os.path.join(ROOT, 'data.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    table = pcsv.read_csv(file_path)
    print("CSV Data:\n", table)

# Save as XLS
def save_xls(table):
    file_path = os.path.join(ROOT, "data.xls")
    df = table.to_pandas()
    df.to_excel(file_path, index=False, engine="openpyxl")
    print(f"XLS file saved: {file_path}")

# Load XLS file
def load_xls():
    file_path = os.path.join(ROOT, 'data.xls')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    df = pd.read_excel(file_path, engine="openpyxl")
    table = pa.Table.from_pandas(df)
    print("XLS Data:\n", table)

# Save as XLSX
def save_xlsx(table):
    file_path = os.path.join(ROOT, "data.xlsx")
    df = table.to_pandas()
    df.to_excel(file_path, index=False, engine="openpyxl")
    print(f"XLSX file saved: {file_path}")

# Load XLSX file
def load_xlsx():
    file_path = os.path.join(ROOT, 'data.xlsx')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    df = pd.read_excel(file_path, engine="openpyxl")
    table = pa.Table.from_pandas(df)
    print("XLSX Data:\n", table)

# Save as Parquet
def save_parquet(table):
    file_path = os.path.join(ROOT, "data.parquet")
    pq.write_table(table, file_path)
    print(f"Parquet file saved: {file_path}")

# Load Parquet file
def load_parquet():
    file_path = os.path.join(ROOT, 'data.parquet')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    table = pq.read_table(file_path)
    print("Parquet Data:\n", table)

# Save as Avro
def save_avro(table):
    file_path = os.path.join(ROOT, "data.avro")
    with pa.OSFile(file_path, 'wb') as f:
        writer = pa.ipc.new_file(f, table.schema)
        writer.write(table)
        writer.close()
    print(f"Avro file saved: {file_path}")

# Load Avro file
def load_avro():
    file_path = os.path.join(ROOT, 'data.avro')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with pa.OSFile(file_path, 'rb') as f:
        reader = pa.ipc.open_file(f)
        table = reader.read_all()
    print("Avro Data:\n", table)


def test_save():
    # Test saving data
    table = create_arrow_table()
    print("Arrow Table:\n", table)

    save_json(table)
    save_csv(table)
    save_xls(table)
    save_xlsx(table)
    save_parquet(table)
    save_avro(table)

def test_load():
    # Test loading data
    load_json()
    load_csv()
    load_xls()
    load_xlsx()
    load_parquet()
    load_avro()

def main():
    test_save()
    test_load()

if __name__ == '__main__':
    main()
