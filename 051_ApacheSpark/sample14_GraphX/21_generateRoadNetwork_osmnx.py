# =============================================================
#  実在の道路ネットワークを osmnx で取得してグラフ化する（Pattern 3 / 2番系）
#
#  1番系(11)と「同じデータ」＝滋賀県全土の幹線道路を対象にするが、
#  取得〜グラフ化を自前の Overpass 解析ではなく osmnx にまかせる。
#  osmnx は交差点抽出・通過点の簡約・距離(length)付与まで自動でやってくれる。
#
#    ・11(1番系) … 標準ライブラリで Overpass を叩き、手作業で交差点グラフ化
#    ・21(2番系) … osmnx が道路グラフを構築（位相簡約されるので頂点数は少なめ）
#
#  出力（1番系と同じ列構成にそろえ、12/22 のどちらでも読めるようにする）:
#    20_input/nodes.csv : id, lat, lon
#    20_input/edges.csv : src, dst, length_m, name, highway
# =============================================================
import os
import osmnx as ox
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "20_input")
GRAPHML = os.path.join(INPUT_DIR, "road.graphml")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

PLACE = "Shiga Prefecture, Japan"
# 1番系(11)と同じ幹線クラス。"motorway|trunk|primary|secondary" は _link も含む。
CUSTOM_FILTER = '["highway"~"motorway|trunk|primary|secondary"]'


def fetch_graph():
    """osmnx で道路グラフを取得（キャッシュ graphml があれば再利用）。"""
    if os.path.exists(GRAPHML):
        print("using cached {0}".format(GRAPHML))
        return ox.load_graphml(GRAPHML)

    print("downloading {0} via osmnx ...".format(PLACE))
    g = ox.graph_from_place(PLACE, custom_filter=CUSTOM_FILTER, simplify=True)
    os.makedirs(INPUT_DIR, exist_ok=True)
    ox.save_graphml(g, GRAPHML)
    return g


def as_text(v):
    """osmnx はタグをリストで持つことがあるので文字列に整える。"""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return "" if v is None else str(v)


def main():
    g = fetch_graph()

    # osmnx のノードは x=経度 / y=緯度、辺は length(メートル) を持つ
    node_rows = [{"id": n, "lat": float(d["y"]), "lon": float(d["x"])} for n, d in g.nodes(data=True)]
    edge_rows = [{
        "src": u, "dst": v,
        "length_m": round(float(d.get("length", 0.0)), 1),
        "name": as_text(d.get("name")),
        "highway": as_text(d.get("highway")),
    } for u, v, d in g.edges(data=True)]

    nodes = pd.DataFrame(node_rows)
    edges = pd.DataFrame(edge_rows)

    os.makedirs(INPUT_DIR, exist_ok=True)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("place : {0}".format(PLACE))
    print("nodes (intersections): {0}".format(len(nodes)))
    print("edges (road segments): {0}".format(len(edges)))
    print(nodes.head())
    print(edges.head())


if __name__ == "__main__":
    main()
