# ref
https://streampipes.apache.org/download/

# Install
```
pip install requests
pip install fastapi uvicorn
```

# build and run
```
docker compose up -d
```
# How to user
Access the following URL using the Web browser.
* http://localhost:80
* user : admin@streampipes.apache.org
* pass : admin

# Setting Adapter
Home -> Connect -> New Adapter -> ISS Location

# Setting Pipelines
Home -> Pipelines & Functions -> New Pipeline

* Data Streams    : ISS Location
* Data Processors : Geo City Name Reverse Decoder


# down
```
docker compose down
```

