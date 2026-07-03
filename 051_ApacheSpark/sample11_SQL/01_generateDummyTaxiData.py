import pandas as pd
from datetime import datetime, timedelta
import random
import os
random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT,"DummyTaxiData.csv")
DUMMY_TYPEDATA = os.path.join(ROOT,"DummyPaymentType.csv")

TYPES = ['Cash', 'Card', 'Voucher', 'Other']

def generateDummyPaymentType():
    data = []
    for type in TYPES:
        data.append([
            type,
        ])
    columns = ["type"]
    df = pd.DataFrame(data, columns=columns)
    return df

def generateDummyTaxiData(records):
    data = []
    for _ in range(records):
        pickupDateTime = datetime(2024, 1, 1, 0, 0) + timedelta(days=random.randint(0, 30))
        dropoffDateTime= pickupDateTime + timedelta(minutes=random.randint(5, 60))
        pickupDateTime = pickupDateTime.strftime("%Y-%m-%d %H:%M:%S")
        dropoffDateTime= dropoffDateTime.strftime("%Y-%m-%d %H:%M:%S")
        passengerCount = random.randint(1, 6)
        tripDistance = round(random.uniform(0.5, 20.0), 2)
        paymentType = random.choice(TYPES)
        totalAmount = round(tripDistance * random.uniform(2.5, 3.0) + random.uniform(2.5, 10.0), 2)

        data.append([
            pickupDateTime,
            dropoffDateTime,
            passengerCount,
            tripDistance,
            paymentType,
            totalAmount
        ])

    columns = ["pickupDateTime", "dropoffDateTime", "passengerCount", "tripDistance", "paymentType", "totalAmount"]
    df = pd.DataFrame(data, columns=columns)
    return df

def main():
    dummyTaxiData = generateDummyTaxiData(10)
    print(dummyTaxiData.head())

    dummyPaymentType = generateDummyPaymentType()
    print(dummyPaymentType.head())

    dummyTaxiData.to_csv(DUMMY_TAXIDATA, index=False)
    dummyPaymentType.to_csv(DUMMY_TYPEDATA, index=False)


if __name__ == '__main__':
    main()