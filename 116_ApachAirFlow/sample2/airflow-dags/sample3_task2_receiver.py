def sample3_task2_receiver(**kwargs):
    # XComから駆動時間を受け取る
    ti = kwargs['ti']
    driving_duration = ti.xcom_pull(task_ids='sample3_task1', key='driving_duration')

    print(f"Sample3 Task2 - Received Duration: {driving_duration} seconds")

