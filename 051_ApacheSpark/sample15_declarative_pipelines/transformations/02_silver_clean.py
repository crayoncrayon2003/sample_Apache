# =============================================================
#  Silver 層 : クレンジング
#
#  bronze への依存は spark.read.table("bronze_taxi_raw") と書くだけ。
#  実行順序(bronze -> silver)はエンジンが DAG から自動で決める。
#
#  ※ データ品質チェック(expectation)について
#    Spark 4.1 の Python SDP API には expect 系デコレータが無い。
#    OSS SDP で品質制約を宣言的に書きたい場合は SQL 定義の
#      CONSTRAINT <name> EXPECT (<condition>) [ON VIOLATION DROP ROW]
#    を使う。ここでは Python なので、同等の絞り込みを .where() で行う。
# =============================================================
from pyspark import pipelines as sdp
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth


@sdp.materialized_view(comment="クレンジング済みタクシーデータ(silver 層)")
def silver_taxi_clean():
    spark = SparkSession.active()
    return (
        spark.read.table("bronze_taxi_raw")
        # 品質フィルタ(SQL の EXPECT ... ON VIOLATION DROP ROW 相当)
        .where((col("totalAmount") > 0) & (col("passengerCount") > 0))
        .withColumn("pickupYear", year(col("pickupDateTime")))
        .withColumn("pickupMonth", month(col("pickupDateTime")))
        .withColumn("pickupDay", dayofmonth(col("pickupDateTime")))
    )
