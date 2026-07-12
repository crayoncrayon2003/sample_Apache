# sample02_cluster

Standalone Spark cluster (1 master + 2 workers) in Docker. The **cluster Spark
version must match the driver's pyspark version**, otherwise the job fails with a
version-mismatch error. Two compose files are provided:

| Cluster | compose file | image | driver venv |
| --- | --- | --- | --- |
| Spark 3系 | `docker-compose.yml` | `spark-py312:3.5.8` | `env358` |
| Spark 4系 | `docker-compose.4.1.2.yml` | `spark-py312:4.1.2` | `env412` |

Run only **one** of them at a time (they share ports 7077 / 8080).

# make dir

```bash
mkdir -p ./data/master ./data/worker1 ./data/worker2
```

# build and run

## Spark 3系 (3.5.8)

```bash
docker compose up -d
```

## Spark 4系 (4.1.2)

```bash
docker compose -f docker-compose.4.1.2.yml up -d
```

Access the following URL using the Web browser.

```bash
http://localhost:8080/
```

Run the driver with the **matching** venv (and `SPARK_HOME`):

```bash
# 3系: source env358/bin/activate  (use-spark3)
# 4系: source env412/bin/activate  (use-spark4)
python3.12 01_hello_sparkcluster.py
```

# down

```bash
# 3系
docker compose down

# 4系
docker compose -f docker-compose.4.1.2.yml down
```
