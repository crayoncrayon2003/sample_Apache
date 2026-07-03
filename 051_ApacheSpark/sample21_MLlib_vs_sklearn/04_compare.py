# =============================================================
#  比較オーケストレータ: 件数を増やしながら両者を実測して表にする
#
#  各データ規模ごとに 01(生成) → 02(sklearn) → 03(mllib) を
#  「別プロセス」で実行し、標準出力の SUMMARY 行を集計する。
#  別プロセスにするのは、sklearn が OOM で落ちても比較を続けられるようにし、
#  かつ各ランのピークメモリを独立に測るため。
#
#  出力例:
#    rows        sklearn_s   mllib_s   sklearn_MB   mllib_MB   winner
#    10,000      0.05        3.20      120.0        280.0      sklearn
#    1,000,000   2.10        4.80      1500.0       300.0      sklearn
#    10,000,000  OOM         9.50      OOM          320.0      mllib
#
#    python3.12 04_compare.py --sizes 10000 100000 1000000
# =============================================================
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable  # 実行中の python（venv 内の python3.12 を想定）


def run(script, extra_args):
    """スクリプトを別プロセスで実行し、SUMMARY 行を dict で返す。"""
    cmd = [PY, os.path.join(ROOT, script)] + extra_args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    summary = None
    for line in proc.stdout.splitlines():
        if line.startswith("SUMMARY,"):
            summary = line.strip().split(",")
    if summary is None:
        sys.stderr.write("[warn] no SUMMARY from {0}\n{1}\n".format(script, proc.stderr[-500:]))
    return summary


def parse(summary):
    # SUMMARY,<lib>,<rows>,<load_s>,<fit_s>,<total_s>,<peakRSS_MB>,<r2 or OOM_*>
    if summary is None:
        return {"total_s": "ERR", "mb": "ERR"}
    total_s = summary[5]
    mb = summary[6]
    r2 = summary[7]
    if r2.startswith("OOM"):
        return {"total_s": "OOM", "mb": "OOM"}
    return {"total_s": total_s, "mb": mb}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[10_000, 100_000, 1_000_000])
    args = parser.parse_args()

    rows_fmt = "{0:<14}{1:<14}{2:<12}{3:<14}{4:<12}{5}"
    print(rows_fmt.format("rows", "sklearn_s", "mllib_s", "sklearn_MB", "mllib_MB", "winner"))
    print("-" * 78)

    for n in args.sizes:
        data = os.path.join(ROOT, "data", "rows_{0}.parquet".format(n))
        run("01_generate_scalable_data.py", ["--rows", str(n), "--out", data])

        sk = parse(run("02_sklearn_baseline.py", ["--data", data]))
        ml = parse(run("03_pyspark_mllib.py", ["--data", data]))

        # 勝者判定（OOM/ERR は自動的に他方の勝ち）
        winner = "-"
        try:
            if sk["total_s"] in ("OOM", "ERR"):
                winner = "mllib"
            elif ml["total_s"] in ("OOM", "ERR"):
                winner = "sklearn"
            else:
                winner = "sklearn" if float(sk["total_s"]) <= float(ml["total_s"]) else "mllib"
        except ValueError:
            winner = "?"

        print(rows_fmt.format(
            "{0:,}".format(n), str(sk["total_s"]), str(ml["total_s"]),
            str(sk["mb"]), str(ml["mb"]), winner))

    print()
    print("読み方: 小さいうちは sklearn が速い（Spark起動コスト分）。")
    print("        件数が増えると sklearn_MB が膨張しやがて OOM、mllib は時間もメモリも安定。")
    print("        => これが『データ規模でSparkに乗り換えるメリット』の交差点。")


if __name__ == "__main__":
    main()
