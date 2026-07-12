# =============================================================
#  Gold 層 : 集計(BI / レポート向け)
#
#  @sdp.materialized_view で「集計結果を実体化したビュー」を宣言する。
#  silver を月次で集計し、売上・トリップ数・平均距離を出す。
#  依存(silver_taxi_clean)はエンジンが DAG から自動解決する。
# =============================================================
from pyspark import pipelines as sdp
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, sum as _sum, avg, round as _round


@sdp.materialized_view(comment="月次の売上サマリ(gold 層)")
def gold_monthly_revenue():
    spark = SparkSession.active()
    return (
        spark.read.table("silver_taxi_clean")
        .groupBy("pickupYear", "pickupMonth", "paymentType")
        .agg(
            count("*").alias("tripCount"),
            _round(_sum("totalAmount"), 2).alias("totalRevenue"),
            _round(avg("tripDistance"), 2).alias("avgDistance"),
        )
        .orderBy("pickupYear", "pickupMonth", "paymentType")
    )
