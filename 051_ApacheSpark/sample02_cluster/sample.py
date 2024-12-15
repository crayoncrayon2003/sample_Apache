import os
import sys
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import*
from pyspark.sql.session import SparkSession
from pyspark.context import SparkContext
import pandas as pd

#Spark configuration
conf = SparkConf() \
        .setAppName("simpleApp") \
        .setMaster("spark://localhost:7077") \
        .set("spark.local.ip", "localhost") \
        .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
        .set("spark.pyspark.python", "/usr/bin/python3.12")
# conf = SparkConf() \
#         .setAppName("simpleApp") \
#         .setMaster('local') \
#         .set("spark.local.ip", "localhost") \
#         .set("spark.pyspark.driver.python", "/usr/bin/python3.12") \
#         .set("spark.pyspark.python", "/usr/bin/python3.12")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

def main():
    dict_data = [
        {'arithmetic': 86, 'science': 57, 'social': 45, 'music': 100},
        {'arithmetic': 67, 'science': 12, 'social': 43, 'music': 54},
        {'arithmetic': 98, 'science': 98, 'social': 78, 'music': 69},
    ]
    df_pandas = pd.DataFrame(dict_data)
    df_spark = spark.createDataFrame(df_pandas)
    df_spark.show()
    print("done..")


if __name__ == "__main__":
    print('\033[31m{0}\033[0m'.format("This sample is aveilable python3.12"))
    main()
