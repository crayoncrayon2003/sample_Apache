# Apache Spark Samples

A set of small samples to learn the whole picture of Apache Spark.
Spark has **four main components** (SQL / Streaming / MLlib / GraphX) on top of the shared **Spark Core**.

```
        ┌──────────────────────────────────────────────┐
 1X     │  Spark SQL │ Streaming │  MLlib  │  GraphX     │  ← four main components
        ├──────────────────────────────────────────────┤
        │               Spark Core (RDD)                │
        └──────────────────────────────────────────────┘
 0X     Getting started: touch Spark lightly (local / cluster)
 2X     Show the benefit of Spark by comparing with other libraries
```

## Structure

| Folder                                                       | Layer      | Description                                                     |
| ------------------------------------------------------------ | ---------- | -------------------------------------------------------------- |
| [sample01_local/](sample01_local/)                           | 0X intro   | Smallest local example (read / show / aggregate)               |
| [sample02_cluster/](sample02_cluster/)                       | 0X intro   | Run on a Docker cluster                                        |
| [sample11_SQL/](sample11_SQL/)                               | 1X         | **Spark SQL** — DataFrame API and `spark.sql()`               |
| [sample12_streaming/](sample12_streaming/)                   | 1X         | **Structured Streaming** — with Kafka                         |
| [sample13_Mlib/](sample13_Mlib/)                             | 1X         | **MLlib** — regression / classification (Pipeline)            |
| [sample14_GraphX/](sample14_GraphX/)                         | 1X         | **GraphX / GraphFrames** — PageRank, connected components     |
| [sample21_MLlib_vs_sklearn/](sample21_MLlib_vs_sklearn/)     | 2X compare | MLlib vs **scikit-learn** (measure where Spark starts to win)  |
| [sample22_PySpark_vs_PyTorch/](sample22_PySpark_vs_PyTorch/) | 2X compare | PySpark+PyTorch vs **PyTorch alone** (distributed inference / training) |

> Note: GraphX has no Python API, so PySpark uses a separate package, **GraphFrames**.
>
> The 2X layer writes the same task with a single-machine library too, and measures the point where Spark becomes faster as the data grows. It also honestly shows that for small data the single-machine library is faster.

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
> openjdk version "11.0.26" 2025-01-21
> OpenJDK Runtime Environment (build 11.0.26+4-post-Ubuntu-1ubuntu124.04)
> OpenJDK 64-Bit Server VM (build 11.0.26+4-post-Ubuntu-1ubuntu124.04, mixed mode, sharing)
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
