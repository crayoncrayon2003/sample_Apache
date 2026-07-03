# Apache Spark Samples

This is a sample of Apache Spark.

Apache Spark consists of four components.

+ Spark SQL
+ Spark Streaming
+ Spark MLlib
+ Spark GraphX


The steps below are the local setup (Java / Spark / Python venv).

# Java

## install

```bash
sudo apt update
sudo apt install openjdk-17-jdk wget tar -y
java -version
```

## Select Java version

```bash
sudo update-alternatives --config java
```

## Set path

open bashrc

```bash
vim ~/.bashrc
```

edit follow

```bash
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

enable bashrc

```bash
source ~/.bashrc
```

## confirm

```bash
java -version
> openjdk version "17.0.19" 2026-04-21
> OpenJDK Runtime Environment (build 17.0.19+10-1-24.04.2-Ubuntu)
> OpenJDK 64-Bit Server VM (build 17.0.19+10-1-24.04.2-Ubuntu, mixed mode, sharing)
```

## spark

### Install

check latest spark version. ref https://dlcdn.apache.org/spark/
folloing "spark-3-5-8"

```bash
wget https://dlcdn.apache.org/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz
sudo tar -xzf spark-3.5.8-bin-hadoop3.tgz -C /opt/
sudo mv /opt/spark-3.5.8-bin-hadoop3 /opt/spark-3-5-8
ls /opt/spark-3-5-8/bin/
```

## Set path

open bashrc

```bash
vim ~/.bashrc
```

edit follow

```
export SPARK_HOME=/opt/spark-3-5-8
export PATH=$SPARK_HOME/bin:$PATH
export PATH=$SPARK_HOME/sbin:$PATH
# export PYSPARK_PYTHON=/usr/bin/python3.9
# export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.9
export PYSPARK_PYTHON=/usr/bin/python3.12
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12
```

enable bashrc

```bash
source ~/.bashrc
```

## confirm

```bash
spark-shell --version
> version 3.5.8
spark-submit --version
> version 3.5.8
```

# python

## create venv & activate venv

```bash
python3.12 -m venv env
```

## activate venv

```bash
source env/bin/activate
```

## pip isntall

```bash
pip install --upgrade pip setuptools
pip install pyspark==3.5.8 py4j
```

## run

```bash
python3.12 filename.py
```

```bash
spark-submit filename.py
```

## deactivate venv

```bash
deactivate
```
