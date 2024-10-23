
# make dir
```
mkdir -p ./nifi0/fileprocessor ./nifi0/database ./nifi0/flow_storage
mkdir -p ./nifi1/fileprocessor ./nifi1/database ./nifi1/flow_storage
mkdir -p ./nifi2/fileprocessor ./nifi2/database ./nifi2/flow_storage
```

# build and run
```
sudo docker-compose up --scale nifi=3 -d
```
wait for 5 minutes.

check container
```
sudo docker ps -a
> d69cf139e38d   apache/nifi:latest ...  Up 8 seconds ...  nifi1
> 2f25451952b9   apache/nifi:latest ...  Up 8 seconds ...  nifi2
> f6ae93011bc6   apache/nifi:latest ...  Up 8 seconds ...  nifi3
```

Access the following URL using the Web browser.
* http://localhost:8080/nifi/
* http://localhost:8081/nifi/
* http://localhost:8082/nifi/


# down
```
docker compose down
```
