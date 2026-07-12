# =============================================================
#  道路メッシュの格子グラフを地図状に可視化する
#
#  node を実際の緯度経度(メッシュ中心)に配置するので、絵が本物の地図の形になる。
#    Before : 生のメッシュ格子（道路密度をそのまま色に反映。まだグラフ解析はしていない状態）
#    After  : PageRank をメッシュの「大きさ」と「色の濃さ」に反映（グラフ解析した状態）
#
#  Spark は不要。必要ライブラリ： networkx, matplotlib（+ pandas）
#  ※ 先に 112_road_analysis.py を実行して vertex_metrics.csv を作っておくこと。
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
INPUT_DIR = os.path.join(ROOT, "11X_input")
OUTPUT_DIR = os.path.join(ROOT, "11X_output")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")
METRICS_CSV = os.path.join(OUTPUT_DIR, "vertex_metrics.csv")
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "road_mesh_before_after.png")

# 配色（dataviz スキルの検証済みパレットより）
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SUB = "#52514e"
EDGE_GRAY = "#b7b6af"
NODE_RING = "#898781"
BLUES = LinearSegmentedColormap.from_list(
    "brand_blues",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)
GREENS = LinearSegmentedColormap.from_list(
    "brand_greens",
    ["#dcefd7", "#b7ddac", "#8fca80", "#61b350", "#3f9430", "#2c7420", "#1c5613"],
)


def geo_positions(nodes):
    """緯度経度を平面座標に。経度は cos(緯度) で縮めて地図の縦横比を合わせる。"""
    mean_lat = math.radians(nodes["lat"].mean())
    scale = math.cos(mean_lat)
    return {row["id"]: (row["lon"] * scale, row["lat"]) for _, row in nodes.iterrows()}


def draw(ax, g, pos, node_size, node_color, title, cmap=None, norm=None, alpha=1.0):
    # Before/After で共通の描画処理。呼び出し側が大きさ・色を変えるだけで2枚を作り分けられるようにまとめてある
    nx.draw_networkx_edges(ax=ax, G=g, pos=pos, width=0.4, edge_color=EDGE_GRAY, arrows=False)
    nodes = nx.draw_networkx_nodes(
        ax=ax, G=g, pos=pos, node_size=node_size, node_color=node_color,
        cmap=cmap, vmin=(norm.vmin if norm else None), vmax=(norm.vmax if norm else None),
        edgecolors=NODE_RING, linewidths=0.3, alpha=alpha,
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
            "先に  python3.12 112_road_analysis.py  を実行してください。".format(METRICS_CSV)
        )

    # 地図の骨格（座標・つながり）は 11X_input から、色や大きさに使う指標は 112 の出力から取る
    nodes = pd.read_csv(NODES_CSV)
    edges = pd.read_csv(EDGES_CSV)
    metrics = pd.read_csv(METRICS_CSV).set_index("id")   # id で引けるようにして後で pagerank 等を紐付けやすくする

    # matplotlib に渡せるよう、メッシュと隣接関係を networkx のグラフに組み直す
    g = nx.DiGraph()
    for _, r in nodes.iterrows():
        g.add_node(r["id"])
    for _, r in edges.iterrows():
        g.add_edge(r["src"], r["dst"])

    # 各メッシュを実際の緯度経度(メッシュ中心)に置くための座標表。Before/After で同じ配置を使う
    pos = geo_positions(nodes)
    nodelist = list(g.nodes())   # 以降の色・サイズ配列を、この node の並び順に必ず揃えるための基準

    base = max(2.0, 300.0 / max(1, len(nodelist)) ** 0.5)   # node が多いほど点を小さくし、地図が潰れないようにする

    # Before 用：グラフ解析をする前でも国土数値情報にすでに入っている「道路密度」をそのまま色に使う
    density = metrics.reindex(nodelist)["road_density"].astype(float).fillna(0.0)
    density_norm = Normalize(vmin=density.min(), vmax=density.max())

    # After 用：PageRank を「点の大きさ」と「青の濃さ」に写像し、道路網の中心メッシュを一目で分かるようにする
    pr = metrics.reindex(nodelist)["pagerank"].astype(float).fillna(metrics["pagerank"].min())
    pr_norm = Normalize(vmin=pr.min(), vmax=pr.max())
    after_sizes = [base + 12 * base * pr_norm(v) for v in pr]
    after_colors = list(pr)

    # 同じ地図を左右に並べ、分析前後を見比べられるレイアウトにする
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(SURFACE)

    # 左（Before）：国土数値情報の道路密度をそのまま色にした「生のメッシュ統計」
    nodes_before = draw(
        ax1, g, pos, node_size=base, node_color=list(density), title="Before — raw road-density mesh (MLIT N04)",
        cmap=GREENS, norm=density_norm,
    )
    cbar1 = fig.colorbar(nodes_before, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label("road density (m / km²)", color=INK_SUB)
    cbar1.ax.tick_params(labelsize=8, colors=INK_SUB)

    # 右（After）：格子グラフとしてPageRankを計算し、大きさ・色に反映した状態
    nodes_after = draw(
        ax2, g, pos, node_size=after_sizes, node_color=after_colors, title="After — central mesh cells (PageRank)",
        cmap=BLUES, norm=pr_norm, alpha=0.8,
    )
    cbar2 = fig.colorbar(nodes_after, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label("PageRank", color=INK_SUB)
    cbar2.ax.tick_params(labelsize=8, colors=INK_SUB)

    fig.suptitle("Road density mesh (Shiga Prefecture, MLIT N04) — before / after graph analysis", fontsize=15, color=INK)
    fig.text(0.5, 0.02, "Nodes = 1km mesh cells with roads, edges = grid adjacency (N/E/S/W).  Positions are real lat/lon.",
             ha="center", fontsize=9, color=INK_SUB)

    # 画面表示ではなくファイルとして残し、あとから見返したり資料に使えるよう PNG に保存する
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print("wrote figure -> {0}".format(OUTPUT_PNG))


if __name__ == "__main__":
    main()
