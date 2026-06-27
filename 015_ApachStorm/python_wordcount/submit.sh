#!/usr/bin/env bash
# Build the topology jar and submit it to the running Storm cluster via Flux.
#
#   app.jar = flux-core-<ver>.jar + resources/wordcount.py + resources/storm.py
#
# The Python files must live INSIDE the jar (under resources/) so Storm ships
# them to the worker, where FluxShellBolt runs `python3 wordcount.py`.
set -euo pipefail
cd "$(dirname "$0")"

FLUX_VERSION=2.7.0          # match the storm:<ver> image in docker-compose
FLUX_JAR="flux-core-${FLUX_VERSION}.jar"
NIMBUS=nimbus              # container_name of the nimbus service

# 1. Fetch the Flux jar once (not committed to git; ~3.7 MB binary).
if [ ! -f "$FLUX_JAR" ]; then
  echo ">> downloading $FLUX_JAR"
  curl -fsSL -o "$FLUX_JAR" \
    "https://repo1.maven.org/maven2/org/apache/storm/flux-core/${FLUX_VERSION}/${FLUX_JAR}"
fi

# 2. Build app.jar on the host (a jar is a zip; the storm image ships only a
#    JRE, so we don't rely on a `jar` tool inside the container). The Python
#    files are added under resources/ so Storm extracts them on the worker.
echo ">> building app.jar"
cp -f "$FLUX_JAR" app.jar
zip -gq app.jar resources/storm.py resources/wordcount.py

# 3. Stage in nimbus and submit via Flux.
echo ">> staging files in $NIMBUS"
docker exec "$NIMBUS" rm -rf /topo
docker exec "$NIMBUS" mkdir -p /topo
docker cp app.jar       "$NIMBUS":/topo/app.jar
docker cp topology.yaml "$NIMBUS":/topo/topology.yaml

echo ">> submitting topology"
docker exec "$NIMBUS" storm jar /topo/app.jar org.apache.storm.flux.Flux /topo/topology.yaml

cat <<'EOF'

Submitted. Watch the Python bolt output in the worker log:
  docker exec supervisor sh -c 'tail -f $(ls -t /logs/workers-artifacts/*/*/worker.log | head -1)' | grep WORDCOUNT

List / kill:
  docker exec nimbus storm list
  ./kill.sh
EOF
