# =============================================================
#  高速道路のインターチェンジ網を地図状に可視化する
#
#  node を実際の緯度経度(IC/JCTの位置)に配置するので、絵が本物の地図の形になる。
#    Before : 生のIC/JCTネットワーク（全ノードは同じ大きさ・色）
#    After  : PageRank をノードの「大きさ」と「色の濃さ」に反映
#
#  Spark は不要。必要ライブラリ： networkx, matplotlib（+ pandas）
#  ※ 先に 032 を実行して vertex_metrics.csv を作っておくこと。
# =============================================================
import os
import sys
import math
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.collections import LineCollection

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "03X_input")
OUTPUT_DIR = os.path.join(ROOT, "03X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")
METRICS_CSV = os.path.join(OUTPUT_DIR, "vertex_metrics.csv")
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "highway_before_after.png")

# 背景に薄く敷く「滋賀の一般主要道」を OSM から取得するための設定。
# N06(高速道路)だけだと 01/02 の全道路網マップと見た目が揃わないので、
# 高速以外の主要道(国道・主要県道クラス)を背景として重ね、地図の骨格を 01/02 とそろえる。
# ※ 背景はあくまで文脈用の下絵で、グラフ解析(PageRank・連結成分)の対象ではない。
PLACE = "Shiga Prefecture, Japan"
# 021 と同じ幹線道路クラス（motorway|trunk|primary|secondary、_link も含む）
CUSTOM_FILTER = '["highway"~"motorway|trunk|primary|secondary"]'
# 背景道路のキャッシュ。pattern 3(02X)を既に実行済みならその graphml を再利用してダウンロードを省く。
BG_GRAPHML = os.path.join(INPUT_DIR, "bg_roads.graphml")
REUSE_GRAPHML = os.path.join(ROOT, "02X_input", "road.graphml")

# 配色（dataviz スキルの検証済みパレットより）
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SUB = "#52514e"
EDGE_GRAY = "#b7b6af"
NODE_FLAT = "#d9d8d0"
NODE_RING = "#898781"
BG_ROAD = "#e6e5de"   # 背景の一般主要道（高速グラフより一段薄いグレー）
BLUES = LinearSegmentedColormap.from_list(
    "brand_blues",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)


def geo_positions(nodes):
    """緯度経度を平面座標に。経度は cos(緯度) で縮めて地図の縦横比を合わせる。"""
    mean_lat = math.radians(nodes["lat"].mean())
    scale = math.cos(mean_lat)
    pos = {row["id"]: (row["lon"] * scale, row["lat"]) for _, row in nodes.iterrows()}
    return pos, scale   # scale は背景道路も同じ平面座標に揃えるために返す


def load_background_roads(scale):
    """背景に敷く滋賀の一般主要道(OSM)を、線分の集まりとして返す。
    高速グラフと同じ (lon*scale, lat) 平面に載せるので位置がぴったり重なる。
    osmnx が無い・ダウンロードに失敗した場合は空リストを返し、背景なしで図を作る。"""
    try:
        import osmnx as ox
    except ImportError:
        print("osmnx が無いため背景の一般道は省略します（高速グラフのみ描画）。")
        return []

    try:
        if os.path.exists(REUSE_GRAPHML):
            print("using cached {0} (pattern 3 の取得結果を再利用)".format(REUSE_GRAPHML))
            g = ox.load_graphml(REUSE_GRAPHML)
        elif os.path.exists(BG_GRAPHML):
            print("using cached {0}".format(BG_GRAPHML))
            g = ox.load_graphml(BG_GRAPHML)
        else:
            print("downloading background roads for {0} via osmnx ...".format(PLACE))
            g = ox.graph_from_place(PLACE, custom_filter=CUSTOM_FILTER, simplify=True)
            os.makedirs(INPUT_DIR, exist_ok=True)
            ox.save_graphml(g, BG_GRAPHML)
    except Exception as e:   # ネットワーク不通など。背景無しでも図は成立するので落とさない
        print("背景の一般道の取得に失敗したため省略します: {0}".format(e))
        return []

    segments = []
    for u, v, d in g.edges(data=True):
        geom = d.get("geometry")
        if geom is not None:   # 簡約されずに曲線形状を持つ辺は、その折れ線をそのまま使う
            segments.append([(x * scale, y) for x, y in zip(*geom.xy)])
        else:                  # 直線の辺は両端ノードを結ぶ
            segments.append([
                (float(g.nodes[u]["x"]) * scale, float(g.nodes[u]["y"])),
                (float(g.nodes[v]["x"]) * scale, float(g.nodes[v]["y"])),
            ])
    return segments


def draw(ax, g, pos, node_size, node_color, title, cmap=None, norm=None, alpha=1.0, bg=None):
    # Before/After で共通の描画処理。呼び出し側が大きさ・色を変えるだけで2枚を作り分けられるようにまとめてある
    # 背景の一般主要道を最初に(最背面に)敷く。高速グラフはこの上に重なる
    if bg:
        ax.add_collection(LineCollection(bg, colors=BG_ROAD, linewidths=0.5, zorder=0))
    nx.draw_networkx_edges(ax=ax, G=g, pos=pos, width=1.2, edge_color=EDGE_GRAY, arrows=False)
    nodes = nx.draw_networkx_nodes(
        ax=ax, G=g, pos=pos, node_size=node_size, node_color=node_color,
        cmap=cmap, vmin=(norm.vmin if norm else None), vmax=(norm.vmax if norm else None),
        edgecolors=NODE_RING, linewidths=0.6, alpha=alpha,
    )
    ax.set_title(title, fontsize=13, color=INK, pad=12)
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.set_facecolor(SURFACE)
    return nodes


def main():
    # １つ前の分析結果が無いと可視化できないので、その場で気づけるよう先に止めて実行手順を案内する
    if not os.path.exists(METRICS_CSV):
        sys.exit(
            "分析結果 {0} が見つかりません。\n"
            "先に  python3.12 032_highway_analysis.py  を実行してください。".format(METRICS_CSV)
        )

    # 地図の骨格（座標・つながり）は 03X_input から、色や大きさに使う指標は 032 の出力から取る
    nodes = pd.read_csv(NODES_CSV)
    edges = pd.read_csv(EDGES_CSV)
    metrics = pd.read_csv(METRICS_CSV).set_index("id")   # id で引けるようにして後で pagerank を紐付けやすくする

    # matplotlib に渡せるよう、IC/JCTとその間の道路を networkx のグラフに組み直す
    g = nx.DiGraph()
    for _, r in nodes.iterrows():
        g.add_node(r["id"])
    for _, r in edges.iterrows():
        g.add_edge(r["src"], r["dst"])

    # 各ノードを実際の緯度経度(IC/JCTの位置)に置くための座標表。Before/After で同じ配置を使う
    pos, scale = geo_positions(nodes)
    # 背景に敷く一般主要道(OSM)。高速グラフと同じ scale で平面化して位置を揃える
    bg_roads = load_background_roads(scale)
    nodelist = list(g.nodes())   # 以降の色・サイズ配列を、この node の並び順に必ず揃えるための基準

    # After 用：PageRank を「点の大きさ」と「青の濃さ」に写像し、重要なIC/JCTを一目で分かるようにする
    pr = metrics.reindex(nodelist)["pagerank"].astype(float).fillna(metrics["pagerank"].min())
    norm = Normalize(vmin=pr.min(), vmax=pr.max())
    base = 60.0   # ノード数が少ないので固定サイズにして見やすくする
    after_sizes = [base + 10 * base * norm(v) for v in pr]
    after_colors = list(pr)

    # 同じ地図を左右に並べ、分析前後を見比べられるレイアウトにする
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(SURFACE)

    # 左（Before）：全IC/JCTを同じ大きさ・無彩色で描き、「ただの道路網」の状態を見せる
    draw(ax1, g, pos, node_size=base, node_color=NODE_FLAT, title="Before — highway interchange network", bg=bg_roads)
    # 右（After）：PageRankを大きさ・色に反映し、要衝が浮かび上がった状態を見せる
    nodes_after = draw(
        ax2, g, pos, node_size=after_sizes, node_color=after_colors, title="After — central interchanges (PageRank)",
        cmap=BLUES, norm=norm, alpha=0.85, bg=bg_roads,
    )
    cbar = fig.colorbar(nodes_after, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("PageRank", color=INK_SUB)
    cbar.ax.tick_params(labelsize=8, colors=INK_SUB)

    fig.suptitle("Highway interchange network (Shiga Prefecture, MLIT N06) — before / after graph analysis", fontsize=15, color=INK)
    fig.text(0.5, 0.02, "Blue graph = MLIT N06 expressways (nodes = interchanges/junctions, sized by PageRank).  "
             "Light-gray background = other major roads (national / main prefectural) from OSM, for context only.",
             ha="center", fontsize=9, color=INK_SUB)

    # 画面表示ではなくファイルとして残し、あとから見返したり資料に使えるよう PNG に保存する
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print("wrote figure -> {0}".format(OUTPUT_PNG))


if __name__ == "__main__":
    main()
