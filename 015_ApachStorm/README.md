# build and run
```bash
docker compose up -d
```

This starts a minimal Storm cluster:
* **nimbus** – master; you submit topologies to it (`storm jar ...`).
* **supervisor** – worker; runs the actual spout/bolt tasks.
* **zookeeper** – cluster coordination.

Note: there is no Storm UI daemon, so `localhost:8080` does not serve a page.
Use the CLI (`docker exec nimbus storm list`) to inspect the cluster.

# Python sample (Flux + multilang)

Storm is JVM-native: you can't "connect a Python client" like Kafka/Pulsar —
you submit a *topology* that runs in the cluster. Python logic runs as a
multilang ShellBolt (stdin/stdout protocol), wired with Flux (YAML, no Java
build). See `python_wordcount/`:

```
python_wordcount/
  topology.yaml          # TestWordSpout (Java core) --word--> count-bolt (Python)
  resources/wordcount.py # the Python bolt (counts words)
  resources/storm.py     # vendored multilang protocol adapter
  submit.sh / kill.sh
```

Run it (cluster must be up):
```bash
cd python_wordcount
./submit.sh        # downloads flux-core jar, builds app.jar, submits via Flux
```

Watch the Python bolt output (multilang logs go to the worker log, not docker logs):
```bash
docker exec supervisor sh -c 'tail -f $(ls -t /logs/workers-artifacts/*/*/worker.log | head -1)' | grep WORDCOUNT
# WORDCOUNT mike = 58
# WORDCOUNT golda = 51
```

Stop it:
```bash
./kill.sh
```

# down
```bash
docker compose down
```


# reference
* https://storm.apache.org/releases/2.7.0/flux.html
* https://storm.apache.org/releases/2.7.0/Multilang-protocol.html
* https://streamparse.readthedocs.io/en/master/topologies.html