from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# タスクのインポート
from sample4.task1_1 import get_data_1
from sample4.task1_2 import get_data_2
from sample4.task2 import transform_data
from sample4.task3 import set_data

# デフォルト引数
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 24),
    'retries': 1,
}

# DAGの定義
dag = DAG(
    'sample4_etl',  # DAG名
    default_args=default_args,
    schedule_interval='* * * * *',  # 毎分実行
    catchup=False
)

# タスク定義
sample4_task1_1 = PythonOperator(
    task_id='sample4_task1_1',  # タスク1_1（データ取得1）
    python_callable=get_data_1,
    dag=dag
)

sample4_task1_2 = PythonOperator(
    task_id='sample4_task1_2',  # タスク1_2（データ取得2）
    python_callable=get_data_2,
    dag=dag
)

sample4_task2 = PythonOperator(
    task_id='sample4_task2',  # タスク2（データ変換）
    python_callable=transform_data,
    dag=dag
)

sample4_task3 = PythonOperator(
    task_id='sample4_task3',  # タスク3（データ格納）
    python_callable=set_data,
    dag=dag
)

# タスクの依存関係設定
sample4_task1_1 >> sample4_task2  # sample4_task1_1が終わった後にsample4_task2を実行
sample4_task1_2 >> sample4_task2  # sample4_task1_2が終わった後にsample4_task2を実行
sample4_task2 >> sample4_task3    # sample4_task2が終わった後にsample4_task3を実行
