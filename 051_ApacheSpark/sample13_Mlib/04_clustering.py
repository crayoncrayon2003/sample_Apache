# =============================================================
#  MLlib (3) : クラスタリング — 乗車パターンを教師なしで分ける
#
#  回帰・分類は「正解ラベル」を使う教師あり学習だった。
#  クラスタリングはラベルを使わず、データの近さだけでグループ分けする
#  教師なし学習。ここでは KMeans で乗車を k 個のクラスタに分ける。
#
#  ポイント：スケールの違う特徴をそのまま使うと距離計算が歪むので、
#  ここでも StandardScaler で標準化してから KMeans にかける。
# =============================================================
import os
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

spark = SparkSession.builder.master("local[*]").appName("MLlibClustering").getOrCreate()


def main():
    df = spark.read.csv(DUMMY_TAXIDATA, header=True, inferSchema=True)

    feature_cols = ["tripDistance", "passengerCount", "totalAmount"]
    df = df.select(*feature_cols).na.drop()

    # 前処理(ベクトル化 -> 標準化) + KMeans を Pipeline に
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="rawFeatures")
    scaler = StandardScaler(inputCol="rawFeatures", outputCol="features", withMean=True, withStd=True)
    kmeans = KMeans(featuresCol="features", k=3, seed=42)
    pipeline = Pipeline(stages=[assembler, scaler, kmeans])

    model = pipeline.fit(df)
    predictions = model.transform(df)

    print("====  クラスタ割り当て(sample)  ====")
    predictions.select(*feature_cols, "prediction").show(10, truncate=False)

    print("====  クラスタごとの件数  ====")
    predictions.groupBy("prediction").count().orderBy("prediction").show()

    # シルエット係数：-1〜1 で、1に近いほどクラスタがよく分離できている
    evaluator = ClusteringEvaluator(featuresCol="features", predictionCol="prediction")
    silhouette = evaluator.evaluate(predictions)
    print("====  Metrics  ====")
    print("Silhouette = {0:.4f}".format(silhouette))

    # 各クラスタの中心（標準化後の空間での座標）
    kmeans_model = model.stages[-1]
    print("====  Cluster centers (standardized space)  ====")
    for i, center in enumerate(kmeans_model.clusterCenters()):
        print("cluster {0}: {1}".format(i, center))


if __name__ == "__main__":
    main()
    spark.stop()
