import json

def set_data(**kwargs):
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='sample4_task2', key='transformed_data')

    # データを格納する処理（例: DBに格納する）
    print(f"Storing transformed data: {json.dumps(transformed_data)}")
    # 実際にはDBに格納するコードを記述する
    return "Data stored successfully"
