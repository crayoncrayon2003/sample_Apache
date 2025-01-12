import os
import pandas as pd
import avro.schema
import avro.datafile
import avro.io

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR  = os.path.join(ROOT,"sample1")
FILE = os.path.join(DIR,'sample1.avro')

def main():
    # make dir
    os.makedirs(DIR, exist_ok=True)

    # create pandas dataframe
    df_save = pd.DataFrame({'one': [-1, 2, 2.5],
                       'two': ['foo', 'bar', 'baz'],
                       'three': [True, False, True]},
                      index=list('abc'))
    print("this is save dataframe")
    print(df_save)
    print("")

    # define Avro schema
    schema_str = """
    {
        "type": "record",
        "name": "DataFrame",
        "fields": [
            {"name": "one", "type": "double"},
            {"name": "two", "type": "string"},
            {"name": "three", "type": "boolean"}
        ]
    }
    """
    schema = avro.schema.parse(schema_str)

    # save dataframe to Avro
    with open(FILE, 'wb') as f:
        writer = avro.datafile.DataFileWriter(f, avro.io.DatumWriter(), schema)
        for _, row in df_save.iterrows():
            writer.append(row.to_dict())
        writer.close()

    # Load Avro
    with open(FILE, 'rb') as f:
        reader = avro.datafile.DataFileReader(f, avro.io.DatumReader())
        rows = [record for record in reader]
        reader.close()

    # create pandas dataframe from loaded data
    df_load = pd.DataFrame(rows)
    print("this is load dataframe")
    print(df_load, "\n")
    print("")

if __name__ == '__main__':
    main()