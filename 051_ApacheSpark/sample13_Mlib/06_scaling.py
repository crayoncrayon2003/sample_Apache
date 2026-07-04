# =============================================================
#  MLlib (5) : 特徴量の前処理 — スケーリングと次元削減
#
#  数値特徴は単位もスケールもバラバラ（距離は数十、人数は数人）。
#  そのまま学習させると大きい値の特徴が過剰に効いてしまうので、
#  StandardScaler で標準化（平均0・分散1）してそろえる。
#  さらに PCA で相関のある特徴をまとめて次元を落とす例も示す。
#
#    数値列 --VectorAssembler--> features
#      --StandardScaler-->  scaledFeatures（平均0・分散1）
#      --PCA-->             pcaFeatures（k 次元に圧縮）
# =============================================================
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler, PCA

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

spark = SparkSession.builder.master("local[*]").appName("MLlibScaling").getOrCreate()


def main():
    df = spark.read.csv(DUMMY_TAXIDATA, header=True, inferSchema=True)

    numeric_cols = ["tripDistance", "passengerCount", "totalAmount"]
    assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")
    df = assembler.transform(df).select("features").limit(10)

    print("====  (1) スケーリング前：features（生の数値ベクトル）  ====")
    df.show(truncate=False)

    # ---- StandardScaler : 平均0・分散1 に標準化 ----
    scaler = StandardScaler(
        inputCol="features", outputCol="scaledFeatures", withMean=True, withStd=True
    )
    scaler_model = scaler.fit(df)        # 各列の平均と標準偏差を学習
    df_scaled = scaler_model.transform(df)

    print("====  (2) スケーリング後：scaledFeatures（平均0・分散1）  ====")
    df_scaled.select("features", "scaledFeatures").show(truncate=False)
    print("学習した平均 mean = {0}".format(scaler_model.mean))
    print("学習した標準偏差 std = {0}".format(scaler_model.std))

    # ---- PCA : 3次元 -> 2次元へ次元削減 ----
    #   標準化済みの特徴を使い、分散を最大化する軸(主成分)へ射影する。
    pca = PCA(k=2, inputCol="scaledFeatures", outputCol="pcaFeatures")
    pca_model = pca.fit(df_scaled)
    df_pca = pca_model.transform(df_scaled)

    print("====  (3) PCA 後：pcaFeatures（3次元 -> 2次元に圧縮）  ====")
    df_pca.select("scaledFeatures", "pcaFeatures").show(truncate=False)
    print("各主成分の寄与率 explainedVariance = {0}".format(pca_model.explainedVariance))


if __name__ == "__main__":
    main()
    spark.stop()
