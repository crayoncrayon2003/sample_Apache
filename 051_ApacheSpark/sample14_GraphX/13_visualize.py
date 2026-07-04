# =============================================================
#  実在の道路ネットワークを地図状に可視化する（Pattern 2 / 1番系）
#
#  頂点を実際の緯度経度に配置するので、絵が本物の地図の形になる。
#    Before : 生の道路ネットワーク（全交差点は同じ大きさ・色）
#    After  : PageRank を交差点の「大きさ」と「色の濃さ」に反映
#             （＝中心的な交差点ほど大きく濃く表示）
#
#  Spark は不要。必要ライブラリ： networkx, matplotlib（+ pandas）
#  ※ 先に 12 を spark-submit で実行して vertex_metrics.csv を作っておくこと。
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
INPUT_DIR = os.path.join(ROOT, "10_input")
OUTPUT_DIR = os.path.join(ROOT, "10_output")
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
    mean_lat = math.radians(nodes["lat"].mean())
    scale = math.cos(mean_lat)
    return {row["id"]: (row["lon"] * scale, row["lat"]) for _, row in nodes.iterrows()}


def draw(ax, g, pos, node_size, node_color, title, cmap=None, norm=None, alpha=1.0):
    nx.draw_networkx_edges(ax=ax, G=g, pos=pos, width=0.5, edge_color=EDGE_GRAY, arrows=False)
    nodes = nx.draw_networkx_nodes(
        ax=ax, G=g, pos=pos, node_size=node_size, node_color=node_color,
        cmap=cmap, vmin=(norm.vmin if norm else None), vmax=(norm.vmax if norm else None),
        edgecolors=NODE_RING, linewidths=0.5, alpha=alpha,
    )
    ax.set_title(title, fontsize=13, color=INK, pad=12)
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.set_facecolor(SURFACE)
    return nodes


def main():
    if not os.path.exists(METRICS_CSV):
        sys.exit(
            "分析結果 {0} が見つかりません。\n"
            "先に  spark-submit --packages graphframes:... 12_road_analysis.py  を実行してください。".format(METRICS_CSV)
        )

    nodes = pd.read_csv(NODES_CSV)
    edges = pd.read_csv(EDGES_CSV)
    metrics = pd.read_csv(METRICS_CSV).set_index("id")

    g = nx.DiGraph()
    for _, r in nodes.iterrows():
        g.add_node(r["id"])
    for _, r in edges.iterrows():
        g.add_edge(r["src"], r["dst"])

    pos = geo_positions(nodes)
    nodelist = list(g.nodes())

    # After 用：PageRank を大きさと色(青の濃淡)に写像。
    #   ノード数が多いほど点を小さくして、地図の形が潰れないようにする。
    pr = metrics.reindex(nodelist)["pagerank"].astype(float).fillna(metrics["pagerank"].min())
    norm = Normalize(vmin=pr.min(), vmax=pr.max())
    base = max(3.0, 400.0 / max(1, len(nodelist)) ** 0.5)   # 頂点数に応じた基準サイズ
    after_sizes = [base + 12 * base * norm(v) for v in pr]
    after_colors = list(pr)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(SURFACE)

    draw(ax1, g, pos, node_size=base, node_color=NODE_FLAT,
         title="Before — road network")
    nodes_pc = draw(ax2, g, pos, node_size=after_sizes, node_color=after_colors,
                    title="After — central intersections (PageRank)", cmap=BLUES, norm=norm, alpha=0.7)
    cbar = fig.colorbar(nodes_pc, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("PageRank", color=INK_SUB)
    cbar.ax.tick_params(labelsize=8, colors=INK_SUB)

    fig.suptitle("Real road network (Shiga Prefecture) — before / after analysis",
                 fontsize=15, color=INK)
    fig.text(0.5, 0.02,
             "Nodes = intersections, edges = road segments.  "
             "Positions are real lat/lon, so the shape is the actual street map.",
             ha="center", fontsize=9, color=INK_SUB)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print("wrote figure -> {0}".format(OUTPUT_PNG))


if __name__ == "__main__":
    main()
