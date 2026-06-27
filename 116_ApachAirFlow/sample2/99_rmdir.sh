#!/bin/bash
# Remove runtime files (DAGs are kept). The Postgres data is in a named volume;
# remove it with: docker compose down -v
cd "$(dirname "$0")"
rm -rf ./airflow-logs ./config ./plugins
