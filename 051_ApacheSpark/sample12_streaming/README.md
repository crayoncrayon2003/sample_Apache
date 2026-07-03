# make dir
```bash
mkdir -p ./data/master ./data/worker1 ./data/worker2
```
# build
```bash
docker compose up -d
```

Access the following URL using the Web browser.
```
http://localhost:8080/
```

# run

Each long-running script (02, 03, 11-21) needs its own terminal.

## step 1: create the topic
Run once.
```bash
python3.12 01_createtopic.py
```

## step 2: start the producer (keep it running)
Sends a message every few seconds. Leave this running for all the steps below.
```bash
python3.12 02_producer.py
```

## step 3: check with the plain Kafka consumer
Confirm the messages arrive, then stop this consumer (keep the producer running).
```bash
python3.12 03_consumer.py
```

## step 4-1
Run 11_readStream.py while 02_producer.py is running
```bash
python3.12 11_readStream.py
```

## step 4-2
Run 12_readStream.py while 02_producer.py is running
```bash
python3.12 12_readStream.py
```

## step 4-3
Run 13_readStream.py while 02_producer.py is running
```bash
python3.12 13_readStream.py
```

## step 4-4
Run 21_writeStream.py while 02_producer.py is running
```bash
python3.12 21_writeStream.py
```

# down
```
docker compose down
```
