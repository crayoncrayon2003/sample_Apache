import os
import configparser
import time
import inspect
import ray

config_ini = configparser.ConfigParser()
config_ini.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"), encoding='utf-8')

# SERVERS = 'ray://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'],'6379')     # Ray API (GCS) server port
SERVERS = 'ray://{}:{}'.format(config_ini['DEFAULT']['HOST_IP'],'10001')    # Ray client-server port

# init ray
ray.init(address=SERVERS,ignore_reinit_error=True)

@ray.remote # Processing 1
def sample_func1(): # taeget func
    fun_name = inspect.currentframe().f_code.co_name

    for idx in range(10):
        print(f"My name is: {fun_name}  {idx}/10")
        time.sleep(1)

    return True

@ray.remote # Processing 2
def sample_func2(): # taeget func
    fun_name = inspect.currentframe().f_code.co_name

    for idx in range(10):
        print(f"My name is: {fun_name}  {idx}/10")
        time.sleep(2)

    return True

def main():
    result1 = sample_func1.remote()         # Create an sample_func1 process.
    result2 = sample_func2.remote()         # Create an sample_func2 process.

    ##################
    # Multi Processing
    ##################

    results = ray.get([result1, result2])   # get result of each process

    print(results)

if __name__ == "__main__":
    main()
