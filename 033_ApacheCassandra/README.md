# pre process
```bash
./00_mkdir.sh
```

# build and run
```bash
docker compose up -d
```

# How to use
## CLI (cqlsh)
```bash
docker exec -it cassandra cqlsh
```

## Python client setup
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install cassandra-driver
```

# run sample
```bash
python3.12 sample1.py 
```

# down
```bash
docker compose down
```

# post process
```bash
./99_rmdir.sh
```

