# pre process
```bash
./00_mkdir.sh
```

# build and run
```bash
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
```bash
SELECT * FROM dfs.`data/data.csv` LIMIT 10;
```

# down
```bash
docker compose down
```

# post process
```bash
./00_mkdir.sh
```

