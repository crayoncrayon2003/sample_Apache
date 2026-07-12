# =============================================================
#  高速道路のインターチェンジ網をグラフ解析する
#
#  031_generateHighwayNetwork.py が作った「IC/JCT=node / IC間の道路=辺」のグラフを
#  GraphFrames で解析する。
#    - 次数 (inDegrees / outDegrees) … そのICで何本の道路に分岐・合流できるか
#    - PageRank                       … 高速道路網の中で中心的なIC・JCT
#    - connectedComponents            … つながっている高速道路網のかたまり
#    - 総延長(km)                     … 対象区間の道路延長の合計
#
#  実行は venv の python でそのまま（3系/4系どちらでも動く。GraphFrames の jar と
#  ドライバメモリはスクリプト内で設定する）：
#    python3.12 032_highway_analysis.py
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
INPUT_DIR = os.path.join(ROOT, "03X_input")
OUTPUT_DIR = os.path.join(ROOT, "03X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("HighwayGraphAnalysis")
    .config("spark.jars.packages", GRAPHFRAMES_PACKAGE)
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
os.makedirs(OUTPUT_DIR, exist_ok=True)
spark.sparkContext.setCheckpointDir(os.path.join(OUTPUT_DIR, "checkpoint"))


def main():
    # CSV を Spark DataFrame に読み込む（header付き・型は自動推論）
    nodes = spark.read.csv(NODES_CSV, header=True, inferSchema=True)   # 列: id, lat, lon, name
    edges = spark.read.csv(EDGES_CSV, header=True, inferSchema=True)   # 列: src, dst, length_m, route_name

    # 読み込んだ nodes / edges を先頭5行だけ確認する
    print("====  Nodes ====")
    nodes.show(5, truncate=False)
    print("====  Edges  ====")
    edges.show(5, truncate=False)

    # IC/JCT(node)とその間の道路(edge)から GraphFrame を組み立てる
    # GraphFrame は、次のルールがある。
    #   nodes : カラム名に、id を持つ列が必須（node ID として使われる主キー）
    #   edges : カラム名に、src/dst を持つ列が必須 かつ、src/dstは、idの値と一致する（辺の始点/終点として使われる外部キー）
    g = GraphFrame(nodes, edges)

    # GraphFrame は g.vertices / g.edges で「node の表」「辺の表」を取り出せる（どちらもDataFrame）
    g_vertices = g.vertices   # 列: id, lat, lon, name（= 渡した nodes と同じ）
    g_edges = g.edges         # 列: src, dst, length_m, route_name（= 渡した edges と同じ）

    # ---- グラフの規模を表示（node の数・辺数） ----
    print("====  Nodes / Edges  ====")
    print("interchanges/junctions = {0}, road segments = {1}".format(g_vertices.count(), g_edges.count()))

    # ---- 次数：そのICで何本の道路に分岐・合流できるか（JCTほど値が大きくなる） ----
    print("====  In Degrees (分岐・合流の多いIC/JCT)  ====")
    in_degrees = g.inDegrees                                   # 列: id, inDegree
    in_degrees_sorted = in_degrees.orderBy(desc("inDegree"))
    in_degrees_sorted.show(5, truncate=False)

    print("====  Out Degrees (分岐・合流の多いIC/JCT)  ====")
    out_degrees = g.outDegrees                                  # 列: id, outDegree
    out_degrees_sorted = out_degrees.orderBy(desc("outDegree"))
    out_degrees_sorted.show(5, truncate=False)

    # ---- スコアを用いてIC/JCTをランク付けし、高速道路網の中心的な地点を抽出する ----
    print("====  PageRank (高速道路網の中心IC/JCT)  ====")
    pr = g.pageRank(resetProbability=0.15, maxIter=10)   # ICごとの重要度スコアを計算
    pr_vertices = pr.vertices                            # 地図表示のために、node の結果を取る
    pr_ranked = pr_vertices.select("id", "name", "pagerank").orderBy(desc("pagerank"))  # 中心IC/JCTトップを一覧表示
    pr_ranked.show(10, truncate=False)

    # ---- 「高速道路網が1つにつながっているか、飛び地(未接続の区間)があるか」を知りたい ----
    print("====  Connected Components (つながっている高速道路網のかたまり)  ====")
    cc = g.connectedComponents()                # 互いに行き来できる範囲ごとに node をグルーピング
    cc_sizes = cc.groupBy("component").count()  # 各かたまりの規模（node数）を比べるため
    cc_sizes.orderBy(desc("count")).show(5, truncate=False)   # 本体の大きな道路網と孤立区間を見分けたい

    # ---- 「対象エリアの高速道路が全体でどれくらいの長さか」を把握したい ----
    total_km = edges.groupBy().sum("length_m").collect()[0][0] / 1000.0 / 2.0   # 双方向2本ぶんを打ち消し、実延長のkmにするため
    print("====  Total highway length ≈ {0:.2f} km  ====".format(total_km))

    # ---- 地図可視化で使えるよう、IC/JCT1つにつき「座標＋各指標」を1行にまとめて渡す ----
    metrics = (
        pr_vertices.select("id", "lat", "lon", "name", "pagerank")  # 地図に置くための座標と、重要度を土台にする
        .join(cc.select("id", "component"), on="id")               # どの高速道路網のかたまりに属すかを付与
        .join(in_degrees, on="id", how="left")                     # 分岐・合流の多さも判断材料に加える
        .join(out_degrees, on="id", how="left")                    # 同上
        .fillna(0, subset=["inDegree", "outDegree"])               # 行き止まり等で欠ける node も0として扱い、可視化で欠落させないため
    )
    # 可視化スクリプトが読みやすい単一CSVにするため、pandasに集約して書き出す
    metrics.toPandas().to_csv(os.path.join(OUTPUT_DIR, "vertex_metrics.csv"), index=False)
    print("wrote analysis results -> {0}".format(os.path.join(OUTPUT_DIR, "vertex_metrics.csv")))


if __name__ == "__main__":
    main()
    spark.stop()
