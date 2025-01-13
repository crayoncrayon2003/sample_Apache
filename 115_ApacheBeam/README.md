# Creating Virtual Environment
```
$ python -m venv env
$ source env/bin/activate
(env) $ pip install --upgrade pip setuptools
(env) $ pip install -r requirements.txt
```

# Install
## Install without Runner
```
(env) $ pip install apache-beam
```

## Install with Runner
```
(env) $ pip install apache-beam[gcp]
(env) $ pip install apache-beam[spark,flink]
```

# Run
```

```

# Deactivate Virtual Environment
```
(env) $ deactivate
```

# Remove Virtual Environment
```
$ rm -rf env
```