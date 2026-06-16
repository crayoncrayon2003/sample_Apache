# Creating Virtual Environment
```bash
$ python -m venv env
$ source env/bin/activate
(env) $ pip install --upgrade pip setuptools
(env) $ pip install -r requirements.txt
```

# Install
## Install without Runner
```bash
(env) $ pip install apache-beam
```

## Install with Runner
```bash
(env) $ pip install apache-beam[gcp]
(env) $ pip install apache-beam[spark,flink]
```

# Run
```

```

# Deactivate Virtual Environment
```bash
(env) $ deactivate
```

# Remove Virtual Environment
```bash
$ rm -rf env
```