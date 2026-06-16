# about
Apache Flink is a stream-processing engine. This sample computes streaming
statistics (count / average / standard deviation per device) with the Table API,
the same foundation Flink ML builds on.

# build and run (Flink cluster)
```bash
docker compose up -d
```
* Flink Web UI : http://localhost:8081

# run the job
## option A: submit to the cluster
```bash
docker exec -it flink-jobmanager ./bin/flink run -py /opt/sample1.py
```
(mount or `docker cp sample1.py flink-jobmanager:/opt/sample1.py` first)

## option B: run locally with PyFlink
### Create Virtual Environment
```bash
python3.12 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install apache-flink
```

### test
```bash
python sample1.py
```

### Deactivate Virtual Environment
```bash
(env) $ deactivate
```


# down
```bash
docker compose down
```

