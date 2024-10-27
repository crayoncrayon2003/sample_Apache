from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
import os
import sys

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

conf = SparkConf()
conf.setAppName("simpleApp")
conf.setMaster("spark://localhost:7077")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

def main():
    input_data = [
        {'arithmetic': 86, 'science': 57, 'social': 45, 'music': 100},
        {'arithmetic': 67, 'science': 12, 'social': 43, 'music': 54},
        {'arithmetic': 98, 'science': 98, 'social': 78, 'music': 69},
    ]
    # rdd = spark.parallelize(input_data)
    # df  = rdd.toDF
    # print("num is {}".format(df.count()))
    df = spark.createDataFrame(input_data)
    df.show()
    print(df.show)
    print("aa")

if __name__ == "__main__":
    main()
