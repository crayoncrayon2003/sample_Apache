# Apache Spark Samples

This is a sample of Apache Spark.

Apache Spark consists of four components.

+ Spark SQL
+ Spark Streaming
+ Spark MLlib
+ Spark GraphX

## Environments

This repository uses two Spark lines side by side. Java 17 is shared;
each line has its own Spark install and its own venv.

| Line          | Spark | Java | Python | venv     | requirements             |
| ------------- | ----- | ---- | ------ | -------- | ------------------------ |
| **Spark 3系** | 3.5.8 | 17   | 3.12   | `env358` | `requirements-3.5.8.txt` |
| **Spark 4系** | 4.1.2 | 17   | 3.12   | `env412` | `requirements-4.1.2.txt` |

**Rule:** always use a matching pair — `use-spark3` + `env358`, or `use-spark4` + `env412`.

---

## 1. Java

### install

```bash
sudo apt update
sudo apt install openjdk-17-jdk wget tar -y
java -version
```

If several JDKs are installed, check which one is the system default.

```bash
sudo update-alternatives --config java
```

### Set path

open bashrc

```bash
vim ~/.bashrc
```

edit follow

```bash
# ##############
# Java
# ##############
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

enable bashrc

```bash
source ~/.bashrc
```

### confirm

```bash
java -version
> openjdk version "17.0.19" 2026-04-21
> OpenJDK Runtime Environment (build 17.0.19+10-1-24.04.2-Ubuntu)
> OpenJDK 64-Bit Server VM (build 17.0.19+10-1-24.04.2-Ubuntu, mixed mode, sharing)
```

## 2. spark

### Install

check latest spark version. ref https://dlcdn.apache.org/spark/
folloing "spark-3-5-8"

```bash
# Spark 3系
wget https://dlcdn.apache.org/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz
sudo tar -xzf spark-3.5.8-bin-hadoop3.tgz -C /opt/
sudo mv /opt/spark-3.5.8-bin-hadoop3 /opt/spark-3-5-8

# Spark 4系
wget https://dlcdn.apache.org/spark/spark-4.1.2/spark-4.1.2-bin-hadoop3.tgz
sudo tar -xzf spark-4.1.2-bin-hadoop3.tgz -C /opt/
sudo mv /opt/spark-4.1.2-bin-hadoop3 /opt/spark-4-1-2
```

> `dlcdn.apache.org` hosts only current releases. If the download returns 404,
> use `https://archive.apache.org/dist/spark/` instead.

```bash
ls /opt/spark-3-5-8/bin/
ls /opt/spark-4-1-2/bin/
```

### Set path

open bashrc

```bash
vim ~/.bashrc
```

```
# ##############
# Spark
# ##############
# export SPARK_HOME=/opt/spark-3-5-8
# export PATH=$SPARK_HOME/bin:$PATH
# export PATH=$SPARK_HOME/sbin:$PATH
# export SPARK_HOME=/opt/spark-4-1-2
# export PATH=$SPARK_HOME/bin:$PATH
# export PATH=$SPARK_HOME/sbin:$PATH
# export PYSPARK_PYTHON=/usr/bin/python3.9
# export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.9
# export PYSPARK_PYTHON=/usr/bin/python3.12
# export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12

use-spark3() { export SPARK_HOME=/opt/spark-3-5-8; export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH; }
use-spark4() { export SPARK_HOME=/opt/spark-4-1-2; export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH; }

export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3

# use-spark3
use-spark4

```

enable bashrc

```bash
source ~/.bashrc
```

### confirm

```bash
use-spark3
spark-shell --version
> version 3.5.8
spark-submit --version
> version 3.5.8

use-spark4
spark-shell --version
> version 4.1.2
spark-submit --version
> version 4.1.2
```


## 3. Python venvs

Create one venv per line.

```bash
# Spark 3系
python3.12 -m venv env358
source env358/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements-3.5.8.txt
deactivate

# Spark 4系
python3.12 -m venv env412
source env412/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements-4.1.2.txt
deactivate
```

---

## 4. Run

Switch Spark and activate the matching venv, then run with either command.

```bash
# Spark 3系
use-spark3
source env358/bin/activate

# Spark 4系
use-spark4
source env412/bin/activate
```

```bash
spark-submit filename.py
# or
python filename.py
```

Check that both sides match before running.

```bash
spark-submit --version 2>&1 | grep -m1 version
python -c "import pyspark; print(pyspark.__version__)"
```

When finished:

```bash
deactivate
```