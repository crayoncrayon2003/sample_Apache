#!/usr/bin/env bash
# =============================================================
#  Run the Spark Declarative Pipeline with the 4系 venv (env412).
#
#  spark-pipelines is a CLI, so it can't self-correct like the python samples.
#  This wrapper pins SPARK_HOME to env412's own bundled pyspark and the driver
#  to env412's python, so a stale shell SPARK_HOME (e.g. /opt/spark-4-1-2 with a
#  python that lacks pyarrow) can't break the run. No activate / export needed:
#
#      ./run.sh              # runs transformations/ via spark-pipeline.yml
#      ./run.sh --dry-run    # extra args are passed through to spark-pipelines
# =============================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$HERE/../env412/bin/python"   # 4系 venv at the repo root

if [ ! -x "$PY" ]; then
  echo "env412 not found at $PY" >&2
  echo "Create it first:  python3.12 -m venv env412 && env412/bin/pip install -r requirements-4.1.2.txt" >&2
  exit 1
fi

# SPARK_HOME = the venv's own pyspark (has spark-pipelines + matching Spark 4.1.2 jars)
SPARK_HOME="$("$PY" -c 'import os, pyspark; print(os.path.dirname(pyspark.__file__))')"
export SPARK_HOME
export PYSPARK_PYTHON="$PY"
export PYSPARK_DRIVER_PYTHON="$PY"

cd "$HERE"

# Generate the dummy data on first run so the pipeline has an input to read.
if [ ! -f 00_input/DummyTaxiData.csv ]; then
  "$PY" 01_generateDummyTaxiData.py
fi

exec "$SPARK_HOME/bin/spark-pipelines" run --spec spark-pipeline.yml "$@"
