# =============================================================
#  MLlib (2) : 分類 — 支払いが Card かどうかを予測する
#
#  カテゴリ列の扱いと分類の基本フロー：
#    1) StringIndexer で文字列カテゴリを数値インデックスに
#    2) OneHotEncoder でカテゴリをベクトル化
#    3) VectorAssembler で数値特徴と結合して1本のベクトルに
#    4) LogisticRegression で学習、多クラス評価で Accuracy / F1 を測る
#
#  01_generateDummyTaxiData.py は「距離が長いほど Card」という
#  弱い相関を入れているので、距離から Card 率をある程度学習できる。
# =============================================================
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

spark = SparkSession.builder.master("local[*]").appName("MLlibClassification").getOrCreate()


def main():
    df = spark.read.csv(DUMMY_TAXIDATA, header=True, inferSchema=True)

    # 目的変数：Card なら 1、それ以外は 0（二値分類）
    df = df.withColumn("label", when(col("paymentType") == "Card", 1.0).otherwise(0.0))
    # 乗車人数をカテゴリ扱いにするための文字列列（one-hot の題材）
    df = df.withColumn("passengerBucket", col("passengerCount").cast("string"))

    numeric_cols = ["tripDistance", "totalAmount"]

    # 1) 文字列カテゴリ -> 数値インデックス
    indexer = StringIndexer(inputCol="passengerBucket", outputCol="passengerIdx", handleInvalid="keep")
    # 2) インデックス -> one-hot ベクトル
    encoder = OneHotEncoder(inputCols=["passengerIdx"], outputCols=["passengerVec"])
    # 3) 数値特徴 + one-hot を1本のベクトルに
    assembler = VectorAssembler(inputCols=numeric_cols + ["passengerVec"], outputCol="features")
    # 4) 分類器
    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=20)

    pipeline = Pipeline(stages=[indexer, encoder, assembler, lr])

    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    print("====  Predictions (sample)  ====")
    predictions.select("tripDistance", "totalAmount", "label", "prediction", "probability").show(10, truncate=False)

    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
    acc = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
    print("====  Metrics  ====")
    print("Accuracy = {0:.4f}".format(acc))
    print("F1       = {0:.4f}".format(f1))


if __name__ == "__main__":
    main()
    spark.stop()
