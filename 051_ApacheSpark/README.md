# Apache Spark Samples

This is a sample of Apache Spark.

Apache Spark consists of four components.

+ Spark SQL
+ Spark Streaming
+ Spark MLlib
+ Spark GraphX

## Environments

This repository uses two Spark lines, each in its own venv.

| Line                | Spark | Java | venv       |
| ------------------- | ----- | ---- | ---------- |
| **Spark 3系** | 3.5.8 | 17   | `env358` |
| **Spark 4系** | 4.1.2 | 17   | `env412` |

The two lines use **separate venvs** so they do not collide. Set up whichever
line you need — the 3系 setup below is the base, and the 4系 setup differs only
in the Spark / venv version.

---

# Spark 3系 (3.5.8) — four core samples

The steps below are the local setup (Java / Spark / Python venv).

## Java

### install

```bash
sudo apt update
sudo apt install openjdk-17-jdk wget tar -y
java -version
```

### Select Java version

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

### Set path

open bashrc

```bash
vim ~/.bashrc
```

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

### confirm

```bash
spark-shell --version
> version 3.5.8
spark-submit --version
> version 3.5.8
```

## python

### create venv & activate venv

```bash
python3.12 -m venv env358
```

### activate venv

```bash
source env358/bin/activate
```

### pip isntall

```bash
pip install --upgrade pip setuptools
pip install -r requirements-3.5.8.txt
```

### run

```bash
python3.12 filename.py
```

```bash
spark-submit filename.py
```

### deactivate venv

```bash
deactivate
```

---

# Spark 4系 (4.1.2)

Set this line up **in addition to** the 3系 line above, in its own venv — do not
overwrite the 3.5.8 environment. Only the Spark version and the venv differ.

## Java

Same as the 3系 chapter — **Java 17** is required and already covered there.
No extra step is needed if you followed the 3系 Java setup.

## spark

### Install

check latest stable version. ref https://dlcdn.apache.org/spark/
following "spark-4-1-2"

```bash
wget https://dlcdn.apache.org/spark/spark-4.1.2/spark-4.1.2-bin-hadoop3.tgz
sudo tar -xzf spark-4.1.2-bin-hadoop3.tgz -C /opt/
sudo mv /opt/spark-4.1.2-bin-hadoop3 /opt/spark-4-1-2
ls /opt/spark-4-1-2/bin/
```

### Set path

Because both lines set `SPARK_HOME`, switch between them by pointing
`SPARK_HOME` at the version you want to use in the current shell.

open bashrc

```bash
vim ~/.bashrc
```

```bash
export SPARK_HOME=/opt/spark-4-1-2
export PATH=$SPARK_HOME/bin:$PATH
export PATH=$SPARK_HOME/sbin:$PATH
export PYSPARK_PYTHON=/usr/bin/python3.12
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12
```

enable bashrc

```bash
source ~/.bashrc
```

### confirm

```bash
spark-shell --version
> version 4.1.2
spark-submit --version
> version 4.1.2
```

## python

Create a **separate** venv so pyspark 4.x does not clobber the 3.5.8 env.

### create venv & activate venv

```bash
python3.12 -m venv env412
```

### activate venv

```bash
source env412/bin/activate
```

### pip install

```bash
pip install --upgrade pip setuptools
pip install -r requirements-4.1.2.txt
```

### run

```bash
python3.12 filename.py
```

```bash
spark-submit filename.py
```

### deactivate venv

```bash
deactivate
```

---

# Spark 3系 / 4系 併用 (side by side)

Install both lines at once and switch per shell. Nothing is shared except Java —
each line keeps its own `SPARK_HOME` and its own venv (`env358` / `env412`).

## Java

Same **Java 17** serves both lines. No extra step if you followed the 3系 Java setup.

## spark

### Install

Install both, following the 3系 and 4系 chapters above.

```bash
ls /opt/spark-3-5-8/bin/
ls /opt/spark-4-1-2/bin/
```

### Set path

Do **not** hard-code one `SPARK_HOME` in `~/.bashrc`. Register switch functions
once, then switch per shell.

open bashrc

```bash
vim ~/.bashrc
```

edit follow (write once)

```bash
use-spark3() { export SPARK_HOME=/opt/spark-3-5-8; export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH; }
use-spark4() { export SPARK_HOME=/opt/spark-4-1-2; export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH; }
export PYSPARK_PYTHON=/usr/bin/python3.12
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12
```

enable bashrc

```bash
source ~/.bashrc
```

### confirm

```bash
use-spark3
spark-submit --version
> version 3.5.8

use-spark4
spark-submit --version
> version 4.1.2
```

## python

Keep both venvs; activate the one that matches the line you switched to.

### create venv & activate venv

Already created in the 3系 / 4系 chapters (`env358` / `env412`). Activate the
matching one.

```bash
# Spark 3系
source env358/bin/activate

# Spark 4系
source env412/bin/activate
```

### pip install

Already installed in each chapter (`pyspark==3.5.8` / `pyspark==4.1.2`). No extra step.

### run

Match the venv and (for CLI use) the `SPARK_HOME`.

```bash
# Spark 3系
use-spark3
source env358/bin/activate
python3.12 filename.py

# Spark 4系
use-spark4
source env412/bin/activate
python3.12 filename.py
```

### deactivate venv

```bash
deactivate
```
