from monitor import Monitor
import csv
from datetime import datetime
from collections import defaultdict

mon = Monitor()
mon.start()

count_by_type = defaultdict(int)
sum_by_type = defaultdict(float)

chunk_size = 100000
processed = 0

with open("DummyTaxiData.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        dt = datetime.strptime(row["pickupDateTime"], "%Y-%m-%d %H:%M:%S")
        if datetime(2024,1,1) <= dt < datetime(2024,4,30):
            ptype = row["paymentType"]
            count_by_type[ptype] += 1
            sum_by_type[ptype] += float(row["totalAmount"])

        processed += 1
        if processed % chunk_size == 0:
            mon.sample()

elapsed, mem = mon.stop()
print("FOR  elapsed={:.2f}s  peak_mem={:.1f}MB".format(elapsed, mem))
print("Results:", dict(count_by_type))