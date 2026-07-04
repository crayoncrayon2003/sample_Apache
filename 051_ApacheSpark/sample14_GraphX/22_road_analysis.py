# =============================================================
#  osmnx で取った道路ネットワークをグラフ解析する（Pattern 3 / 2番系）
#
#  21_generateRoadNetwork_osmnx.py が作った 20_input/ のグラフを GraphFrames で解析する。
#  分析内容は 1番系(12)と同じ（データの作り方だけが Overpass 手作業 → osmnx の違い）。
#    - 次数 (inDegrees / outDegrees)
#    - PageRank
#    - connectedComponents
#    - 総延長(km)
#  （shortestPaths は大規模道路網では Pregel が OOM を起こすため 02 で扱う）
#
#  実行にはパッケージ指定とドライバメモリ指定が必要：
#    spark-submit --driver-memory 2g \
#      --packages graphframes:graphframes:0.8.4-spark3.5-s_2.12 22_road_analysis.py
# =============================================================
import os
import sys

# --- 実行する Python インタプリタを固定する（02 と同じ。詳細は 02_graph_analysis.py 参照） ---
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_BIN = os.path.join(REPO_ROOT, "env", "bin", "python")
if os.path.exists(PYTHON_BIN) and os.path.abspath(sys.executable) != PYTHON_BIN:
    os.execv(PYTHON_BIN, [PYTHON_BIN] + sys.argv)
PIN_PY = PYTHON_BIN if os.path.exists(PYTHON_BIN) else sys.executable
os.environ["PYSPARK_PYTHON"] = PIN_PY
os.environ["PYSPARK_DRIVER_PYTHON"] = PIN_PY

from pyspark.sql import SparkSession
from pyspark.sql.functions import desc
from graphframes import GraphFrame

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "20_input")
OUTPUT_DIR = os.path.join(ROOT, "20_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

spark = SparkSession.builder.master("local[*]").appName("RoadGraphAnalysisOsmnx").getOrCreate()
os.makedirs(OUTPUT_DIR, exist_ok=True)
spark.sparkContext.setCheckpointDir(os.path.join(OUTPUT_DIR, "checkpoint"))


def main():
    vertices = spark.read.csv(NODES_CSV, header=True, inferSchema=True)   # 列: id, lat, lon
    edges = spark.read.csv(EDGES_CSV, header=True, inferSchema=True)       # 列: src, dst, length_m, name, highway

    g = GraphFrame(vertices, edges)

    print("====  Vertices / Edges  ====")
    print("intersections = {0}, road segments = {1}".format(g.vertices.count(), g.edges.count()))
    g.edges.select("src", "dst", "length_m", "name", "highway").show(5, truncate=False)

    print("====  In / Out Degrees (道が集まる交差点)  ====")
    g.inDegrees.orderBy(desc("inDegree")).show(5, truncate=False)

    print("====  PageRank (中心的な交差点)  ====")
    pr = g.pageRank(resetProbability=0.15, maxIter=10)
    pr.vertices.select("id", "pagerank").orderBy(desc("pagerank")).show(5, truncate=False)

    print("====  Connected Components (道路のかたまり)  ====")
    cc = g.connectedComponents()
    cc.groupBy("component").count().orderBy(desc("count")).show(5, truncate=False)

    # 道路ネットワークならではの集計：総延長（辺は双方向で2重に持つので半分にする）
    total_km = edges.groupBy().sum("length_m").collect()[0][0] / 1000.0 / 2.0
    print("====  Total road length ≈ {0:.2f} km  ====".format(total_km))

    # ---- 可視化用に 分析結果を 20_output/ へ書き出す（緯度経度も付ける） ----
    metrics = (
        pr.vertices.select("id", "lat", "lon", "pagerank")
        .join(cc.select("id", "component"), on="id")
        .join(g.inDegrees, on="id", how="left")
        .join(g.outDegrees, on="id", how="left")
        .fillna(0, subset=["inDegree", "outDegree"])
    )
    metrics.toPandas().to_csv(os.path.join(OUTPUT_DIR, "vertex_metrics.csv"), index=False)
    print("wrote analysis results -> {0}".format(os.path.join(OUTPUT_DIR, "vertex_metrics.csv")))


if __name__ == "__main__":
    main()
    spark.stop()
