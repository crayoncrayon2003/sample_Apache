# pre process
```
./00_mkdir.sh
```

# build and run
```
docker compose up -d
```

# How to user
## CLI
```
docker exec -it cassandra cqlsh
```

## CLI
```
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install cassandra-driver
```

# down
```
docker compose down
```

# post process
```
./00_mkdir.sh
```

