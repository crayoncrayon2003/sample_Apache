# build and run
```bash
docker compose up -d --build
```
* Apache MADlib ships only as source, so the image is built from source on top of
  `postgres:15` (the first build takes a while). MADlib is installed into the
  `madlib` schema automatically on first start.

# How to use
## CLI
```bash
docker exec -it madlib psql -U postgres -c "SELECT madlib.version();"
```

## python
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install psycopg2-binary
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
