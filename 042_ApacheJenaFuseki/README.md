# build and run
```bash
docker compose up -d
```

# How to use
## Web UI
* Fuseki Admin : http://localhost:3030
  * user     : admin
  * password : password

## python
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install SPARQLWrapper
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
