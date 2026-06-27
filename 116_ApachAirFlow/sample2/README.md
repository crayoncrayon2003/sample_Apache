# about
Apache Airflow 3 cluster (CeleryExecutor) based on the official docker-compose:
postgres + redis + apiserver + scheduler + dag-processor + worker + triggerer.
Sample DAGs live in `./airflow-dags`.

# make dir
Creates the bind-mount dirs and an `.env` (sets AIRFLOW_UID + admin/admin):
```bash
./00_mkdir.sh
```

# build and run
```bash
docker compose up -d
```
The first start runs `airflow-init` (DB migrate + create admin user); wait until
it has exited with code 0, then the other services become healthy.

# How to use
http://localhost:8080
* Username: admin
* Password: admin

The DAGs (`hello_airflow`, `sample2`, `sample3`, `sample4_etl`) are paused by
default — toggle them on in the UI, or:
```bash
docker compose exec airflow-scheduler airflow dags unpause hello_airflow
docker compose exec airflow-scheduler airflow dags trigger  hello_airflow
```

# down
```bash
docker compose down        # keep the database
docker compose down -v     # also remove the Postgres named volume
```

# post process
Remove runtime files (logs/config/plugins). DAGs are kept:
```bash
./99_rmdir.sh
```
