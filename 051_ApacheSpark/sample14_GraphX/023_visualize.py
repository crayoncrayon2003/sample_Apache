# =============================================================
#  osmnx で取った道路ネットワークを地図状に可視化する
#
#  node を実際の緯度経度に配置するので、絵が本物の地図の形になる。
#    Before : 生の道路ネットワーク（全交差点は同じ大きさ・色）
#    After  : PageRank を交差点の「大きさ」と「色の濃さ」に反映
#
#  Spark は不要。必要ライブラリ： networkx, matplotlib（+ pandas）
#  ※ 先に 022_road_analysis.py を spark-submit で実行して vertex_metrics.csv を作っておくこと。
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

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "02X_input")
OUTPUT_DIR = os.path.join(ROOT, "02X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")
METRICS_CSV = os.path.join(OUTPUT_DIR, "vertex_metrics.csv")
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "road_before_after.png")

# 配色（dataviz スキルの検証済みパレットより）
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SUB = "#52514e"
EDGE_GRAY = "#b7b6af"
NODE_FLAT = "#d9d8d0"
NODE_RING = "#898781"
BLUES = LinearSegmentedColormap.from_list(
    "brand_blues",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)


def geo_positions(nodes):
    """緯度経度を平面座標に。経度は cos(緯度) で縮めて地図の縦横比を合わせる。"""
    # 高緯度ほど経度1度の実距離は縮む。その補正をかけて絵が実地図と同じ縦横比になるようにする
    mean_lat = math.radians(nodes["lat"].mean())
    scale = math.cos(mean_lat)
    # id → (x, y) の対応表を作り、各交差点を実際の位置に置けるようにする
    return {row["id"]: (row["lon"] * scale, row["lat"]) for _, row in nodes.iterrows()}


def draw(ax, g, pos, node_size, node_color, title, cmap=None, norm=None, alpha=1.0):
    # Before/After で共通の描画処理。呼び出し側が大きさ・色を変えるだけで2枚を作り分けられるようにまとめてある
    # まず道路（辺）を薄いグレーで敷き、地図の骨格を見せる
    nx.draw_networkx_edges(ax=ax, G=g, pos=pos, width=0.5, edge_color=EDGE_GRAY, arrows=False)
    # その上に交差点（node）を重ねる。色をカラーバーに連動させるため描画結果を返す
    nodes = nx.draw_networkx_nodes(
        ax=ax, G=g, pos=pos, node_size=node_size, node_color=node_color,
        cmap=cmap, vmin=(norm.vmin if norm else None), vmax=(norm.vmax if norm else None),
        edgecolors=NODE_RING, linewidths=0.5, alpha=alpha,
    )
    ax.set_title(title, fontsize=13, color=INK, pad=12)
    ax.set_axis_off()
    ax.set_aspect("equal")   # 緯度経度の比率を保ち、地図が歪まないようにする
    ax.set_facecolor(SURFACE)
    return nodes


def main():
    # １つ前の分析結果が無いと可視化できないので、その場で気づけるよう先に止めて実行手順を案内する
    if not os.path.exists(METRICS_CSV):
        sys.exit(
            "分析結果 {0} が見つかりません。\n"
            "先に  spark-submit --packages graphframes:... 022_road_analysis.py  を実行してください。".format(METRICS_CSV)
        )

    # 地図の骨格（座標・つながり）は 02X_input から、色や大きさに使う指標は 022 の出力から取る
    nodes = pd.read_csv(NODES_CSV)
    edges = pd.read_csv(EDGES_CSV)
    metrics = pd.read_csv(METRICS_CSV).set_index("id")   # id で引けるようにして後で pagerank を紐付けやすくする

    # matplotlib に渡せるよう、交差点と道路のつながりを networkx のグラフに組み直す
    g = nx.DiGraph()
    for _, r in nodes.iterrows():
        g.add_node(r["id"])
    for _, r in edges.iterrows():
        g.add_edge(r["src"], r["dst"])

    # 各交差点を実際の緯度経度に置くための座標表。Before/After で同じ配置を使い、純粋に見た目の差だけを比較できるようにする
    pos = geo_positions(nodes)
    nodelist = list(g.nodes())   # 以降の色・サイズ配列を、この node の並び順に必ず揃えるための基準

    # After 用：PageRank を「点の大きさ」と「青の濃さ」に写像し、重要な交差点を一目で分かるようにする
    # metrics に無い node は最小値で補い、色スケールが破綻しないようにする
    pr = metrics.reindex(nodelist)["pagerank"].astype(float).fillna(metrics["pagerank"].min())
    norm = Normalize(vmin=pr.min(), vmax=pr.max())          # PageRank を 0〜1 に正規化し、色と大きさの基準をそろえる
    base = max(3.0, 400.0 / max(1, len(nodelist)) ** 0.5)   # node が多いほど点を小さくし、地図が黒く潰れないようにする
    after_sizes = [base + 12 * base * norm(v) for v in pr]  # 重要な交差点ほど大きく描くためのサイズ配列
    after_colors = list(pr)                                 # 同じく色付け用に PageRank をそのまま渡す

    # 同じ地図を左右に並べ、分析前後を見比べられるレイアウトにする
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(SURFACE)

    # 左（Before）：全交差点を同じ大きさ・無彩色で描き、「ただの道路網」の状態を見せる
    draw(ax1, g, pos, node_size=base, node_color=NODE_FLAT, title="Before — road network")
    # 右（After）：PageRank を大きさ・色に反映し、要衝が浮かび上がった状態を見せる
    nodes_pc = draw(ax2, g, pos, node_size=after_sizes, node_color=after_colors, title="After — central intersections (PageRank)", cmap=BLUES, norm=norm, alpha=0.7)
    # 色の濃さが何を表すかを読み手に示すため、PageRank のカラーバーを添える
    cbar = fig.colorbar(nodes_pc, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("PageRank", color=INK_SUB)
    cbar.ax.tick_params(labelsize=8, colors=INK_SUB)

    fig.suptitle("Real road network (Shiga Prefecture, via osmnx) — before / after analysis", fontsize=15, color=INK)
    fig.text(0.5, 0.02, "Nodes = intersections, edges = road segments.  Positions are real lat/lon, so the shape is the actual street map.",
             ha="center", fontsize=9, color=INK_SUB)

    # 画面表示ではなくファイルとして残し、あとから見返したり資料に使えるよう PNG に保存する
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print("wrote figure -> {0}".format(OUTPUT_PNG))


if __name__ == "__main__":
    main()
