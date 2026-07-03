# sample13_Mlib — MLlib（機械学習）

Sparkの4大コンポーネントのひとつ **MLlib**。
`Transformer` / `Estimator` / `Pipeline` という共通APIで、前処理〜学習〜評価を組み立てます。

| ファイル | 内容 |
|---|---|
| `01_generateDummyTaxiData.py` | 学習用のダミータクシーデータ(2000件)を生成。分類に効くよう「距離が長いほど Card」の弱い相関付き |
| `02_regression.py` | **回帰** — `tripDistance` などから `totalAmount` を予測（LinearRegression、RMSE / R2 で評価） |
| `03_classification.py` | **分類** — 支払いが Card か否かを予測（StringIndexer → OneHotEncoder → LogisticRegression、Accuracy / F1） |

## 実行

```bash
# まず学習データを生成
python3.12 01_generateDummyTaxiData.py

# 回帰
python3.12 02_regression.py

# 分類
python3.12 03_classification.py
```

> MLlib は追加パッケージ不要で、`pyspark` だけで動きます（環境構築はリポジトリ直下の [README.md](../README.md) 参照）。

## ポイント

- **Pipeline**：`VectorAssembler` などの前処理と推定器を一列に並べ、`fit`/`transform` を一括で扱う。
- **特徴量ベクトル**：Spark ML は「複数列」ではなく `features` という1本のベクトル列を入力に取る。`VectorAssembler` がその変換を担う。
- **カテゴリ変換**：文字列カテゴリは `StringIndexer`（数値化）→ `OneHotEncoder`（ベクトル化）の2段で扱う。
