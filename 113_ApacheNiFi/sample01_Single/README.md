
# make dir
```
mkdir -p ./nifi/fileprocessor ./nifi/database ./nifi/flow_storage
```

# build and run
```
sudo docker-compose up -d
```
wait for 5 minutes.

Access the following URL using the Web browser.
```
http://localhost:8080/nifi/
```

# control using python
```
pip install nipyapi
```

# down
```
docker compose down
```