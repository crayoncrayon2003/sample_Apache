# 実行

```bash
# 単発で確認
python3.12 01_generate_scalable_data.py --rows 1000000
python3.12 02_sklearn_baseline.py --data data/rows_1000000.parquet
python3.12 03_pyspark_mllib.py --data data/rows_1000000.parquet

# 規模を変えて一括比較（本命）
python3.12 04_compare.py --sizes 10000 100000 1000000 10000000
```

