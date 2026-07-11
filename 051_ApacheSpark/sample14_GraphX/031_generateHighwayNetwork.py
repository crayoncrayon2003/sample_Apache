# =============================================================
#  国土数値情報「高速道路時系列データ(N06)」からインターチェンジの道路網グラフを作る
#
#  このデータは「路線(区間)」と「接合部(IC・JCT等)」が別々のシェープファイルで
#  配布されており、しかも区間は交差点ごとには分割されていない
#  （1本の区間が複数のICをまたいで長く伸びている）。そのため、
#  区間の線と接合部の点をそのまま GraphFrame には渡せず、
#  「どの接合部がどの区間上のどの位置にあるか」を自分で求めてから
#  区間を接合部ごとに輪切りにする必要がある。
#
#  手順:
#    1. 区間(HighwaySection)と接合部(Joint)を読み込み、現在も供用中のものだけ残す
#    2. 滋賀県の周辺だけに絞り込む
#    3. 区間ごとに、その線に近い接合部を探し、線上の位置(0〜1)に射影する
#    4. 線の始点・終点も含めて位置順に並べ、隣り合う点同士を1本の辺として切り出す
#
#  node = 接合部(IC/JCT)。公式の地点名を持つ場合はそれを使い、
#         区間の端が接合部に対応しない場合は座標そのものをID化した点になる
#  edge = 隣り合う接合部の間の道路（実延長・路線名つき）
#
#  対象は滋賀県の周辺（県境をまたぐ高速道路の接続を落とさないよう少し外側まで含める）。
#  データ源: 国土数値情報 高速道路時系列データ（N06-20, 令和2年度時点, 全国一括）
#    https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N06-v2_0.html
#
#  出力:
#    03X_input/nodes.csv : id, lat, lon, name
#    03X_input/edges.csv : src, dst, length_m, route_name
# =============================================================
import os
import zipfile
import urllib.request
import math
import warnings
import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely.ops import substring

# 緯度経度(度)のまま distance() を使うための警告を抑える。
# 許容距離が数百メートル程度の粗いフィルタ用途なので、度→メートルの歪みは実用上問題にならない。
warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "03X_input")
RAW_DIR = os.path.join(INPUT_DIR, "raw")
BOUNDARY_GEOJSON = os.path.join(INPUT_DIR, "shiga_boundary.geojson")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

PLACE = "Shiga Prefecture, Japan"
# 高速道路時系列データは都道府県別ではなく全国一括ファイルとして配布されている
N06_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/N06/N06-20/N06-20_GML.zip"
SECTION_SHP = "N06-20_HighwaySection.shp"
JOINT_SHP = "N06-20_Joint.shp"

BOUNDARY_BUFFER_DEG = 0.02   # 県境をまたぐ区間・接合部も拾うための緩衝距離（約2km）
SNAP_TOL_DEG = 0.003         # 接合部を区間の線に紐づける許容距離（約300m）
MERGE_TOL_M = 50.0           # 同一地点とみなす接合部同士の距離（JCT/ICが同じ場所にある場合など）


def fetch_shiga_boundary():
    """滋賀県の行政界ポリゴンを取得（キャッシュがあれば再利用）。対象範囲を絞り込むために使う。"""
    if os.path.exists(BOUNDARY_GEOJSON):
        print("using cached {0}".format(BOUNDARY_GEOJSON))
        return gpd.read_file(BOUNDARY_GEOJSON)

    print("geocoding {0} via osmnx ...".format(PLACE))
    gdf = ox.geocode_to_gdf(PLACE)
    os.makedirs(INPUT_DIR, exist_ok=True)
    gdf.to_file(BOUNDARY_GEOJSON, driver="GeoJSON")
    return gdf


def fetch_n06():
    """N06(高速道路時系列データ、全国一括)をダウンロード・展開する（キャッシュがあれば再利用）。"""
    section_path = os.path.join(RAW_DIR, SECTION_SHP)
    if os.path.exists(section_path):
        print("using cached {0}".format(section_path))
        return section_path, os.path.join(RAW_DIR, JOINT_SHP)

    print("downloading {0} ...".format(N06_URL))
    os.makedirs(RAW_DIR, exist_ok=True)
    zip_path = os.path.join(RAW_DIR, "N06-20_GML.zip")
    urllib.request.urlretrieve(N06_URL, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(RAW_DIR)
    # zip の中身は N06-20/ サブフォルダの下に展開される
    return os.path.join(RAW_DIR, "N06-20", SECTION_SHP), os.path.join(RAW_DIR, "N06-20", JOINT_SHP)


def haversine_m(lat1, lon1, lat2, lon2):
    """2地点間の距離(メートル)。輪切りにした区間の実延長を求めるために使う。"""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def line_length_m(line):
    """LineString の頂点列に沿って実延長(メートル)を積算する。"""
    coords = list(line.coords)
    return sum(
        haversine_m(coords[i][1], coords[i][0], coords[i + 1][1], coords[i + 1][0])
        for i in range(len(coords) - 1)
    )


def load_sections_and_joints():
    """N06を読み込み、現在も供用中(設置期間の終了=9999)のものだけ、滋賀県周辺に絞って返す。"""
    section_path, joint_path = fetch_n06()
    section = gpd.read_file(section_path, encoding="shift_jis")
    joint = gpd.read_file(joint_path, encoding="shift_jis")

    # N06_003/N06_014 = 設置期間の終了年。9999 は「現在も継続して設置されている」ことを表す
    section = section[section["N06_003"] == 9999].copy()
    joint = joint[joint["N06_014"] == 9999].copy()

    boundary = fetch_shiga_boundary()
    area = boundary.union_all().buffer(BOUNDARY_BUFFER_DEG)
    section = section[section.intersects(area)].copy()
    joint = joint[joint.intersects(area)].copy()
    return section, joint


def synthetic_id(lat, lon):
    """区間の端が接合部と対応しない場合に、座標から一意なIDを作る。"""
    return "PT_{0:.6f}_{1:.6f}".format(lat, lon)


def build_graph(sections, joints):
    """区間を接合部ごとに輪切りにして node / edge を組み立てる。"""
    nodes = {}   # id -> (lat, lon, name)
    edge_rows = []

    for _, sec in sections.iterrows():
        line = sec.geometry
        # この区間の近くにある接合部を探し、線上の位置(0〜1の割合)に射影する
        nearby = joints[joints.distance(line) < SNAP_TOL_DEG]
        anchors = []  # [frac, id, lat, lon, name]
        for _, j in nearby.iterrows():
            frac = line.project(j.geometry, normalized=True)
            anchors.append([frac, str(j["N06_015"]), j.geometry.y, j.geometry.x, j["N06_018"]])

        # 区間の始点・終点も、それ自体が交差点(輪切りの端)になるので anchor に含める
        for pt, frac in ((line.coords[0], 0.0), (line.coords[-1], 1.0)):
            near_existing = any(
                haversine_m(pt[1], pt[0], a[2], a[3]) < MERGE_TOL_M for a in anchors
            )
            if not near_existing:
                anchors.append([frac, synthetic_id(pt[1], pt[0]), pt[1], pt[0], ""])

        anchors.sort(key=lambda a: a[0])

        # 位置が非常に近い anchor 同士(同じ場所にある JCT と IC など)は1つにまとめる
        deduped = []
        for a in anchors:
            if deduped and haversine_m(a[2], a[3], deduped[-1][2], deduped[-1][3]) < MERGE_TOL_M:
                continue
            deduped.append(a)

        for a in deduped:
            nodes[a[1]] = (a[2], a[3], a[4])

        # 隣り合う anchor 同士を1本の辺として切り出す(区間を交差点単位に分割する)
        for i in range(len(deduped) - 1):
            f0, id0 = deduped[i][0], deduped[i][1]
            f1, id1 = deduped[i + 1][0], deduped[i + 1][1]
            sub_line = substring(line, f0, f1, normalized=True)
            length_m = round(line_length_m(sub_line), 1)
            edge_rows.append({"src": id0, "dst": id1, "length_m": length_m, "route_name": sec["N06_007"]})
            edge_rows.append({"src": id1, "dst": id0, "length_m": length_m, "route_name": sec["N06_007"]})

    node_rows = [{"id": k, "lat": v[0], "lon": v[1], "name": v[2]} for k, v in nodes.items()]
    return pd.DataFrame(node_rows), pd.DataFrame(edge_rows)


def main():
    sections, joints = load_sections_and_joints()
    nodes, edges = build_graph(sections, joints)

    os.makedirs(INPUT_DIR, exist_ok=True)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("place : {0}".format(PLACE))
    print("=" * 40, "nodes", "=" * 40, )
    print("nodes (interchanges / junctions): {0}".format(len(nodes)))
    print(nodes.head(10))

    print("=" * 40, "edges", "=" * 40, )
    print("edges (highway segments between interchanges): {0}".format(len(edges)))
    print(edges.head(10))


if __name__ == "__main__":
    main()
