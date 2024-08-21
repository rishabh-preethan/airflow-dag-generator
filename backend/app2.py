from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# CORS(app, resources={r"/*": {"origins": "http://localhost:5173/"}})
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"], "headers": ["Content-Type", "Authorization"]}})
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Set environment variables and define the function
os.environ['GRAPHRAG_LLM_DEPLOYMENT_NAME'] = 'gpt-4o'
os.environ['GRAPHRAG_LLM_API_KEY'] = '7c90d344cb524b9885202a7603641589'
os.environ['GRAPHRAG_LLM_API_BASE'] = 'https://azure-isv-success-in.openai.azure.com'
os.environ['GRAPHRAG_LLM_API_VERSION'] = '2024-06-01'

@app.before_request
def option_autoreply():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        headers = resp.headers

        # Allow the origin which made the XHR
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET,HEAD,POST,OPTIONS,PUT,PATCH,DELETE'
        headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'

        # Set the headers and return the response
        return resp

def generate_dag_code(schedule, prompt):
    dag_code = f"""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import time
import requests

default_args = {{
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}}

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
        print(f"Failed to trigger API request, status code: {{response.status_code}}")

dag = DAG(
    'simple_dag_with_api_notification',
    default_args=default_args,
    description='A simple DAG that performs a task and triggers an API request on completion',
    schedule_interval='{schedule}',
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
"""
    return dag_code

@app.route('/api/schedule', methods=['POST', 'OPTIONS'])
def schedule_dag():
    if request.method == 'OPTIONS':
        return jsonify({"status": "OK"}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS'}
    data = request.json
    schedule = data.get('schedule')
    prompt = data.get('prompt')
    
    dag_code = generate_dag_code(schedule, prompt)
    
    dag_filename = 'generated_dag.py'
    with open(dag_filename, 'w') as file:
        file.write(dag_code)
    
    return jsonify({"dag_code": dag_code})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
