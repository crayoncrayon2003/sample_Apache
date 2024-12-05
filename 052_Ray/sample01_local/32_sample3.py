import os
import ray
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
DUMMY_TAXIDATA = os.path.join(ROOT,"DummyTaxiData.csv")
DUMMY_TYPEDATA = os.path.join(ROOT,"DummyPaymentType.csv")

OUTPUT_CSVFILE  = os.path.join(ROOT,"result.csv")

# init ray
ray.init()

# read csv
@ray.remote
def read_csv(file_path):
    return pd.read_csv(file_path)

def main():
    # csv files
    csv_files = [DUMMY_TAXIDATA, DUMMY_TYPEDATA]

    # decentralized processing : read csv
    results = ray.get([read_csv.remote(file) for file in csv_files])

    print("show each result")
    for item in results:
        print(item.head())
        print("-------------")

    # combine results from
    df = pd.concat(results)

    print("show combine result")
    print(df.head())

    summary = df.describe()
    summary.to_csv(OUTPUT_CSVFILE)

if __name__ == "__main__":
    main()
