import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR  = os.path.join(ROOT,"sample1")
FILE = os.path.join(DIR,'sample1.parquet')

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

    # create table from pandas dataframe
    table_save = pa.Table.from_pandas(df_save)
    print("this is save table")
    print(table_save,"\n")
    print("")

    # save parquet
    pq.write_table(table_save, FILE)

    # Load parquet
    table_load = pq.read_table(FILE, columns=['one', 'two', 'three'])
    print("this is load table")
    print(table_load,"\n")
    print("")

    # create pandas dataframe from table
    df_load = table_load.to_pandas()
    print("this is load dataframe")
    print(df_load,"\n")
    print("")

if __name__ == '__main__':
    main()