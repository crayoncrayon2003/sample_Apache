import random

def get_data_1(**kwargs):
    data = {"source": "api", "value": random.randint(1, 100)}
    kwargs['ti'].xcom_push(key='data_1', value=data)
    print("Data 1 Retrieved: ", data)
    return data
