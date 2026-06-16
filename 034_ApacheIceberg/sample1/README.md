# ref
* https://iceberg.apache.org/spark-quickstart/#docker-compose

# build and run
```bash
docker compose up -d
```

# GUI
## MinIO
MinIO is object storage that Amazon S3 compatible.
* http://localhost:9001
* user : admin
* pass : password

Object Browser -> iceberg-bucket -> Upload  -> upload ./data/data.csv


## Spark
Master
http://localhost:8080

Jupiter
http://localhost:8888

Iceberg - Getting Started.ipynb

# down
```bash
docker compose down
```

# post process
```bash
./99_rmdir.sh
```

