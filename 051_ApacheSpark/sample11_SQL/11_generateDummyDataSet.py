# =============================================================
#  Pattern 2 の入力データ生成
#
#  12_spark_sql.py が使う 10_input/ の3ファイルを生成する:
#    - data.csv  : CSV 入力（ヘッダ + 数行）
#    - data.json : スキーマ(fields)付き JSON 入力。null を含み、型(int/numeric/text)
#                  ごとの変換を確認できるように作ってある。
#    - query.sql : temp view "recode" に対して実行する変換SQL
#
#  パターン1の 01_generateDummyTaxiData.py と対になる位置づけ。
# =============================================================
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "10_input")

DATA_CSV  = os.path.join(INPUT_DIR, "data.csv")
DATA_JSON = os.path.join(INPUT_DIR, "data.json")
QUERY_SQL = os.path.join(INPUT_DIR, "query.sql")

# --- data.csv : key1/key2/key3 の単純な表 ---
CSV_CONTENT = "key1,key2,key3\n1,1,1\n2,2,2\n2,2,3\n"

# --- data.json : records（null を含む）＋ fields（スキーマ定義）---
JSON_CONTENT = {
    "data": {
        "records": [
            {"key1": None, "key2": 1,    "key3": "1"},
            {"key1": 2,    "key2": None, "key3": "2"},
            {"key1": 3,    "key2": 3,    "key3": None},
        ],
        "fields": [
            {"id": "key1", "type": "int"},
            {"id": "key2", "type": "numeric"},
            {"id": "key3", "type": "text"},
        ],
    }
}

# --- query.sql : recode ビューを NGSI-LD 風の構造に変換 ---
QUERY_CONTENT = """\
SELECT
    CONCAT('urn:ngsi-ld:', `key1`) AS id,
    'test' AS type,
    STRUCT(`key1` AS value, 'Text' AS type) AS data1,
    STRUCT(`key2` AS value, 'Text' AS type) AS data2,
    STRUCT(`key3` AS value, 'Text' AS type) AS data3
FROM recode;
"""


def main():
    os.makedirs(INPUT_DIR, exist_ok=True)

    with open(DATA_CSV, "w", encoding="utf-8", newline="") as f:
        f.write(CSV_CONTENT)

    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(JSON_CONTENT, f, ensure_ascii=False, indent=4)
        f.write("\n")

    with open(QUERY_SQL, "w", encoding="utf-8") as f:
        f.write(QUERY_CONTENT)

    print("generated into {0}:".format(INPUT_DIR))
    for p in (DATA_CSV, DATA_JSON, QUERY_SQL):
        print("  -", os.path.basename(p))


if __name__ == "__main__":
    main()
