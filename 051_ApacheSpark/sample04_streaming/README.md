# make dir
```
mkdir -p ./data/master ./data/worker1 ./data/worker2
```

# install
```
sudo apt-get update
sudo apt-get install python3-pip python3-dev openjdk-8-jdk build-essential
python3.12 -m pip install pyspark==3.5.3 py4j kafka-python kafka-python-ng kafka-utils six>=1.16.0

```


# build
```
docker compose up -d
```

Access the following URL using the Web browser.
```
http://localhost:8080/
```

# run
```
python3.12 filename.py
```


# down
```
docker compose down
```
