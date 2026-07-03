# =============================================================
#  MLlib 用のダミータクシーデータ生成
#
#  sample01/sample11 の生成器と同じ列構成だが、機械学習の学習に
#  足りる件数(2000件)を出力する。分類サンプル(03)で意味のある
#  結果が出るよう、支払い種別(paymentType)を「乗車距離が長いほど
#  Card になりやすい」という弱い相関を持たせて生成している。
# =============================================================
import pandas as pd
from datetime import datetime, timedelta
import random
import os

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT, "DummyTaxiData.csv")

TYPES = ['Cash', 'Card', 'Voucher', 'Other']


def choose_payment_type(trip_distance):
    """乗車距離が長いほど Card になりやすい重み付き抽選（分類に信号を持たせる）。"""
    card_weight = 1.0 + trip_distance / 5.0   # 距離が長いほど Card の重みが増える
    weights = {
        'Card': card_weight,
        'Cash': 2.0,
        'Voucher': 0.5,
        'Other': 0.3,
    }
    population = list(weights.keys())
    return random.choices(population, weights=[weights[p] for p in population], k=1)[0]


def generateDummyTaxiData(records):
    data = []
    for _ in range(records):
        pickupDateTime = datetime(2024, 1, 1, 0, 0) + timedelta(days=random.randint(0, 30))
        dropoffDateTime = pickupDateTime + timedelta(minutes=random.randint(5, 60))
        pickupDateTime = pickupDateTime.strftime("%Y-%m-%d %H:%M:%S")
        dropoffDateTime = dropoffDateTime.strftime("%Y-%m-%d %H:%M:%S")
        passengerCount = random.randint(1, 6)
        tripDistance = round(random.uniform(0.5, 20.0), 2)
        paymentType = choose_payment_type(tripDistance)
        totalAmount = round(tripDistance * random.uniform(2.5, 3.0) + random.uniform(2.5, 10.0), 2)

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
    dummyTaxiData = generateDummyTaxiData(2000)
    print(dummyTaxiData.head())
    dummyTaxiData.to_csv(DUMMY_TAXIDATA, index=False)
    print("wrote {0} rows -> {1}".format(len(dummyTaxiData), DUMMY_TAXIDATA))


if __name__ == '__main__':
    main()
