from airflow import DAG
from airflow.operators.python import PythonOperator  # 修正
from datetime import datetime, timedelta
import time

# タスク1: 時間を送る
def sample2_task1_sender(**kwargs):
    # 開始時刻
    start_time = time.time()

    # サンプルとして待機
    time.sleep(5)

    # 終了時刻
    end_time = time.time()

    # 時間の計算
    duration = end_time - start_time

    # XComでタスク2へ時間を送る
    kwargs['ti'].xcom_push(key='driving_duration', value=duration)
    print(f"Sample2 Task1 - Duration: {duration} seconds")

# タスク2: 時間を受ける
def sample2_task2_reciver(**kwargs):
    # XComでタスク１から時間を受ける
    ti = kwargs['ti']
    driving_duration = ti.xcom_pull(task_ids='sample2_task1', key='driving_duration')

    print(f"Sample2 Task2 - Received Duration: {driving_duration} seconds")

# デフォルト引数
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 24),
    'retries': 1,
}

# DAG定義
dag = DAG(
    'sample2',                              # DAG名
    default_args=default_args,              # デフォルト引数
    schedule_interval='* * * * *',          # 毎分実行
    catchup=False
)

# タスク1のタスク定義
sample2_task1 = PythonOperator(
    task_id='sample2_task1',                # タスク1のID
    python_callable=sample2_task1_sender,   # 実行する関数
    dag=dag                                 # DAGを指定
)

# タスク2のタスク定義
sample2_task2 = PythonOperator(
    task_id='sample2_task2',                # タスク2のID
    python_callable=sample2_task2_reciver,  # 実行する関数
    dag=dag                                 # DAGを指定
)

# タスク間の依存関係を設定
sample2_task1 >> sample2_task2

