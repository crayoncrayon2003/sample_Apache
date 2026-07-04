# =============================================================
#  MLlib (2) : 分類 — 支払いが Card かどうかを予測する
#
#  カテゴリ列の扱いと分類の基本フロー：
#    1) StringIndexer で文字列カテゴリを数値インデックスに
#    2) OneHotEncoder でカテゴリをベクトル化
#    3) VectorAssembler で数値特徴と結合して1本のベクトルに
#    4) LogisticRegression で学習、多クラス評価で Accuracy / F1 を測る
#    5) CrossValidator + ParamGridBuilder でハイパーパラメータを調整する
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
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

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

    # 5) ハイパーパラメータ調整（クロスバリデーションで最適な組み合わせを探す）
    #    - regParam       : 正則化の強さ
    #    - elasticNetParam: L1(=1.0) と L2(=0.0) のブレンド比
    #    分類の指標として F1 を最大化するモデルを選ぶ。
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    param_grid = (
        ParamGridBuilder()
        .addGrid(lr.regParam, [0.01, 0.1, 1.0])
        .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0])
        .build()
    )
    cv = CrossValidator(
        estimator=pipeline,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,      # F1 最大のモデルを選ぶ
        numFolds=3,
        seed=42,
    )

    print("====  Cross validation (grid size = {0})  ====".format(len(param_grid)))
    cv_model = cv.fit(train_df)          # 各パラメータで学習し、最良モデルを保持
    model = cv_model.bestModel           # 最適パラメータで学習し直された Pipeline モデル
    predictions = model.transform(test_df)

    print("====  Predictions (sample)  ====")
    predictions.select("tripDistance", "totalAmount", "label", "prediction", "probability").show(10, truncate=False)

    acc = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})
    print("====  Metrics (test)  ====")
    print("Accuracy = {0:.4f}".format(acc))
    print("F1       = {0:.4f}".format(f1))

    # 選ばれた最適ハイパーパラメータ
    best_lr = model.stages[-1]
    print("====  Best params  ====")
    print("regParam        = {0}".format(best_lr.getRegParam()))
    print("elasticNetParam = {0}".format(best_lr.getElasticNetParam()))


if __name__ == "__main__":
    main()
    spark.stop()
