
# make dir
```bash
/00_mkdir.sh
```

# build and run
```bash
sudo docker compose up -d
```
wait for 5 minutes.

Access the following URL using the Web browser.
```bash
http://localhost:8080/nifi/
```

# control using python
```bash
pip install nipyapi
```

# down
```bash
docker compose down
```

# post process
```bash
./99_rmdir.sh
```