# prepare
```
curl -LfO https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml
mkdir -p ./config ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

# build and run
wait for 5 minutes.
```
docker compose up airflow-init
```

```
docker compose up -d
```

wait for 5 minutes.
Access the following URL using the Web browser.
```
http://localhost:8080
```

account  : airflow
password : airflow

# down
```
docker compose down
```

# reference
* https://airflow.apache.org/docs/docker-stack/index.html
* https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
