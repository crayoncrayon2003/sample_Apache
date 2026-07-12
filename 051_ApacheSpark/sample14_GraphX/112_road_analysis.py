# =============================================================
#  道路メッシュの格子グラフをグラフ解析する
#
#  111_generateRoadMeshNetwork.py が作った「1kmメッシュ=node / 隣接=辺」のグラフを
#  GraphFrames で解析する。
#    - 次数 (inDegrees / outDegrees) … 道路のある隣接メッシュが何個あるか
#    - PageRank                       … 道路網のかたまりの中で中心的なメッシュ
#    - connectedComponents            … 地理的につながった道路メッシュのかたまり
#    - 総延長(km)                     … メッシュの道路統計そのものを合計
#
#  実行は venv の python でそのまま（3系/4系どちらでも動く。GraphFrames の jar と
#  ドライバメモリはスクリプト内で設定する）：
#    python3.12 112_road_analysis.py
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
INPUT_DIR = os.path.join(ROOT, "11X_input")
OUTPUT_DIR = os.path.join(ROOT, "11X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("RoadMeshGraphAnalysis")
    .config("spark.jars.packages", GRAPHFRAMES_PACKAGE)
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
os.makedirs(OUTPUT_DIR, exist_ok=True)
spark.sparkContext.setCheckpointDir(os.path.join(OUTPUT_DIR, "checkpoint"))


def main():
    # CSV を Spark DataFrame に読み込む（header付き・型は自動推論）
    nodes = spark.read.csv(NODES_CSV, header=True, inferSchema=True)   # 列: id, lat, lon, road_length_m, road_density
    edges = spark.read.csv(EDGES_CSV, header=True, inferSchema=True)   # 列: src, dst, length_m（メッシュ中心間の距離）

    # 読み込んだ nodes / edges を先頭5行だけ確認する
    print("====  Nodes ====")
    nodes.show(5, truncate=False)
    print("====  Edges  ====")
    edges.show(5, truncate=False)

    # メッシュ(node)と隣接関係(edge)から GraphFrame を組み立てる
    # GraphFrame は、次のルールがある。
    #   nodes : カラム名に、id を持つ列が必須（node ID として使われる主キー）
    #   edges : カラム名に、src/dst を持つ列が必須 かつ、src/dstは、idの値と一致する（辺の始点/終点として使われる外部キー）
    g = GraphFrame(nodes, edges)

    # GraphFrame は g.vertices / g.edges で「node の表」「辺の表」を取り出せる（どちらもDataFrame）
    g_vertices = g.vertices   # 列: id, lat, lon, road_length_m, road_density（= 渡した nodes と同じ）
    g_edges = g.edges         # 列: src, dst, length_m（= 渡した edges と同じ）

    # ---- グラフの規模を表示（node の数・辺数） ----
    print("====  Nodes / Edges  ====")
    print("mesh cells = {0}, adjacency edges = {1}".format(g_vertices.count(), g_edges.count()))

    # ---- 次数：隣接する「道路ありメッシュ」がいくつあるか（山際・湖畔ほど値が小さくなる） ----
    print("====  In Degrees (隣接メッシュの数)  ====")
    in_degrees = g.inDegrees                                   # 列: id, inDegree
    in_degrees_sorted = in_degrees.orderBy(desc("inDegree"))
    in_degrees_sorted.show(5, truncate=False)

    print("====  Out Degrees (隣接メッシュの数)  ====")
    out_degrees = g.outDegrees                                  # 列: id, outDegree
    out_degrees_sorted = out_degrees.orderBy(desc("outDegree"))
    out_degrees_sorted.show(5, truncate=False)

    # ---- スコアを用いてメッシュをランク付けし、道路網の中心的な地域を抽出する ----
    print("====  PageRank (道路網の中心メッシュ)  ====")
    pr = g.pageRank(resetProbability=0.15, maxIter=10)   # メッシュごとの重要度スコアを計算
    pr_vertices = pr.vertices                            # 地図表示のために、node の結果を取る
    pr_ranked = pr_vertices.select("id", "pagerank").orderBy(desc("pagerank"))  # 中心メッシュトップを一覧表示
    pr_ranked.show(5, truncate=False)

    # ---- 「道路メッシュが地理的に1つにつながっているか、飛び地があるか」を知りたい ----
    print("====  Connected Components (道路メッシュのかたまり)  ====")
    cc = g.connectedComponents()                # 隣接しあうメッシュごとにグルーピング
    cc_sizes = cc.groupBy("component").count()  # 各かたまりの規模（メッシュ数）を比べるため
    cc_sizes.orderBy(desc("count")).show(5, truncate=False)   # 本体の大きなかたまりと飛び地を見分けたい

    # ---- 「対象エリアの道路が全体でどれくらいの長さか」を把握したい ----
    # 注) edge はメッシュ同士の「隣接関係」であって道路そのものではないので合計しても意味がない。
    #     実際の道路延長は node 側の属性(road_length_m = メッシュ内の道路実延長)に入っているので、
    #     総延長は node を合計して求める。
    total_km = nodes.groupBy().sum("road_length_m").collect()[0][0] / 1000.0
    print("====  Total road length ≈ {0:.2f} km  ====".format(total_km))

    # ---- 地図可視化で使えるよう、メッシュ1つにつき「座標＋各指標」を1行にまとめて渡す ----
    metrics = (
        pr_vertices.select("id", "lat", "lon", "road_length_m", "road_density", "pagerank")  # 地図に置くための座標と、統計値・重要度を土台にする
        .join(cc.select("id", "component"), on="id")               # どの道路網のかたまりに属すかを付与
        .join(in_degrees, on="id", how="left")                     # 隣接メッシュの多さも判断材料に加える
        .join(out_degrees, on="id", how="left")                    # 同上（無向なので in と同じ値になる）
        .fillna(0, subset=["inDegree", "outDegree"])               # 孤立メッシュも0として扱い、可視化で欠落させないため
    )
    # 可視化スクリプトが読みやすい単一CSVにするため、pandasに集約して書き出す
    metrics.toPandas().to_csv(os.path.join(OUTPUT_DIR, "vertex_metrics.csv"), index=False)
    print("wrote analysis results -> {0}".format(os.path.join(OUTPUT_DIR, "vertex_metrics.csv")))


if __name__ == "__main__":
    main()
    spark.stop()
