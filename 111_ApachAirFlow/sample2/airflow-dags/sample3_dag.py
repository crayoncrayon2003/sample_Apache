from airflow import DAG
from airflow.operators.python import PythonOperator  # 修正
from datetime import datetime
from sample3_task1_sender import sample3_task1_sender   # task1.pyからインポート
from sample3_task2_receiver import sample3_task2_receiver  # task2.pyからインポート（修正）

# デフォルト引数
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 24),
    'retries': 1,
}

dag = DAG(
    'sample3',                              # DAG名
    default_args=default_args,              # デフォルト引数
    schedule_interval='* * * * *',          # 毎分実行
    catchup=False
)

# タスク1のタスク定義
sample3_task1 = PythonOperator(
    task_id='sample3_task1',                # タスク1のID
    python_callable=sample3_task1_sender,   # 実行する関数
    dag=dag                                 # DAGを指定
)

# タスク2のタスク定義
sample3_task2 = PythonOperator(
    task_id='sample3_task2',                # タスク2のID
    python_callable=sample3_task2_receiver, # 実行する関数
    dag=dag                                 # DAGを指定
)

# タスク間の依存関係を設定
sample3_task1 >> sample3_task2

