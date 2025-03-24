from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

def sample1_hello_airflow():
    print('Hello, Airflow!')

# デフォルト引数
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 24),
    'retries': 1,
}

# DAG定義
dag = DAG(
    'hello_airflow',                # DAG名
    default_args=default_args,      # デフォルト引数
    schedule_interval='* * * * *',  # 毎分実行
)

# スタートタスクのタスク定義
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

# helloタスクのタスク定義
hello_task = PythonOperator(
    task_id='hello',
    python_callable=sample1_hello_airflow,
    dag=dag,
)

# タスク間の依存関係を設定
start_task >> hello_task

