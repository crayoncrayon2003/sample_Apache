### 分散推論（02 ↔ 03）

```bash
python3.12 01_generate_data.py --rows 5000000

python3.12 02_pytorch_only.py --data data/rows_5000000.parquet
python3.12 03_pyspark_pytorch_inference.py --data data/rows_5000000.parquet
```

### 分散学習（04）

```bash
# 単一ノード学習 と TorchDistributor 分散学習 を続けて実行して時間比較
python3.12 04_torch_distributor_train.py --rows 200000 --epochs 5 --procs 2
```
