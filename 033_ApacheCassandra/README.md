# pre process
```bash
./00_mkdir.sh
```

# build and run
```bash
docker compose up -d
```

# How to user
## CLI
```bash
docker exec -it cassandra cqlsh
```

## CLI
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install cassandra-driver
```

# down
```bash
docker compose down
```

# post process
```bash
./00_mkdir.sh
```

