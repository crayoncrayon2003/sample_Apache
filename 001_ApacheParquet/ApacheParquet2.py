import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import random
import numpy.random

ROOT = os.path.dirname(os.path.abspath(__file__))
DIR  = os.path.join(ROOT,"sample2")

def main():
    # make dir
    os.makedirs(DIR, exist_ok=True)

    # create pandas dataframe
    columns = ['year', 'month', 'day', 'value']
    df_save = pd.DataFrame(columns = columns)
    for year in range(2022,2024):
        for month in range(1,11):
            for day in range(1,15):
                df_work = pd.DataFrame([[year, month, day, random.randint(0,100)]],columns = columns)
                df_save = pd.concat([df_save, df_work])
    print(df_save)

    # create table from pandas dataframe
    table_save = pa.Table.from_pandas(df_save)
    # save parquet
    pq.write_to_dataset(
        table_save,
        root_path=DIR,
        partition_cols=['year', 'month', 'day'],
    )

    # Load parquet
    dataset = pq.ParquetDataset(DIR)
    table_load = dataset.read()
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