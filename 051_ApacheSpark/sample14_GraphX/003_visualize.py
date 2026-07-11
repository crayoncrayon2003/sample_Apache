# =============================================================
#  GraphX / GraphFrames : 分析結果の可視化（分析前後の比較）
#
#  分析の前後の情報を可視化する
#    分析前 : オリジナルの移動ネットワーク（全 node は同じ大きさ・色）
#    分析後 : を node の「大きさ」と「色の濃さ」に PageRank 反映 
#
#  Spark は不要。必要ライブラリ： networkx, matplotlib（+ pandas）
# =============================================================
import os
import sys
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "00X_input")
OUTPUT_DIR = os.path.join(ROOT, "00X_output")
VERTICES_CSV = os.path.join(INPUT_DIR, "vertices.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")
METRICS_CSV = os.path.join(OUTPUT_DIR, "vertex_metrics.csv")
OUTPUT_PNG = os.path.join(OUTPUT_DIR, "graph_before_after.png")

# 配色（dataviz スキルの検証済みパレットより）
SURFACE = "#fcfcfb"        # 背景
INK = "#0b0b0b"            # 主テキスト
INK_SUB = "#52514e"        # 副テキスト
EDGE_GRAY = "#b7b6af"      # 辺
NODE_FLAT = "#d9d8d0"      # Before の node の色（無彩色）
NODE_RING = "#898781"      # node の輪郭
# PageRank 用シーケンシャル(青 淡→濃)。1色相 light→dark。
BLUES = LinearSegmentedColormap.from_list(
    "brand_blues",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)


def build_graph():
    nodes = pd.read_csv(VERTICES_CSV)
    edges = pd.read_csv(EDGES_CSV)

    # 平行辺（同じ src->dst の複数移動）は trips を合計して1本にまとめる
    agg = edges.groupby(["src", "dst"], as_index=False)["trips"].sum()

    g = nx.DiGraph()
    for _, r in nodes.iterrows():
        g.add_node(r["id"], name=r["name"])
    for _, r in agg.iterrows():
        g.add_edge(r["src"], r["dst"], trips=int(r["trips"]))
    return g


def draw(ax, g, pos, node_size, node_color, title, cmap=None, norm=None):
    names = nx.get_node_attributes(g, "name")
    trips = [g[u][v]["trips"] for u, v in g.edges()]
    tmax = max(trips) if trips else 1
    widths = [0.6 + 3.4 * (t / tmax) for t in trips]   # 太さ ∝ 移動回数

    nx.draw_networkx_edges(
        ax=ax, G=g, pos=pos, width=widths, edge_color=EDGE_GRAY,
        arrows=True, arrowstyle="-|>", arrowsize=10,
        connectionstyle="arc3,rad=0.08",   # 双方向の辺が重ならないよう少し湾曲
    )
    nodes = nx.draw_networkx_nodes(
        ax=ax, G=g, pos=pos, node_size=node_size, node_color=node_color,
        cmap=cmap, vmin=(norm.vmin if norm else None), vmax=(norm.vmax if norm else None),
        edgecolors=NODE_RING, linewidths=1.0,
    )
    nx.draw_networkx_labels(ax=ax, G=g, pos=pos, labels=names, font_size=8, font_color=INK)
    ax.set_title(title, fontsize=13, color=INK, pad=12)
    ax.set_axis_off()
    ax.set_facecolor(SURFACE)
    return nodes


def main():
    if not os.path.exists(METRICS_CSV):
        sys.exit(
            "分析結果 {0} が見つかりません。\n"
            "先に  spark-submit --packages graphframes:... 002_graph_analysis.py  を実行してください。".format(METRICS_CSV)
        )

    g = build_graph()
    metrics = pd.read_csv(METRICS_CSV).set_index("id")

    # 描画位置は1度だけ計算し、Before / After で共有する（同じ配置で比較するため）
    pos = nx.spring_layout(g, seed=42, k=0.9)
    nodelist = list(g.nodes())

    # After 用：PageRank を大きさ(300〜2200)と色(青の濃淡)に写像
    pr = metrics.loc[nodelist, "pagerank"].astype(float)
    norm = Normalize(vmin=pr.min(), vmax=pr.max())
    after_sizes = [300 + 1900 * norm(v) for v in pr]
    after_colors = list(pr)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor(SURFACE)

    # Before：全 node フラット（同じ大きさ・無彩色）
    draw(ax1, g, pos, node_size=800, node_color=NODE_FLAT,
         title="Before — raw movement network")

    # After：PageRank を反映
    nodes = draw(ax2, g, pos, node_size=after_sizes, node_color=after_colors,
                 title="After — PageRank importance", cmap=BLUES, norm=norm)
    cbar = fig.colorbar(nodes, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("PageRank", color=INK_SUB)
    cbar.ax.tick_params(labelsize=8, colors=INK_SUB)

    n_comp = metrics["component"].nunique()
    fig.suptitle(
        "Taxi zone movement graph — before / after analysis", fontsize=15, color=INK
    )
    fig.text(
        0.5, 0.02,
        "Nodes = zones, edges = trips (width ∝ trip count).  "
        "Connected components: {0} (all zones mutually reachable).".format(n_comp),
        ha="center", fontsize=9, color=INK_SUB,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print("wrote figure -> {0}".format(OUTPUT_PNG))


if __name__ == "__main__":
    main()
