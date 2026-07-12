# =============================================================
#  osmnx で取った道路ネットワークをグラフ解析する
#
#  021_generateRoadNetwork_osmnx.py が作った 02X_input/ のグラフを GraphFrames で解析する。
#    - 次数 (inDegrees / outDegrees)
#    - PageRank
#    - connectedComponents
#    - 総延長(km)
#  （shortestPaths は大規模道路網では Pregel が OOM を起こすため、ここでは扱わない）
#
#  実行は venv の python でそのまま（3系/4系どちらでも動く。GraphFrames の jar と
#  ドライバメモリはスクリプト内で設定する）：
#    python3.12 022_road_analysis.py
# =============================================================
import os
import pyspark

# Use the Spark jars bundled with the active pyspark (ignore any stale shell
# SPARK_HOME), so this runs under whichever venv is active — 3系 or 4系.
os.environ["SPARK_HOME"] = os.path.dirname(pyspark.__file__)

# The GraphFrames JVM package must match Spark (4.x = Scala 2.13, 3.x = Scala
# 2.12). Derive it from pyspark.__version__; pulled via spark.jars.packages.
SPARK_VERSION = pyspark.__version__
if SPARK_VERSION.startswith("4"):
    GRAPHFRAMES_PACKAGE = "io.graphframes:graphframes-spark4_2.13:0.12.1"
else:
    GRAPHFRAMES_PACKAGE = "io.graphframes:graphframes-spark3_2.12:0.12.1"

from pyspark.sql import SparkSession
from pyspark.sql.functions import desc
from graphframes import GraphFrame

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "02X_input")
OUTPUT_DIR = os.path.join(ROOT, "02X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

# ローカル全コアで Spark を起動する
spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("RoadGraphAnalysisOsmnx")
    .config("spark.jars.packages", GRAPHFRAMES_PACKAGE)
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# connectedComponents 等が中間結果を保存するチェックポイント先を指定
spark.sparkContext.setCheckpointDir(os.path.join(OUTPUT_DIR, "checkpoint"))


def main():
    # CSV を Spark DataFrame に読み込む（header付き・型は自動推論）
    nodes = spark.read.csv(NODES_CSV, header=True, inferSchema=True)   # 列: id, lat, lon
    edges = spark.read.csv(EDGES_CSV, header=True, inferSchema=True)   # 列: src, dst, length_m, name, highway

    # 読み込んだ nodes / edges を先頭5行だけ確認する
    print("====  Nodes ====")
    nodes.show(5, truncate=False)
    print("====  Edges  ====")
    edges.show(5, truncate=False)

    # 交差点(node)と道路区間(edge)から GraphFrame を組み立てる
    # GraphFrame は、次のルールがある。
    #   nodes : カラム名に、id を持つ列が必須（node ID として使われる主キー）
    #   edges : カラム名に、src/dst を持つ列が必須 かつ、src/dstは、idの値と一致する（辺の始点/終点として使われる外部キー）
    g = GraphFrame(nodes, edges)

    # GraphFrame は g.vertices / g.edges で「node の表」「辺の表」を取り出せる（どちらもDataFrame）
    g_vertices = g.vertices   # 列: id, lat, lon （= 渡した nodes と同じ）
    g_edges = g.edges         # 列: src, dst, length_m, name, highway （= 渡した edges と同じ）

    # ---- グラフの規模を表示（node の数・辺数）と辺サンプル ----
    print("====  Nodes / Edges  ====")
    print("intersections = {0}, road segments = {1}".format(g_vertices.count(), g_edges.count()))
    g_edges.select("src", "dst", "length_m", "name", "highway").show(5, truncate=False)

    # ---- 流入数：多くの道が流れ込む交差点ほど値が大きい ----
    print("====  In Degrees (道が集まる交差点)  ====")
    # node への流入数入次数を求める。g.inDegrees は、新しいDataFrameを返す、列は id, inDegree
    in_degrees = g.inDegrees                                   # 列: id, inDegree
    in_degrees.show(5, truncate=False)                         # 上位5件を表示
    in_degrees_sorted = in_degrees.orderBy(desc("inDegree"))   # inDegree の大きい順に並べ替え
    in_degrees_sorted.show(5, truncate=False)                  # 上位5件を表示

    print("====  Out Degrees (道が集まる交差点)  ====")
    # node からの流出数出次数を求める。g.outDegrees は、新しいDataFrameを返す、列は id, outDegree
    out_degrees = g.outDegrees                                  # 列: id, outDegree
    out_degrees.show(5, truncate=False)                         # 上位5件を表示
    out_degrees_sorted = out_degrees.orderBy(desc("outDegree")) # outDegree の大きい順に並べ替え
    out_degrees_sorted.show(5, truncate=False)                  # 上位5件を表示

    # ---- スコアを持ちて交差点をランク付けして、重要な交差点を抽出する ----
    print("====  PageRank (中心的な交差点)  ====")
    pr = g.pageRank(resetProbability=0.15, maxIter=10)   # 交差点ごとの重要度スコアを計算
    pr_vertices = pr.vertices                            # 地図表示のために、node の結果を取る
    pr_vertices.show(5, truncate=False)                  # 入力の nodes と同じ列に pagerank が追加される
    pr_ranked = pr_vertices.select("id", "pagerank").orderBy(desc("pagerank"))  # 要衝トップを一覧表示
    pr_ranked.show(5, truncate=False)                    # 中心的な交差点トップ5を確認

    # ---- 「道路網が1つにつながっているか、離れ小島があるか」を知りたい ----
    print("====  Connected Components (道路のかたまり)  ====")
    cc = g.connectedComponents()                # 互いに行き来できる範囲ごとに node をグルーピング
    cc.show(5, truncate=False)                  # id, lat, lon, component の列ができる。component は同じ道路網の node は同じ値になる
    cc_sizes = cc.groupBy("component").count()  # 各かたまりの規模（node の数）を比べるため
    cc_sizes.orderBy(desc("count")).show(5, truncate=False)   # 本体の大きな道路網と孤立塊を見分けたい

    # ---- 「対象エリアの道路が全体でどれくらいの長さか」を把握したい ----
    total_km = edges.groupBy().sum("length_m").collect()[0][0] / 1000.0 / 2.0   # 双方向2本ぶんを打ち消し、実延長のkmにするため
    print("====  Total road length ≈ {0:.2f} km  ====".format(total_km))

    # ---- 地図可視化で使えるよう交差点1つにつき「座標＋各指標」を1行にまとめて渡す ----
    metrics = (
        pr_vertices.select("id", "lat", "lon", "pagerank")         # 地図に置くための座標と、重要度を土台にする
        .join(cc.select("id", "component"), on="id")               # どの道路網に属すかを付与
        .join(in_degrees, on="id", how="left")                     # 流入の多さも判断材料に加える
        .join(out_degrees, on="id", how="left")                    # 流出の多さも判断材料に加える
        .fillna(0, subset=["inDegree", "outDegree"])               # 行き止まり等で欠ける node も0として扱い、可視化で欠落させないため
    )
    # 可視化スクリプトが読みやすい単一CSVにするため、pandasに集約して書き出す
    metrics.toPandas().to_csv(os.path.join(OUTPUT_DIR, "vertex_metrics.csv"), index=False)
    print("wrote analysis results -> {0}".format(os.path.join(OUTPUT_DIR, "vertex_metrics.csv")))


if __name__ == "__main__":
    main()
    spark.stop()
