#!/bin/bash
# Create the host directories Airflow bind-mounts and generate an .env so the
# containers write files as your user (AIRFLOW_UID), not root.
cd "$(dirname "$0")"
mkdir -p ./airflow-dags ./airflow-logs ./config ./plugins
cat > .env <<EOF
AIRFLOW_UID=$(id -u)
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
EOF
echo "Created dirs and .env (AIRFLOW_UID=$(id -u))"
