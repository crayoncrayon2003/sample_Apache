# =============================================================
#  GraphX / GraphFrames : グラフ解析
#
#  GraphX には Python API が無いため、PySpark では GraphFrames を使う。
#  この1本で代表的なグラフ処理をひと通り体験する：
#    - 次数 (inDegrees / outDegrees)
#    - PageRank（重要なゾーンの推定）
#    - connectedComponents（連結成分）
#    - モチーフ探索（A->B->C の経路パターン抽出）
#    - shortestPaths（指定ゾーンへの最短ホップ数）
#
#  実行にはパッケージ指定が必要（README 参照）：
#    spark-submit \
#      --packages graphframes:graphframes:0.8.4-spark3.5-s_2.12 \
#      02_graph_analysis.py
# =============================================================
import os
from pyspark.sql import SparkSession
from graphframes import GraphFrame

ROOT = os.path.dirname(os.path.abspath(__file__))
VERTICES_CSV = os.path.join(ROOT, "vertices.csv")
EDGES_CSV = os.path.join(ROOT, "edges.csv")

spark = SparkSession.builder.master("local[*]").appName("GraphFramesDemo").getOrCreate()
# connectedComponents はチェックポイントを必要とするため出力先を設定する
spark.sparkContext.setCheckpointDir(os.path.join(ROOT, "checkpoint"))


def main():
    vertices = spark.read.csv(VERTICES_CSV, header=True, inferSchema=True)   # 列: id, name
    edges = spark.read.csv(EDGES_CSV, header=True, inferSchema=True)         # 列: src, dst, trips, distance

    g = GraphFrame(vertices, edges)

    print("====  Vertices / Edges  ====")
    g.vertices.show(truncate=False)
    g.edges.show(5, truncate=False)

    print("====  In / Out Degrees  ====")
    g.inDegrees.orderBy("inDegree", ascending=False).show(truncate=False)
    g.outDegrees.orderBy("outDegree", ascending=False).show(truncate=False)

    print("====  PageRank (重要なゾーン)  ====")
    pr = g.pageRank(resetProbability=0.15, maxIter=10)
    pr.vertices.select("id", "name", "pagerank").orderBy("pagerank", ascending=False).show(truncate=False)

    print("====  Connected Components  ====")
    cc = g.connectedComponents()
    cc.select("id", "name", "component").show(truncate=False)

    print("====  Motif: A -> B -> C  ====")
    motifs = g.find("(a)-[]->(b); (b)-[]->(c)")
    motifs.select("a.id", "b.id", "c.id").show(10, truncate=False)

    print("====  Shortest Paths to Airport(Z01) / Station(Z03)  ====")
    sp = g.shortestPaths(landmarks=["Z01", "Z03"])
    sp.select("id", "name", "distances").show(truncate=False)


if __name__ == "__main__":
    main()
    spark.stop()
