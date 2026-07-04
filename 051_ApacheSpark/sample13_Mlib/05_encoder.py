# =============================================================
#  MLlib (4) : エンコーダー — カテゴリ列をベクトルに変換する
#
#  03_classification.py では StringIndexer / OneHotEncoder が
#  Pipeline の中に埋もれていて「何が起きているか」が見えない。
#  ここでは1段ずつ transform して、エンコード前後で DataFrame が
#  どう変わるかを show() で並べて確認する。
#
#    生データ(文字列)
#      --StringIndexer-->  数値インデックス列を追加
#      --OneHotEncoder-->  one-hot ベクトル列を追加
# =============================================================
import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

spark = SparkSession.builder.master("local[*]").appName("MLlibEncoder").getOrCreate()


def main():
    # 全データで学習(fit)し、変化は先頭10件だけ表示(show)する。
    # ※ limit してから fit すると一部カテゴリを取りこぼすので、fit は全データで行う。
    df = spark.read.csv(DUMMY_TAXIDATA, header=True, inferSchema=True).select("paymentType")

    # ---- Before : 文字列カテゴリのまま ----
    print("====  (1) 生データ：paymentType は文字列  ====")
    df.show(10, truncate=False)

    # ---- StringIndexer : 文字列 -> 数値インデックス ----
    #   出現頻度が多いカテゴリほど小さい番号(0,1,2,...)が振られる。
    indexer = StringIndexer(inputCol="paymentType", outputCol="paymentIdx")
    indexer_model = indexer.fit(df)          # ラベル一覧を学習する Estimator
    df_indexed = indexer_model.transform(df)

    print("====  (2) StringIndexer 後：paymentIdx 列が増える  ====")
    df_indexed.show(10, truncate=False)
    print("index の対応（頻度順）: {0}".format(
        {label: i for i, label in enumerate(indexer_model.labels)}))

    # ---- OneHotEncoder : インデックス -> one-hot ベクトル ----
    #   デフォルト dropLast=True なので、カテゴリ数 - 1 次元の疎ベクトルになる
    #   （多重共線性を避けるため最後のカテゴリは全0で表す）。
    encoder = OneHotEncoder(inputCols=["paymentIdx"], outputCols=["paymentVec"])
    encoder_model = encoder.fit(df_indexed)
    df_encoded = encoder_model.transform(df_indexed)

    print("====  (3) OneHotEncoder 後：paymentVec 列(疎ベクトル)が増える  ====")
    df_encoded.show(10, truncate=False)
    n = len(indexer_model.labels)
    print("疎ベクトルの読み方: (次元数, [値が1の位置], [その値]) の形。")
    print("カテゴリは {0} 種類だが dropLast=True なので次元数は {1}。".format(n, n - 1))
    print("例) ({0},[0],[1.0]) は 0番目だけが1 = index 0 のカテゴリ。".format(n - 1))
    print("    最後のカテゴリ(index {0})は全0 = ({1},[],[]) で表される。".format(n - 1, n - 1))


if __name__ == "__main__":
    main()
    spark.stop()
