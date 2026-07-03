# =============================================================
#  グラフ用のダミーデータ生成（タクシーのゾーン間移動）
#
#  頂点(vertices) = タクシーの乗降ゾーン
#  辺(edges)      = あるゾーンから別ゾーンへの移動（trips 件数付き）
#
#  GraphFrames は "id" 列を持つ頂点DataFrameと、"src"/"dst" 列を持つ
#  辺DataFrame から構築する。ここではそれぞれ CSV に書き出す。
# =============================================================
import pandas as pd
import random
import os

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
VERTICES_CSV = os.path.join(ROOT, "vertices.csv")
EDGES_CSV = os.path.join(ROOT, "edges.csv")

# 乗降ゾーン（頂点）
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


def generate_vertices():
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
    vertices = generate_vertices()
    edges = generate_edges(60)

    vertices.to_csv(VERTICES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("vertices ({0}):".format(len(vertices)))
    print(vertices.head())
    print("edges ({0}):".format(len(edges)))
    print(edges.head())


if __name__ == "__main__":
    main()
