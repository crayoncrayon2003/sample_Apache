# =============================================================
#  グラフ用のダミーデータ生成（タクシーのゾーン間移動）
#
#  node = タクシーの乗降ゾーン
#  辺(edges)      = あるゾーンから別ゾーンへの移動（trips 件数付き）
#
#  GraphFrames は "id" 列を持つ node の DataFrameと、"src"/"dst" 列を持つ
#  辺DataFrame から構築する。ここではそれぞれ 00_input/ 配下の CSV に書き出す。
# =============================================================
import pandas as pd
import random
import os

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "00_input")
VERTICES_CSV = os.path.join(INPUT_DIR, "vertices.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

# 乗降ゾーン（node）
ZONES = [
    ("Z01", "Airport"),
    ("Z02", "Downtown"),
    ("Z03", "Station"),
    ("Z04", "Harbor"),
    ("Z05", "University"),
    ("Z06", "Stadium"),
    ("Z07", "Suburb"),
    ("Z08", "Hospital"),
]


def generate_nodes():
    return pd.DataFrame([{"id": zid, "name": name} for zid, name in ZONES])


def generate_edges(records):
    ids = [zid for zid, _ in ZONES]
    rows = []
    for _ in range(records):
        src = random.choice(ids)
        dst = random.choice(ids)
        if src == dst:
            continue  # 自己ループは除外
        rows.append({
            "src": src,
            "dst": dst,
            "trips": random.randint(1, 50),          # その区間の移動回数
            "distance": round(random.uniform(0.5, 20.0), 2),
        })
    return pd.DataFrame(rows)


def main():
    nodes = generate_nodes()
    edges = generate_edges(60)

    os.makedirs(INPUT_DIR, exist_ok=True)
    nodes.to_csv(VERTICES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("nodes ({0}):".format(len(nodes)))
    print(nodes.head())
    print("edges ({0}):".format(len(edges)))
    print(edges.head())


if __name__ == "__main__":
    main()
