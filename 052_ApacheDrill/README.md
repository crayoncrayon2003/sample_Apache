# pre process
```
./00_mkdir.sh
```

# build and run
```
docker compose up -d
```

# How to use
## GUI
Access the following URL using the Web browser.
* http://localhost:8047

## Setting: Storage
Storage -> dfs -> Storage -> Upload

```
{
  "type": "file",
  "connection": "file:///data",
  "workspaces": {
    "data": {
      "location": "/data",
      "writable": true,
      "defaultInputFormat": "csv",
      "allowAccessOutsideWorkspace": true
    }
  },
  "formats": {
    "csv": {
      "type": "text",
      "extensions": [
        "csv"
      ],
      "lineDelimiter": "\n",
      "fieldDelimiter": ",",
      "quote": "\"",
      "escape": "\"",
      "comment": "#"
    }
  },
  "authMode": "SHARED_USER",
  "enabled": true
}
```


## Setting: Query
```
SELECT * FROM dfs.`data/data.csv` LIMIT 10;
```

# down
```
docker compose down
```

# post process
```
./00_mkdir.sh
```

