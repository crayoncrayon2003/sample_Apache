# =============================================================
#  国土数値情報「道路密度・道路延長メッシュデータ(N04)」を格子グラフ化する
#
#  国土交通省が3次メッシュ(1kmメッシュ)単位で集計した道路統計データを取得する。
#  これは道路延長・道路密度などの数値がセルごとに入った「表形式データ」であり、
#  そもそも node/edge（つながり）の概念を持たない。
#
#  そこで、以下のルールで自分たちでグラフに組み立てる：
#    node = 道路が実在する(実延長>0)1kmメッシュ。属性として道路延長・道路密度・緯度経度を持つ
#    edge = 上下左右で隣接するメッシュ同士のつながり（格子状グラフ、斜めは含めない）
#
#  対象は滋賀県全域。
#  データ源: 国土数値情報 道路密度・道路延長メッシュデータ（N04-10, 平成22年, JGD2000）
#    https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N04.html
#
#  出力:
#    11X_input/nodes.csv : id, lat, lon, road_length_m, road_density
#    11X_input/edges.csv : src, dst, length_m
# =============================================================
import os
import zipfile
import urllib.request
import geopandas as gpd
import pandas as pd
import osmnx as ox
import math

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "11X_input")
RAW_DIR = os.path.join(INPUT_DIR, "raw")
BOUNDARY_GEOJSON = os.path.join(INPUT_DIR, "shiga_boundary.geojson")
NODES_CSV = os.path.join(INPUT_DIR, "nodes.csv")
EDGES_CSV = os.path.join(INPUT_DIR, "edges.csv")

PLACE = "Shiga Prefecture, Japan"
# 滋賀県の外接範囲(lat 34.79-35.70, lon 135.76-136.46)を覆う1次メッシュ(80km角)コード。
# 1次メッシュコードは「緯度*1.5の整数部2桁」+「経度-100の整数部2桁」なので、
# 滋賀県は緯度帯(52,53)×経度帯(35,36)の4タイルにまたがる。
MESH1_CODES = ["5235", "5236", "5335", "5336"]
N04_BASE_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/N04/N04-10/N04-10_{code}-jgd_GML.zip"


def fetch_shiga_boundary():
    """滋賀県の行政界ポリゴンを取得（キャッシュがあれば再利用）。メッシュを県域だけに絞り込むために使う。"""
    if os.path.exists(BOUNDARY_GEOJSON):
        print("using cached {0}".format(BOUNDARY_GEOJSON))
        return gpd.read_file(BOUNDARY_GEOJSON)

    print("geocoding {0} via osmnx ...".format(PLACE))
    gdf = ox.geocode_to_gdf(PLACE)
    os.makedirs(INPUT_DIR, exist_ok=True)
    gdf.to_file(BOUNDARY_GEOJSON, driver="GeoJSON")
    return gdf


def fetch_mesh_tile(code):
    """1次メッシュ単位のN04シェープファイルをダウンロード・展開する（キャッシュがあれば再利用）。"""
    tile_dir = os.path.join(RAW_DIR, code)
    shp_path = os.path.join(tile_dir, "N04-10_{0}-jgd-g_RoadDensityAndLengthMesh_H22.shp".format(code))
    if os.path.exists(shp_path):
        print("using cached {0}".format(shp_path))
        return shp_path

    url = N04_BASE_URL.format(code=code)
    print("downloading {0} ...".format(url))
    os.makedirs(tile_dir, exist_ok=True)
    zip_path = os.path.join(tile_dir, "{0}.zip".format(code))
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tile_dir)
    return shp_path


def load_mesh_cells():
    """4タイル分のメッシュを読み込み、滋賀県内かつ道路が実在するセルだけに絞り込む。"""
    boundary = fetch_shiga_boundary()
    shiga_polygon = boundary.union_all()

    frames = []
    for code in MESH1_CODES:
        shp_path = fetch_mesh_tile(code)
        gdf = gpd.read_file(shp_path, encoding="shift_jis")
        gdf.set_crs(epsg=4326, allow_override=True, inplace=True)
        frames.append(gdf)
    mesh = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")

    # 図形の重心ではなく外接矩形の中心を使う（メッシュは正方形なので同じ結果になり、
    # 地理座標系での centroid() 警告を避けられる）
    bounds = mesh.geometry.bounds
    mesh["lat"] = (bounds["miny"] + bounds["maxy"]) / 2.0
    mesh["lon"] = (bounds["minx"] + bounds["maxx"]) / 2.0

    # 滋賀県のポリゴン内にある(中心点が入っている)セルだけを残す
    centers = gpd.GeoSeries(gpd.points_from_xy(mesh["lon"], mesh["lat"]), crs="EPSG:4326")
    mesh = mesh[centers.within(shiga_polygon).values]

    # N04_055=幅員合計の実延長(m), N04_056=同・1km²換算の相対延長(m/km²=道路密度)
    # 非調査等のセルは "unknown" 文字列が入っているので、数値化できないものは道路無しとして扱う
    mesh["road_length_m"] = pd.to_numeric(mesh["N04_055"], errors="coerce").fillna(0.0)
    mesh["road_density"] = pd.to_numeric(mesh["N04_056"], errors="coerce").fillna(0.0)

    # 道路が実在するメッシュだけを node 候補にする（山地・湖面などは除外され、グラフが県全体を覆う正方形にならない）
    mesh = mesh[mesh["road_length_m"] > 0].copy()
    mesh["id"] = mesh["N04_001"].astype(str)
    return mesh[["id", "lat", "lon", "road_length_m", "road_density"]].reset_index(drop=True)


def mesh_code_to_rowcol(code):
    """3次メッシュコード(8桁)を全国共通の行番号・列番号(整数)に変換する。

    桁構成: 緯度*1.5の整数部(2桁) + (経度-100)の整数部(2桁)
           + 2次メッシュ内の行(1桁) + 列(1桁) + 3次メッシュ内の行(1桁) + 列(1桁)
    行番号・列番号さえ分かれば、隣接メッシュは ±1 するだけで求まる（タイルをまたいでも連続する）。
    """
    p, u, q, v, r, w = code[0:2], code[2:4], code[4], code[5], code[6], code[7]
    row = int(p) * 80 + int(q) * 10 + int(r)
    col = int(u) * 80 + int(v) * 10 + int(w)
    return row, col


def haversine_m(lat1, lon1, lat2, lon2):
    """2地点間の距離(メートル)。隣接メッシュ間の距離(≈1000m)を辺の重みとして持たせるために使う。"""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_edges(nodes):
    """上下左右で隣接するメッシュ同士を辺で結ぶ（格子状グラフ、斜め方向は含めない）。"""
    by_rowcol = {}
    for _, row in nodes.iterrows():
        rc = mesh_code_to_rowcol(row["id"])
        by_rowcol[rc] = row

    edge_rows = []
    for (r, c), row in by_rowcol.items():
        # 北(row+1)と東(col+1)方向だけ調べれば、双方向の辺を1回の走査で漏れなく作れる
        for dr, dc in ((1, 0), (0, 1)):
            neighbor = by_rowcol.get((r + dr, c + dc))
            if neighbor is None:
                continue
            length = round(haversine_m(row["lat"], row["lon"], neighbor["lat"], neighbor["lon"]), 1)
            edge_rows.append({"src": row["id"], "dst": neighbor["id"], "length_m": length})
            edge_rows.append({"src": neighbor["id"], "dst": row["id"], "length_m": length})
    return pd.DataFrame(edge_rows)


def main():
    # 滋賀県内・道路が実在するメッシュだけを node 候補として集める
    nodes = load_mesh_cells()
    # メッシュコードの行列番号から、隣接するメッシュ同士を辺で結ぶ
    edges = build_edges(nodes)

    os.makedirs(INPUT_DIR, exist_ok=True)
    nodes.to_csv(NODES_CSV, index=False)
    edges.to_csv(EDGES_CSV, index=False)

    print("place : {0} (mesh tiles: {1})".format(PLACE, ", ".join(MESH1_CODES)))
    print("=" * 40, "nodes", "=" * 40, )
    print("nodes (1km mesh cells with roads): {0}".format(len(nodes)))
    print(nodes.head())

    print("=" * 40, "edges", "=" * 40, )
    print("edges (mesh adjacency): {0}".format(len(edges)))
    print(edges.head())


if __name__ == "__main__":
    main()
