import random

def get_data_2(**kwargs):
    data = {"source": "file", "value": random.randint(1, 100)}
    kwargs['ti'].xcom_push(key='data_2', value=data)
    print("Data 2 Retrieved: ", data)
    return data
