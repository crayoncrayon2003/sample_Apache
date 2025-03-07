# Java
## install

```
sudo apt update
sudo apt install openjdk-11-jdk wget tar -y
java -version
```

## Select Java version

```
sudo update-alternatives --config java
```

## Set path

open bashrc
```
sudo vim ~/.bashrc
```


edit follow
```
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```


enable bashrc
```
source ~/.bashrc
```

## confirm

```
java -version
> openjdk version "11.0.26" 2025-01-21
> OpenJDK Runtime Environment (build 11.0.26+4-post-Ubuntu-1ubuntu124.04)
> OpenJDK 64-Bit Server VM (build 11.0.26+4-post-Ubuntu-1ubuntu124.04, mixed mode, sharing)
```

## spark
### Install

```
wget https://dlcdn.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz
sudo mkdir -p /opt/spark-3-5-5
sudo tar -xvzf spark-3.5.5-bin-hadoop3.tgz -C /opt/spark-3-5-5 --strip-components=1
ls /opt/spark-3-5-5
```

## Set path

open bashrc
```
sudo vim ~/.bashrc
```


edit follow
```
export SPARK_HOME=/opt/spark-3-5-5
export PATH=$SPARK_HOME/bin:$PATH
export PATH=$SPARK_HOME/sbin:$PATH
export PYSPARK_PYTHON=/usr/bin/python3.12
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12
```


enable bashrc
```
source ~/.bashrc
```

## confirm
```
spark-shell --version
> version 3.5.5
spark-submit --version
> version 3.5.5
```

# python
## create venv & activate venv
```
python3.12 -m venv env
```

## activate venv
```
source env/bin/activate
```

## pip isntall
```
pip install --upgrade pip setuptools
pip install pyspark==3.5.5 py4j
```

## run
```
python3.12 filename.py
```

```
spark-submit filename.py
```

## deactivate venv
```
deactivate
```

