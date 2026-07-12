# sample14_GraphX — GraphX / GraphFrames

**GraphX** is one of Spark's four main parts. It handles graph data (vertices and edges).

GraphX has no Python API, so PySpark uses **GraphFrames** instead.

Samples are numbered `[family][variant][step]` — 1st digit = graph type, 2nd = dataset, 3rd = step.

**Dataset (1st + 2nd digit)**

| number | graph type | input file type | overview |
|---|---|---|---|
| `00X` | pure | CSV (self-generated) | dummy taxi data → zone-to-zone graph (GraphFrames basics) |
| `01X` | pure | JSON (Overpass API) | OpenStreetMap, hand-parsed → real road network |
| `02X` | pure | GraphML (via `osmnx`) | OpenStreetMap via osmnx → same road network, less redundant |
| `03X` | pure | shapefile (line + point features, not mesh polygons) | MLIT N06 expressways → interchange network |
| `11X` | forced | shapefile (mesh polygons, not line + point) | MLIT N04 road-density mesh → grid graph |

*"pure" = the source already has a node/edge structure; "forced" = no structure, so the graph itself has to be defined.*

---

**GraphX** は Spark の4大機能の一つで、グラフデータ(頂点と辺)を扱う。

GraphX に Python API は無いため、PySpark では代わりに **GraphFrames** を使う。

サンプルは `[family][variant][step]` の3桁で番号付けしている(1桁目=グラフ種別、2桁目=データセット、3桁目=step)。

**データセット(1・2桁目)**

| 番号 | グラフ種別 | 入力ファイル種別 | 概要 |
|---|---|---|---|
| `00X` | 純粋 | CSV(自前生成) | ダミーのタクシーデータ → ゾーン間グラフ(GraphFrames の基本) |
| `01X` | 純粋 | JSON(Overpass API) | OpenStreetMap を手動パース → 実道路網 |
| `02X` | 純粋 | GraphML(`osmnx` 経由) | OpenStreetMap を osmnx で取得 → 同じ道路網(冗長ノードが少ない) |
| `03X` | 純粋 | シェープファイル(線+点で構成。メッシュポリゴンではない) | 国交省 N06 高速道路 → IC/JCT 網 |
| `11X` | 強制 | シェープファイル(メッシュポリゴン。線+点ではない) | 国交省 N04 道路密度メッシュ → グリッドグラフ |

*「純粋」= 元データが最初からノード/辺の構造を持つ / 「強制」= 構造が無いのでグラフ自体を定義する。*

## Pattern 1 (000番台) — GraphFrames basics

Build a taxi zone-to-zone graph and run the classic graph algorithms:
degrees, PageRank, connected components, motif finding, and shortest paths.
Then draw a before/after picture so the analysis is easy to read.

```bash
# 1) Generate the graph data (written to 00X_input/)
python3.12 001_generateGraphData.py

# 2) Analyze — just run with the venv's python (works on 3系 / 4系).
#    The GraphFrames jar is auto-selected from the running Spark version.
python3.12 002_graph_analysis.py

# 2b) Same as above, but split the output: print/show -> out.txt, Spark logs -> spark.log
python3.12 002_graph_analysis.py > out.txt 2> spark.log


# 3) Visualize before/after into 00X_output/graph_before_after.png
python3.12 003_visualize.py
```

The "after" picture maps each zone's PageRank to node **size** and **color**
(darker blue = more important), so the hub zones stand out at a glance.

## Pattern 2 (010番台) — a real road network

A **real road network** downloaded from OpenStreetMap:
the major roads (expressways / national / main prefectural roads) of **Shiga Prefecture** (~7,500 intersections).

Because the whole prefecture is used, the picture shows the road network wrapping around Lake Biwa.

 Nodes are intersections, edges are road segments with their real length in metres, so PageRank finds the central intersections and the visualization comes out shaped like an actual map.

```bash
# 1) Download the road network from OpenStreetMap into 01X_input/
python3.12 011_generateRoadNetwork.py

# 2) Analyze — writes the results to 01X_output/vertex_metrics.csv
python3.12 012_road_analysis.py

# 2b) Same as above, but split the output: print/show -> out.txt, Spark logs -> spark.log
python3.12 012_road_analysis.py > out.txt 2> spark.log

# 3) Visualize before/after into 01X_output/road_before_after.png
python3.12 013_visualize.py
```

Only the standard library is used to fetch and parse the OSM data (no `osmnx`).

## Pattern 3 (020番台) — the same road network via osmnx

Same data as Pattern 2 (the major roads of Shiga Prefecture).

But the download and graph building are done by **osmnx** instead of hand-parsing Overpass.

osmnx extracts intersections, simplifies pass-through nodes, and fills in segment lengths for you, so the graph is more compact (fewer redundant nodes).

The GraphFrames analysis and the visualization are the same as Pattern 2.

```bash
# 1) Download via osmnx into 02X_input/ (cached as 02X_input/road.graphml)
python3.12 021_generateRoadNetwork_osmnx.py

# 2) Analyze — writes 02X_output/vertex_metrics.csv
python3.12 022_road_analysis.py

# 2b) Same as above, but split the output: print/show -> out.txt, Spark logs -> spark.log
python3.12 022_road_analysis.py > out.txt 2> spark.log

# 3) Visualize before/after into 02X_output/road_before_after.png
python3.12 023_visualize.py
```

## Pattern 4 (030番台) — highway interchanges from a government time-series dataset

MLIT's (国土交通省) **高速道路時系列データ (N06)** from 国土数値情報, downloaded as a single
nationwide file. Unlike OSM, this data ships as two separate shapefiles — line features for
highway sections and point features for interchanges/junctions — and the sections are **not**
split at every interchange (one line can pass by several ICs at once). So building the graph
means snapping each interchange point onto the nearest highway line, sorting the interchanges
along that line, and cutting the line into segments between consecutive ones (a classic GIS
"linear referencing" operation).

```bash
# 1) Download the N06 highway dataset (nationwide) into 03X_input/, clip to Shiga Prefecture,
#    and cut it into an interchange-level graph (nodes.csv / edges.csv)
python3.12 031_generateHighwayNetwork.py

# 2) Analyze — writes 03X_output/vertex_metrics.csv
python3.12 032_highway_analysis.py

# 2b) Same as above, but split the output: print/show -> out.txt, Spark logs -> spark.log
python3.12 032_highway_analysis.py > out.txt 2> spark.log

# 3) Visualize before/after into 03X_output/highway_before_after.png
python3.12 033_visualize.py
```

Nodes are interchanges/junctions (official names like 米原JCT, 草津JCT), edges are the highway
segments between them. PageRank picks out the junctions where multiple expressways meet.

N06 only covers expressways, so on its own the picture looks sparse next to Patterns 2/3.
To make it comparable, the visualization step draws Shiga's **other major roads** (national /
main prefectural, from OSM — the same `motorway|trunk|primary|secondary` filter as Pattern 3) as a
light-gray **background layer**, with the government expressway graph drawn on top. The background
is context only — it is **not** part of the graph that `PageRank` / `connectedComponents` run on.
If `osmnx` is unavailable (or offline), the background is skipped and the highway graph is drawn alone.
The background download is cached in `03X_input/bg_roads.graphml`; if Pattern 3 has already been run,
its `02X_input/road.graphml` is reused instead so nothing is downloaded twice.

## Pattern 5 (110番台) — a government road-mesh statistic turned into a graph

A completely different kind of source: MLIT's (国土交通省)
**道路密度・道路延長メッシュデータ (N04)** from 国土数値情報 (National Land Numerical Information).

This is not a road network — it's a table of statistics (road length, road density)
attached to each 1km grid cell (3次メッシュ), with no concept of nodes/edges at all. So the graph itself
has to be defined: each 1km mesh cell **that actually has a road** becomes a node, and cells that share a
border (up/down/left/right) become edges — a grid graph covering Shiga Prefecture.

```bash
# 1) Download the N04 mesh (4 tiles covering Shiga) into 11X_input/, clip to the prefecture,
#    and build the grid graph (nodes.csv / edges.csv)
python3.12 111_generateRoadMeshNetwork.py

# 2) Analyze — writes 11X_output/vertex_metrics.csv
python3.12 112_road_analysis.py

# 2b) Same as above, but split the output: print/show -> out.txt, Spark logs -> spark.log
python3.12 112_road_analysis.py > out.txt 2> spark.log

# 3) Visualize before/after into 11X_output/road_mesh_before_after.png
python3.12 113_visualize.py
```

Because the source data already carries a "road density" statistic per cell, the **before** picture colors
each mesh cell by that raw MLIT value (no graph analysis yet), while the **after** picture shows PageRank
computed on the grid graph — the cells embedded in the largest, most connected mass of road-bearing mesh
stand out, and disconnected mesh "islands" fall out of `connectedComponents` just like the isolated road
segments in Patterns 2/3.

## Folder naming

- `00X_input` / `00X_output` — input and output for pattern 1.
- `01X_input` / `01X_output` — input and output for pattern 2.
- `02X_input` / `02X_output` — input and output for pattern 3.
- `03X_input` / `03X_output` — input and output for pattern 4.
- `11X_input` / `11X_output` — input and output for pattern 5.
- All folders are generated by the scripts, so they are not tracked in git.
