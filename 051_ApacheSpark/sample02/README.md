# make dir
```
mkdir -p ./data/master ./data/worker1 ./data/worker2
```

# build and run
```
docker compose up -d
```

Access the following URL using the Web browser.
```
http://localhost:8080/
```

# install
```
pip3 install pyspark==2.0.2 py4j
```

# down
```
docker compose down
```
