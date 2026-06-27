
# make dir
```bash
/00_mkdir.sh
```

# build and run
```bash
sudo docker compose up --scale nifi=3 -d
```
wait for 5 minutes.

check container
```bash
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
```bash
docker compose down
```

# post process
```bash
./99_rmdir.sh
```