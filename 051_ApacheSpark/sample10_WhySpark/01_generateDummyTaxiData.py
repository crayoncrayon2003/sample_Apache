import pandas as pd
from datetime import datetime, timedelta
import random
import os
import string

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

TYPES = ['Cash', 'Card', 'Voucher', 'Other']

def rand_str(n):
    return ''.join(random.choices(string.ascii_letters, k=n))

def generateDummyTaxiData(records, use_batch=True, batch_size=100000):
    """
    ダミーデータ生成

    Args:
        records: 生成するレコード数
        use_batch: バッチ処理を使用するか（大量データ向け）
        batch_size: バッチサイズ
    """

    columns = [
        "pickupDateTime", "dropoffDateTime", "passengerCount",
        "tripDistance", "paymentType", "totalAmount"
    ]
    columns += [f"metric_{i:02d}" for i in range(1, 11)]
    columns += [f"category_{i:02d}" for i in range(1, 6)]
    columns += [f"comment_{i:02d}" for i in range(1, 6)]
    columns += [f"optional_{i:02d}" for i in range(1, 6)]

    if not use_batch or records < batch_size:
        # 小規模データ: 一括生成
        print(f"一括生成モード: {records:,} records")
        return _generate_all_at_once(records, columns)
    else:
        # 大規模データ: バッチ生成
        print(f"バッチ生成モード: {records:,} records (batch: {batch_size:,})")
        return _generate_in_batches(records, batch_size, columns)

def _generate_all_at_once(records, columns):
    """一括でデータを生成（メモリに全て載せる）"""
    data = []

    for i in range(records):
        if i % 100000 == 0 and i > 0:
            print(f"  進捗: {i:,} / {records:,} ({i/records*100:.1f}%)")

        row = _generate_single_row()
        data.append(row)

    return pd.DataFrame(data, columns=columns)

def _generate_in_batches(records, batch_size, columns):
    """バッチごとにデータを生成してファイルに追記"""
    # 最初にヘッダーだけ書き込む
    pd.DataFrame(columns=columns).to_csv(DUMMY_TAXIDATA, index=False)

    num_batches = (records + batch_size - 1) // batch_size

    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, records)
        current_batch_size = end_idx - start_idx

        print(f"  バッチ {batch_num + 1}/{num_batches}: {start_idx:,} - {end_idx:,}")

        # バッチ分のデータ生成
        batch_data = []
        for _ in range(current_batch_size):
            row = _generate_single_row()
            batch_data.append(row)

        # DataFrameに変換してファイルに追記
        batch_df = pd.DataFrame(batch_data, columns=columns)
        batch_df.to_csv(DUMMY_TAXIDATA, mode='a', header=False, index=False)

        # メモリ解放
        del batch_data
        del batch_df

    # ダミーのDataFrameを返す（互換性のため）
    return pd.DataFrame(columns=columns)

def _generate_single_row():
    """1行分のデータを生成"""
    pickup = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))
    dropoff = pickup + timedelta(minutes=random.randint(5, 60))

    row = [
        pickup.strftime("%Y-%m-%d %H:%M:%S"),
        dropoff.strftime("%Y-%m-%d %H:%M:%S"),
        random.randint(1, 6),
        round(random.uniform(0.5, 20.0), 2),
        random.choice(TYPES),
        round(random.uniform(10, 80), 2)
    ]

    # 数値ダミー 10列
    row.extend([random.random() for _ in range(10)])

    # 短文字列 5列
    row.extend([rand_str(10) for _ in range(5)])

    # 長文字列 5列（pandas殺し）
    row.extend([rand_str(200) for _ in range(5)])

    # NULL混在 5列
    for _ in range(5):
        if random.random() < 0.3:
            row.append(None)
        else:
            row.append(rand_str(20))

    return row

def main():
    # 生成するレコード数
    total_records = 5_000_000  # 5M records

    print("="*60)
    print("ダミータクシーデータ生成")
    print("="*60)

    # レコード数に応じて自動的にバッチ処理を選択
    use_batch = total_records >= 500000  # 50万件以上はバッチ処理

    if use_batch:
        # バッチ処理モード（ファイルに直接書き込み）
        generateDummyTaxiData(total_records, use_batch=True, batch_size=100000)
    else:
        # 一括生成モード
        df = generateDummyTaxiData(total_records, use_batch=False)
        print("CSVファイルに書き出し中...")
        df.to_csv(DUMMY_TAXIDATA, index=False)

    # ファイルサイズ表示
    file_size = os.path.getsize(DUMMY_TAXIDATA) / (1024 * 1024)
    print("="*60)
    print(f"✓ CSV生成完了")
    print(f"  ファイル: {DUMMY_TAXIDATA}")
    print(f"  レコード数: {total_records:,}")
    print(f"  ファイルサイズ: {file_size:.1f} MB")
    print("="*60)

if __name__ == "__main__":
    main()