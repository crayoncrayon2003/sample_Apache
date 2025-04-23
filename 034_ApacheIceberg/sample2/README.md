# pre process
```
./00_mkdir.sh
```

# build and run
```
docker compose up -d
```

# Setting up
Setting up PostgreSQL / MinIO / Trino
```
python 01_setup.py
```

# GUI
## MinIO
MinIO is object storage that Amazon S3 compatible.
* http://localhost:9001
* user : admin
* pass : password

Iceberg data is stored in a bucket named warehouse.

## Spark
http://localhost:8080
http://localhost:8888

New -> python3(ipykernel) -> 


## Create catalog
```
!pip install --upgrade pip
!pip install --upgrade pyiceberg
```

## Create catalog
```
from pyiceberg.catalog.rest import RestCatalog

catalog = RestCatalog(
    name="iceberg",
    uri="http://iceberg-rest:8181",
    warehouse="s3://warehouse/"
)
```

## Create namespace
```
from pyiceberg.catalog import Identifier

namespaces = catalog.list_namespaces()

namespaces_identifier = "default"

if (namespaces_identifier,) in namespaces:
    print("namespace is exist")
else:
    catalog.create_namespace((namespaces_identifier,))
    print("create namespace")
```

## Confirm namespace
```
catalog.list_namespaces()
```

## Create Table
```
from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import LongType, StringType, TimestampType

table_identifier = ("default", "sample_table")

schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="name", field_type=StringType(), required=True),
    NestedField(field_id=3, name="created_at", field_type=TimestampType(), required=True),
)

catalog.create_table(table_identifier, schema)

```
## Confirm Table
```
print(catalog.list_tables("default"))
```

## Insert data
```
from pyiceberg.io.pyarrow import write_table
import pyarrow as pa
import datetime

data = pa.Table.from_pydict({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "created_at": [datetime.datetime.now()] * 3
})

write_table(data, catalog.load_table(("default", "sample_table")))
```

# down
```
docker compose down
```

# post process
```
./99_rmdir.sh
```

