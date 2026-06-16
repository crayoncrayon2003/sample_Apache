# pre process
```bash
./00_mkdir.sh
```

# build and run
```bash
docker compose up -d
```
Access the following URL using the Web browser.
* apache/hop
    http://localhost:8083/
    account  : cluster
    password : cluster

* apache/hop-web
    http://localhost:8082/ui

# down
```bash
docker compose down
```

# post process
```bash
./00_mkdir.sh
```

# refarence
* https://qiita.com/Tadataka_Takahashi/items/b2eab05086ac6a449f3d
* https://qiita.com/Tadataka_Takahashi/items/f13161b981a8699f46ff
* https://hop.apache.org/tech-manual/latest/docker-container.html
