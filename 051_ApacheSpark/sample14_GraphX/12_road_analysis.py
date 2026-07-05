# =============================================================
#  実在の道路ネットワークをグラフ解析する（Pattern 2 / 1番系）
#
#  11_generateRoadNetwork.py が作った「交差点=node / 道路区間=辺」のグラフを
#  GraphFrames で解析する。0番系(02)と同じ API を、実データに対して使う。
#    - 次数 (inDegrees / outDegrees) … 何本の道が集まる交差点か
#    - PageRank                       … ネットワーク上で中心的な交差点
#    - connectedComponents            … 連結した道路のかたまり
#    - 総延長(km)                     … 道路網ならではの集計
#  （shortestPaths は大規模道路網では Pregel が OOM を起こすため 02 で扱う。理由は下記）
#
#  実行にはパッケージ指定とドライバメモリ指定が必要：
#    spark-submit --driver-memory 2g \
#      --packages graphframes:graphframes:0.8.4-spark3.5-s_2.12 12_road_analysis.py
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
INPUT_DIR = os.path.join(ROOT, "10_input")
OUTPUT_DIR = os.path.join(ROOT, "10_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

spark = SparkSession.builder.master("local[*]").appName("RoadGraphAnalysis").getOrCreate()
os.makedirs(OUTPUT_DIR, exist_ok=True)
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

    # ---- スコアを用いて交差点をランク付けし、重要な交差点を抽出する ----
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

    # 注) shortestPaths はここでは実行しない。
    #   GraphX の shortestPaths(Pregel) はチェックポイントせず反復するため、
    #   道路網のように直径が大きいグラフでは反復回数が数百に達し、系統(lineage)が肥大して
    #   ドライバが OutOfMemory になる。最短ホップ数のデモは小規模な Pattern 1 (02) で行う。

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
