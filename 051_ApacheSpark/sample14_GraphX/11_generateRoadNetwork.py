# =============================================================
#  実在の道路ネットワークを取得してグラフ化する（Pattern 2 / 1番系）
#
#  OpenStreetMap の Overpass API から、滋賀県全土の幹線道路を取得し、
#  「交差点=頂点 / 道路区間=辺(距離付き)」のグラフに変換して 10_input/ に書き出す。
#
#  ・題材は滋賀県全域の幹線道路（高速・国道・主要地方道クラス）。
#    県全体だと琵琶湖を囲む道路網の構造が見え、ネットワークとして理解しやすい。
#  ・追加の地理ライブラリ(osmnx 等)は使わず、標準ライブラリだけで取得・変換する。
#  ・生の応答は 10_input/osm_raw.json にキャッシュし、再実行やオフラインでも動く。
#
#  出力:
#    10_input/nodes.csv : id, lat, lon               （交差点）
#    10_input/edges.csv : src, dst, length_m, name, highway （道路区間）
# =============================================================
import os
import json
import math
import urllib.request
import urllib.parse
from collections import Counter
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "10_input")
RAW_JSON = os.path.join(INPUT_DIR, "osm_raw.json")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

# 取得する範囲：OSM の行政界(admin_level=4 = 都道府県)。県名を変えれば他県も試せる。
PLACE = "Shiga Prefecture (major roads)"
AREA_NAME = "滋賀県"
ADMIN_LEVEL = "4"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# 幹線道路だけに絞る（高速・国道・主要地方道クラス）。県全体の全道路は巨大すぎるため。
DRIVE_TAGS = {
    "motorway", "trunk", "primary", "secondary",
    "motorway_link", "trunk_link", "primary_link", "secondary_link",
}


def fetch_osm():
    """Overpass から車道の way とその構成 node を取得（キャッシュがあれば再利用）。"""
    if os.path.exists(RAW_JSON):
        print("using cached {0}".format(RAW_JSON))
        with open(RAW_JSON, encoding="utf-8") as f:
            return json.load(f)

    # 行政界エリア内の幹線道路を取得する。
    # ※ Overpass 手前の Apache が正規表現(|付き)クエリを 406 で弾くため、正規表現は使わず
    #   種別ごとの完全一致 way を union(...) で並べる。
    ways = "".join('way["highway"="{0}"](area.a);'.format(t) for t in sorted(DRIVE_TAGS))
    query = (
        "[out:json][timeout:300];"
        'area["name"="{name}"]["admin_level"="{lvl}"]->.a;'
        "({ways});(._;>;);out body;"
    ).format(name=AREA_NAME, lvl=ADMIN_LEVEL, ways=ways)

    print("downloading road network for {0} ...".format(PLACE))
    data = urllib.parse.urlencode({"data": query}).encode()
    # デフォルトの User-Agent (Python-urllib) はサーバに拒否される(406)ことがあるので明示する
    headers = {"User-Agent": "sample14-graphx-tutorial/1.0", "Accept": "application/json"}
    req = urllib.request.Request(OVERPASS_URL, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    os.makedirs(INPUT_DIR, exist_ok=True)
    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f)
    return raw


def haversine_m(lat1, lon1, lat2, lon2):
    """2地点間の距離(メートル)。"""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_graph(raw):
    """OSM の node/way を「交差点グラフ」に変換する。

    道の途中にある通過点(次数2)はまとめ、交差点と端点だけを頂点として残す。
    """
    coords = {e["id"]: (e["lat"], e["lon"]) for e in raw["elements"] if e["type"] == "node"}
    # 車道の way だけを対象にする（歩道・階段などは除外）
    ways = [
        e for e in raw["elements"]
        if e["type"] == "way" and "nodes" in e and e.get("tags", {}).get("highway") in DRIVE_TAGS
    ]

    # 各 node が「いくつの車道 way に含まれるか」を数え、交差点(>=2)を判定する
    way_count = Counter()
    endpoints = set()
    for w in ways:
        for nid in set(w["nodes"]):
            way_count[nid] += 1
        endpoints.add(w["nodes"][0])
        endpoints.add(w["nodes"][-1])

    def is_junction(nid):
        return way_count[nid] >= 2 or nid in endpoints

    node_rows = {}
    edge_rows = []
    for w in ways:
        tags = w.get("tags", {})
        highway = tags.get("highway", "")
        name = tags.get("name", "")
        oneway = tags.get("oneway", "")

        seq = [n for n in w["nodes"] if n in coords]
        if len(seq) < 2:
            continue

        # way を交差点ごとに区切り、区間ごとに距離を合計して1本の辺にする
        start = seq[0]
        acc = 0.0
        for a, b in zip(seq[:-1], seq[1:]):
            la1, lo1 = coords[a]
            la2, lo2 = coords[b]
            acc += haversine_m(la1, lo1, la2, lo2)
            if is_junction(b) or b == seq[-1]:
                if start != b and acc > 0:
                    length = round(acc, 1)
                    forward = {"src": start, "dst": b, "length_m": length, "name": name, "highway": highway}
                    if oneway in ("yes", "true", "1"):
                        edge_rows.append(forward)
                    elif oneway == "-1":
                        edge_rows.append({"src": b, "dst": start, "length_m": length, "name": name, "highway": highway})
                    else:  # 双方向
                        edge_rows.append(forward)
                        edge_rows.append({"src": b, "dst": start, "length_m": length, "name": name, "highway": highway})
                    for nid in (start, b):
                        node_rows[nid] = {"id": nid, "lat": coords[nid][0], "lon": coords[nid][1]}
                start = b
                acc = 0.0

    nodes = pd.DataFrame(node_rows.values())
    edges = pd.DataFrame(edge_rows)
    return nodes, edges


def main():
    raw = fetch_osm()
    nodes, edges = build_graph(raw)

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
