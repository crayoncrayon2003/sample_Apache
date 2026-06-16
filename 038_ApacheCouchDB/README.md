# build and run
```bash
docker compose up -d
```

# How to use
## Web UI (Fauxton)
* http://localhost:5984/_utils
  * user     : admin
  * password : password

## python
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install couchdb
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
