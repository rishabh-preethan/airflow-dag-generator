
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import time
import requests

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

def task_that_takes_time(**kwargs):
    count = int(kwargs['dag_run'].conf.get('seconds', 1))
    time.sleep(count)
    print("Task completed")

def trigger_api_request():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    if response.status_code == 200:
        print("API request was successful")
    else:
        print(f"Failed to trigger API request, status code: {response.status_code}")

dag = DAG(
    'simple_dag_with_api_notification',
    default_args=default_args,
    description='A simple DAG that performs a task and triggers an API request on completion',
    schedule_interval='* * * * *',
)

task_1 = PythonOperator(
    task_id='task_that_takes_time',
    python_callable=task_that_takes_time,
    provide_context=True,
    dag=dag,
)

task_2 = PythonOperator(
    task_id='trigger_api_request',
    python_callable=trigger_api_request,
    provide_context=True,
    dag=dag,
)

task_1 >> task_2
