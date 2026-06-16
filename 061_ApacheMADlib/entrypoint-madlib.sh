#!/bin/bash
set -e

# Install the MADlib schema once, after PostgreSQL accepts TCP connections.
# Runs in the background so we can hand PID 1 to the stock postgres entrypoint.
(
    export PGPASSWORD="${POSTGRES_PASSWORD}"
    until pg_isready -h localhost -U "${POSTGRES_USER}" -q 2>/dev/null; do
        sleep 2
    done
    sleep 2  # small grace once the socket is up

    already=$(psql -h localhost -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc \
        "SELECT 1 FROM pg_namespace WHERE nspname='madlib'" 2>/dev/null || true)
    if [ "$already" != "1" ]; then
        echo "[madlib-init] installing MADlib schema..."
        gosu postgres env PGPASSWORD="${POSTGRES_PASSWORD}" \
            /usr/local/madlib/bin/madpack -s madlib -p postgres \
            -c "${POSTGRES_USER}@localhost:5432/${POSTGRES_DB}" install \
            && echo "[madlib-init] MADlib install complete." \
            || echo "[madlib-init] MADlib install FAILED."
    fi
) &

exec docker-entrypoint.sh "$@"
