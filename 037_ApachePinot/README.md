# build and run
```bash
docker compose up -d
```
* It takes a while for the QuickStart batch ingestion to finish loading the sample data.

# How to use
## Web UI
* Controller / Query Console : http://localhost:9000

## python
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install pinotdb
```

```bash
python sample1.py
```

# Deactivate Virtual Environment
```bash
(env) $ deactivate
```

# down
```bash
docker compose down
```
