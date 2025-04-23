import time

def sample3_task1_sender(**kwargs):
    start_time = time.time()  # 実行開始時刻

    # 実行処理（例: 5秒間の待機）
    time.sleep(5)  # サンプルとして5秒間待機

    end_time = time.time()  # 実行終了時刻
    duration = end_time - start_time  # 駆動時間を計算

    # XComでタスク2に駆動時間を送る
    kwargs['ti'].xcom_push(key='driving_duration', value=duration)
    print(f"Sample3 Task1 - Duration: {duration} seconds")

