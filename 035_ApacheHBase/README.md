# build and run
```bash
docker compose up -d
```

# How to use
## CLI
```bash
docker exec -it hbase hbase shell
```

## Web UI
* HBase Master : http://localhost:16010

## python
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install happybase
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
