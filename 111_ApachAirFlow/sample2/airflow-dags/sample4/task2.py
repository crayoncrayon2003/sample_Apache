def transform_data(**kwargs):
    ti = kwargs['ti']

    data_1 = ti.xcom_pull(task_ids='sample4_task1_1', key='data_1')
    data_2 = ti.xcom_pull(task_ids='sample4_task1_2', key='data_2')

    datas = []
    if data_1:
        datas.append(data_1)
    if data_2:
        datas.append(data_2)

    for data in datas:
        transformed_data = {
            "value": data['value'] * -1,
        }

        ti.xcom_push(key='transformed_data', value=transformed_data)
        print("Data Transformed: ", transformed_data)
