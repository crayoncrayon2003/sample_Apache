# =============================================================
#  Bronze 層 : 生データの取り込み(as-is)
#
#  @sdp.materialized_view で取り込む。ここでは変換をせず、
#  00_input/DummyTaxiData.csv をそのまま読むだけ(生の履歴を残す)。
#
#  ※ @sdp.table は「ストリーミングテーブル」になり、ストリーミング源
#    (readStream) が必要。batch な CSV なので materialized_view を使う。
#    Kafka 等のストリーミング源にするなら @sdp.table + spark.readStream。
#
#  クエリ関数はパイプライン実行時に呼ばれる。その時点で有効な Spark
#  セッション(Spark Connect)を SparkSession.active() で取得する。
# =============================================================
import os
from pyspark import pipelines as sdp
from pyspark.sql import SparkSession

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(ROOT, "00_input", "DummyTaxiData.csv")


@sdp.materialized_view(comment="生のタクシーデータ(無変換で取り込む bronze 層)")
def bronze_taxi_raw():
    spark = SparkSession.active()
    return (
        spark.read
        .format("csv")
        .option("header", True)
        .option("inferSchema", True)
        .load(INPUT_CSV)
    )
