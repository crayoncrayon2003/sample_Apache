# install
## Java
```
sudo apt update
sudo apt install openjdk-11-jdk wget tar -y
java -version
```
## spark
### Install
```
wget https://dlcdn.apache.org/spark/spark-3.5.4/spark-3.5.4-bin-hadoop3.tgz
sudo mkdir -p /opt/spark-3-5-4
sudo tar -xvzf spark-3.5.4-bin-hadoop3.tgz -C /opt/spark-3-5-4 --strip-components=1
ls /opt/spark
```

### Setting
open the .bashrc
```
vim ~/.bashrc
```

add the following at the end
```
export SPARK_HOME=/opt/spark-3-5-4
export PATH=$SPARK_HOME/bin:$PATH
export PATH=$SPARK_HOME/sbin:$PATH
```

apply the changes
```
source ~/.bashrc
```

### Check
```
spark-shell --version
spark-submit --version
```

```
pip3 install pyspark==3.5.3 py4j
```
