# install
```
sudo apt install build-essential libssl-dev libffi-dev python3-dev libsasl2-dev libsasl2-2 libsasl2-modules-gssapi-mit
python3.12 -m pip install -U psutil
python3.12 -m pip install pyhive
python3.12 -m pip install thrift thrift-sasl
python3.12 -m pip install pandas sqlalchemy
```

# mkdir
```
mkdir -p ./data/namenode ./data/datanode1 ./data/datanode2
```

# build and run
```
docker compose up -d
```

Access the following URL using the Web browser.
```
http://localhost:9870
```


# down
```
docker compose down
```
