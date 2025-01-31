from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os
# add the tasks folder to the system path for airflow to find the module
dag_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(dag_folder, ".."))
from tasks.dag_tasks import *  

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 31),
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}
# DAG with tasks dependencies
with DAG('news_dag',
        default_args=default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:

        get_data_eng = PythonOperator(
            task_id = 'get_data_eng',
            python_callable = get_data_eng
        )

        get_data_ita = PythonOperator(
            task_id = 'get_data_ita',
            python_callable = get_data_ita
        )

        transform_data = PythonOperator(
            task_id = 'transform_data',
            python_callable = transform_data
        )

        upload_data = PythonOperator(
            task_id = 'upload_data',
            python_callable = upload_data
        )

        [get_data_eng, get_data_ita] >> transform_data >> upload_data