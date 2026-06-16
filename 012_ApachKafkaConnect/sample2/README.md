# Creat jar file
## Custom Sink Connector
```bash
cd kafka-custom-connector-sink
mvn clean install
```
copy jar file 
* form : ./kafka-custom-connector-sink/target/kafka-custom-sink-connector-1.0-SNAPSHOT.jar
* to   : ./kafka-custom-connector/kafka-custom-sink-connector-1.0-SNAPSHOT.jar

## Custom Source Connector
```bash
cd kafka-custom-connector-source
mvn clean install
```
copy jar file 
* form : ./kafka-custom-connector-sink/target/kafka-custom-source-connector-1.0-SNAPSHOT.jar
* to   : ./kafka-custom-connector/kafka-custom-source-connector-1.0-SNAPSHOT.jar

## Custom Transform
```bash
cd kafka-custom-transforms
mvn clean install
```
copy jar file 
* form : ./kafka-custom-connector-sink/target/kafka-custom-transform-1.0-SNAPSHOT.jar
* to   : ./kafka-custom-connector/kafka-custom-transform-1.0-SNAPSHOT.jar

# build and run
```bash
docker compose up -d
```

# check 
## check jar file
```bash
docker exec -it kafka-connect ls /usr/share/confluent-hub-components/custom-connectors
> kafka-custom-sink-connector-1.0-SNAPSHOT.jar
> kafka-custom-source-connector-1.0-SNAPSHOT.jar
> kafka-custom-transform-1.0-SNAPSHOT.jar
```

## check path
```bash
docker exec -it kafka-connect printenv | grep CONNECT_PLUGIN_PATH
> CONNECT_PLUGIN_PATH=/usr/share/confluent-hub-components
```

# Experiment
## Preparation
```bash
python3.12 step01_SinkServer.py 
python3.12 step02_SourceServer.py
```

### start
```bash
python3.12 step11_StartHTTPSinkConnector.py
python3.12 step12_StartHTTPSourceConnector.py 
```

### stop
```bash
python3.12 step13_StartHTTPSinkConnector.py
python3.12 step14_StartHTTPSourceConnector.py 
```


# down
```bash
docker compose down
```
