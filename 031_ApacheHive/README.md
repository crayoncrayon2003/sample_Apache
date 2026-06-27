# install
```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev libsasl2-dev libsasl2-2 libsasl2-modules-gssapi-mit
python3.12 -m pip install -U psutil
python3.12 -m pip install pyhive
python3.12 -m pip install thrift thrift-sasl
python3.12 -m pip install pandas sqlalchemy
```

# mkdir
```bash
mkdir -p ./hdfs/namenode ./hdfs/datanode ./metastore-postgresql/postgresql/data
```

# build and run
```bash
docker compose up -d
```

Access the NameNode UI using the Web browser (Hadoop 2.7 uses port 50070, not 9870).
```bash
http://localhost:50070
```

# run sample
```bash
python3.12 sample.py 
```

# down
```bash
docker compose down
```
