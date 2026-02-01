from monitor import Monitor
import pandas as pd
from collections import defaultdict

mon = Monitor()
mon.start()

chunk_size = 500000
count_by_type = defaultdict(int)
sum_by_type = defaultdict(float)

for chunk in pd.read_csv("DummyTaxiData.csv", parse_dates=["pickupDateTime"], chunksize=chunk_size):
    mon.sample()

    # フィルタリング
    chunk_filtered = chunk[
        (chunk["pickupDateTime"] >= "2024-01-01") &
        (chunk["pickupDateTime"] <  "2024-04-30")
    ]

    # 集計
    result = (
        chunk_filtered.groupby("paymentType")
          .agg(count=("paymentType","count"),
               sales=("totalAmount","sum"))
    )

    for ptype, row in result.iterrows():
        count_by_type[ptype] += row['count']
        sum_by_type[ptype] += row['sales']

    mon.sample()

elapsed, mem = mon.stop()
print("PANDAS elapsed={:.2f}s  peak_mem={:.1f}MB".format(elapsed, mem))
print("Results:", dict(count_by_type))