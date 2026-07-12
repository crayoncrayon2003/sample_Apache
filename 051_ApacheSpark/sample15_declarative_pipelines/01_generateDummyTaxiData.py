# =============================================================
#  Spark Declarative Pipelines (SDP) : ダミーデータ生成
#
#  既存サンプル(sample11_SQL など)と同じタクシーデータを題材にする。
#  ここで作った CSV を bronze -> silver -> gold のメダリオン構成で
#  宣言的パイプライン(spark-pipelines run)が取り込む。
#
#  注意: このスクリプト自体は pandas だけで動く(Spark 不要)。
#        パイプライン本体(transformations/)は Spark 4.x が必要。
# =============================================================
import pandas as pd
from datetime import datetime, timedelta
import random
import os
random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(ROOT, "00_input")
DUMMY_TAXIDATA = os.path.join(INPUT_DIR, "DummyTaxiData.csv")
DUMMY_TYPEDATA = os.path.join(INPUT_DIR, "DummyPaymentType.csv")

TYPES = ['Cash', 'Card', 'Voucher', 'Other']


def generateDummyPaymentType():
    data = [[t] for t in TYPES]
    return pd.DataFrame(data, columns=["type"])


def generateDummyTaxiData(records):
    data = []
    for _ in range(records):
        pickupDateTime = datetime(2024, 1, 1, 0, 0) + timedelta(days=random.randint(0, 120))
        dropoffDateTime = pickupDateTime + timedelta(minutes=random.randint(5, 60))
        pickupDateTime = pickupDateTime.strftime("%Y-%m-%d %H:%M:%S")
        dropoffDateTime = dropoffDateTime.strftime("%Y-%m-%d %H:%M:%S")
        passengerCount = random.randint(0, 6)              # 0 を混ぜて silver の品質チェックで落とす
        tripDistance = round(random.uniform(0.5, 20.0), 2)
        paymentType = random.choice(TYPES)
        totalAmount = round(tripDistance * random.uniform(2.5, 3.0) + random.uniform(2.5, 10.0), 2)
        if random.random() < 0.1:
            totalAmount = -totalAmount                     # 一部を負値にして expectation で除外させる

        data.append([
            pickupDateTime,
            dropoffDateTime,
            passengerCount,
            tripDistance,
            paymentType,
            totalAmount,
        ])

    columns = ["pickupDateTime", "dropoffDateTime", "passengerCount", "tripDistance", "paymentType", "totalAmount"]
    return pd.DataFrame(data, columns=columns)


def main():
    dummyTaxiData = generateDummyTaxiData(200)
    print(dummyTaxiData.head())

    dummyPaymentType = generateDummyPaymentType()
    print(dummyPaymentType.head())

    os.makedirs(INPUT_DIR, exist_ok=True)
    dummyTaxiData.to_csv(DUMMY_TAXIDATA, index=False)
    dummyPaymentType.to_csv(DUMMY_TYPEDATA, index=False)
    print(f"wrote: {DUMMY_TAXIDATA}")
    print(f"wrote: {DUMMY_TYPEDATA}")


if __name__ == '__main__':
    main()
