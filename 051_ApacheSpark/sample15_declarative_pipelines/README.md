# sample15_declarative_pipelines — Spark Declarative Pipelines (SDP)

**Spark Declarative Pipelines (SDP)** = Databricks の 
Lakeflow Declarative Pipelines(旧 Delta Live Tables）を OSS 化したもの。

テーブル/ビューを宣言するだけで依存関係(DAG)・実行順序・更新をエンジンが自動処理する宣言的 ETL。

**⚠️ 4系(env412)専用。** SDP は Spark 4.x のみの機能で、3系(env358)では動きません。

## 構成（bronze → silver → gold のメダリオン）

```
├── run.sh                        # 実行ラッパー
├── spark-pipeline.yml            # パイプライン spec
├── 01_generateDummyTaxiData.py   # ダミーデータ生成
└── transformations/
    ├── 01_bronze_ingest.py       # @sdp.materialized_view  取り込み
    ├── 02_silver_clean.py        # @sdp.materialized_view  クレンジング
    └── 03_gold_aggregate.py      # @sdp.materialized_view  月次集計
```

依存は各ファイルで `spark.read.table(...)` と書くだけ。順序は DAG から自動解決。

## 実行

```bash
./run.sh
```

初回はダミーデータ生成も自動、

SPARK_HOME/python を env412 に固定するので activate も export も不要）。

成功すると各フローが順に COMPLETED になり、結果テーブルが `spark-warehouse/` に作られる

## メモ

- 依存(初回のみ): `env412/bin/pip install -r ../requirements-4.1.2.txt`（`pyspark[connect]` / `pyyaml`）
- batch 源は `@sdp.materialized_view`、streaming 源は `@sdp.table`（要 `readStream`）
- 品質チェックは Python API に無い → SQL の `CONSTRAINT ... EXPECT` か、本サンプルは `.where()` で代替
