import os
import pandas as pd
import avro.schema
import avro.datafile
import avro.io
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, "sample2")
FILE = os.path.join(DIR, 'sample2.avro')

def main():
    # make dir
    os.makedirs(DIR, exist_ok=True)

    # create pandas dataframe
    columns = ['year', 'month', 'day', 'value']
    df_save = pd.DataFrame(columns=columns)
    for year in range(2022, 2024):
        for month in range(1, 11):
            for day in range(1, 15):
                df_work = pd.DataFrame([[year, month, day, random.randint(0, 100)]], columns=columns)
                df_save = pd.concat([df_save, df_work])

    print("this is save dataframe")
    print(df_save, "\n")

    # define Avro schema
    schema_str = """
    {
        "type": "record",
        "name": "DataFrame",
        "fields": [
            {"name": "year", "type": "int"},
            {"name": "month", "type": "int"},
            {"name": "day", "type": "int"},
            {"name": "value", "type": "int"}
        ]
    }
    """
    schema = avro.schema.parse(schema_str)

    # save dataframe to Avro
    avro_file = os.path.join(DIR, 'data.avro')
    with open(avro_file, 'wb') as f:
        writer = avro.datafile.DataFileWriter(f, avro.io.DatumWriter(), schema)
        for _, row in df_save.iterrows():
            writer.append(row.to_dict())
        writer.close()

    # Load Avro
    with open(avro_file, 'rb') as f:
        reader = avro.datafile.DataFileReader(f, avro.io.DatumReader())
        rows = [record for record in reader]
        reader.close()

    # create pandas dataframe from loaded data
    df_load = pd.DataFrame(rows)
    print("this is load dataframe")
    print(df_load, "\n")

if __name__ == '__main__':
    main()