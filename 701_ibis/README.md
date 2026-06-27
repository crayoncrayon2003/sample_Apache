# install
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install ibis ibis-framework[duckdb]
pip install pyarrow
pip install pyspark
pip install ibis ibis-framework[postgres]
pip install ibis ibis-framework[mysql]
```