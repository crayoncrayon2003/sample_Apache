# make dir
```
mkdir -p ./data/master ./data/worker1 ./data/worker2
```

# install
```
sudo apt-get update
sudo apt-get install python3-pip python3-dev openjdk-8-jdk build-essential
python3.12 -m pip install pyspark py4j
```

# build and run
```
docker compose up -d
```

Access the following URL using the Web browser.
```
http://localhost:8080/
```

```
python3.12 sample.py
```


# down
```
docker compose down
```
