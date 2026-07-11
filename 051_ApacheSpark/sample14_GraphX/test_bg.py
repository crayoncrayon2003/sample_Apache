# 033 の load_background_roads 内の線分生成ロジックだけを抜き出して検証（外部依存なし）
class FakeGeom:
    def __init__(self, xs, ys): self._xy = (xs, ys)
    @property
    def xy(self): return self._xy

class FakeGraph:
    def __init__(self): self.nodes = {}; self._edges = []
    def add_node(self, n, x, y): self.nodes[n] = {"x": x, "y": y}
    def add_edge(self, u, v, geometry=None): self._edges.append((u, v, {"geometry": geometry}))
    def edges(self, data=True): return self._edges

def build_segments(g, scale):
    segments = []
    for u, v, d in g.edges(data=True):
        geom = d.get("geometry")
        if geom is not None:
            segments.append([(x * scale, y) for x, y in zip(*geom.xy)])
        else:
            segments.append([
                (float(g.nodes[u]["x"]) * scale, float(g.nodes[u]["y"])),
                (float(g.nodes[v]["x"]) * scale, float(g.nodes[v]["y"])),
            ])
    return segments

g = FakeGraph()
g.add_node(1, x=136.0, y=35.0)      # 文字列座標も来うるので str も混ぜる
g.add_node(2, x="136.5", y="35.2")
g.add_edge(1, 2, geometry=None)                                   # 直線辺
g.add_edge(1, 2, geometry=FakeGeom([136.0, 136.2, 136.5], [35.0, 35.1, 35.2]))  # 曲線辺

scale = 0.8  # cos(緯度) 相当
segs = build_segments(g, scale)
assert len(segs) == 2, segs
# 直線辺: 両端2点、lon に scale 適用
assert segs[0] == [(136.0*0.8, 35.0), (136.5*0.8, 35.2)], segs[0]
# 曲線辺: 折れ線3点
assert segs[1] == [(136.0*0.8,35.0),(136.2*0.8,35.1),(136.5*0.8,35.2)], segs[1]
print("segment-building logic OK:", segs)
