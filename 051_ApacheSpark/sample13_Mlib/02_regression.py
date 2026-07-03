# =============================================================
#  MLlib (1) : 回帰 — 乗車料金(totalAmount)を予測する
#
#  Spark ML の基本フロー：
#    1) 特徴量を VectorAssembler で1本のベクトル列にまとめる
#    2) Pipeline に前処理と推定器(LinearRegression)を並べる
#    3) train/test に分割して fit / transform
#    4) RegressionEvaluator で RMSE / R2 を評価する
# =============================================================
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, unix_timestamp
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

spark = SparkSession.builder.master("local[*]").appName("MLlibRegression").getOrCreate()


def main():
    # 1) 読み込み（型推論あり）
    df = spark.read.csv(DUMMY_TAXIDATA, header=True, inferSchema=True)

    # 乗車時間(分)を特徴量として作る
    df = df.withColumn(
        "durationMin",
        (unix_timestamp(col("dropoffDateTime")) - unix_timestamp(col("pickupDateTime"))) / 60.0,
    )

    feature_cols = ["tripDistance", "passengerCount", "durationMin"]
    df = df.select(*feature_cols, col("totalAmount").alias("label")).na.drop()

    # 2) 特徴量ベクトル化 + 線形回帰 を Pipeline に
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    lr = LinearRegression(featuresCol="features", labelCol="label")
    pipeline = Pipeline(stages=[assembler, lr])

    # 3) 学習/評価に分割
    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    print("====  Predictions (sample)  ====")
    predictions.select("features", "label", "prediction").show(10, truncate=False)

    # 4) 評価
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction")
    rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
    r2 = evaluator.evaluate(predictions, {evaluator.metricName: "r2"})
    print("====  Metrics  ====")
    print("RMSE = {0:.4f}".format(rmse))
    print("R2   = {0:.4f}".format(r2))

    # 学習された係数
    lr_model = model.stages[-1]
    print("coefficients = {0}".format(lr_model.coefficients))
    print("intercept    = {0:.4f}".format(lr_model.intercept))


if __name__ == "__main__":
    main()
    spark.stop()
