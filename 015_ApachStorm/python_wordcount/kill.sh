#!/usr/bin/env bash
# Stop the topology (3s grace period for inflight tuples).
set -euo pipefail
docker exec nimbus storm kill python-wordcount -w 3
