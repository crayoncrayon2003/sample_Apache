# ref
https://github.com/apache/druid/


# build and run
```bash
docker compose up -d
```

Access the following URL using the Web browser.
* Druid Console
    http://localhost:8888

* SQL Endpoint (Broker)
	http://localhost:8082/druid/v2/sql

## python
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install happybase requests
```

# input data and run qury
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
