# run

```bash
# 1) グラフデータを生成
python3.12 01_generateGraphData.py

# 2) 解析（必ず --packages を付けて spark-submit で実行）
spark-submit --packages graphframes:graphframes:0.8.4-spark3.5-s_2.12 02_graph_analysis.py
```