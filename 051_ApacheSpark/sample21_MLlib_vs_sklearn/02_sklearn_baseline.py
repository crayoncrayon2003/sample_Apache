# =============================================================
#  ベースライン: scikit-learn（単一マシン・全件インメモリ）
#
#  parquet を pandas で「全件メモリに」読み込み、LinearRegression を学習する。
#  - 小データでは Spark 起動コストが無いぶん高速。
#  - データが大きくなると Python プロセスのメモリ(RSS)が急増し、
#    やがて MemoryError（=単一マシンの限界）に達する。
#
#  末尾に機械可読な SUMMARY 行を出力する（04_compare.py が集計する）:
#    SUMMARY,sklearn,<rows>,<load_s>,<fit_s>,<total_s>,<peakRSS_MB>,<r2>
#
#    python3.12 02_sklearn_baseline.py --data data/rows_1000000.parquet
# =============================================================
import argparse
import resource
import time

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

FEATURES = ["tripDistance", "passengerCount", "durationMin"]
LABEL = "totalAmount"


def peak_rss_mb():
    # Linux では ru_maxrss は KB 単位。プロセスのピーク常駐メモリ。
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="入力parquetパス")
    args = parser.parse_args()

    # ---- 全件ロード（ここが単一マシンのメモリを圧迫する） ----
    t0 = time.perf_counter()
    try:
        pdf = pd.read_parquet(args.data)
    except MemoryError:
        print("SUMMARY,sklearn,NA,NA,NA,NA,NA,OOM_on_load")
        return
    load_s = time.perf_counter() - t0
    rows = len(pdf)

    X = pdf[FEATURES].values
    y = pdf[LABEL].values
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    # ---- 学習 ----
    t1 = time.perf_counter()
    try:
        model = LinearRegression().fit(X_tr, y_tr)
    except MemoryError:
        print("SUMMARY,sklearn,{0},{1:.3f},NA,NA,{2:.1f},OOM_on_fit".format(rows, load_s, peak_rss_mb()))
        return
    fit_s = time.perf_counter() - t1

    r2 = r2_score(y_te, model.predict(X_te))
    total_s = load_s + fit_s

    print("====  scikit-learn  ====")
    print("rows       = {0:,}".format(rows))
    print("coef       = {0}".format(model.coef_))
    print("intercept  = {0:.4f}".format(model.intercept_))
    print("load  time = {0:.3f}s".format(load_s))
    print("fit   time = {0:.3f}s".format(fit_s))
    print("total time = {0:.3f}s".format(total_s))
    print("peak  RSS  = {0:.1f} MB".format(peak_rss_mb()))
    print("R2         = {0:.4f}".format(r2))
    print("SUMMARY,sklearn,{0},{1:.3f},{2:.3f},{3:.3f},{4:.1f},{5:.4f}".format(
        rows, load_s, fit_s, total_s, peak_rss_mb(), r2))


if __name__ == "__main__":
    main()
