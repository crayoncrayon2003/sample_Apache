# install
```bash
python3.12 -m pip install ray==2.40.0 grpcio
```
* The Ray version on the host must match the cluster image (`rayproject/ray:2.40.0-py312`),
  and the host Python minor version must be 3.12.

# build
```bash
docker compose up -d
```

# run
```bash
python3.12 11_sample1.py
```


# down
```bash
docker compose down
```
