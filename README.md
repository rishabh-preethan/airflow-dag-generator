# DAG automation
DAG Automation is a web application that enables users to generate and manage Directed Acyclic Graphs (DAGs) for scheduling tasks. The application uses Pyodide for Python code execution in the browser and interacts with a backend server to generate and submit DAGs.

### Project Structure
##### Frontend
The frontend of the DAG Automation project is built using Svelte. It provides a user-friendly interface for interacting with the DAG generation and management features. Key components include:

* DAG Name Input: A text field for users to specify the name of the DAG, which must be a single string without spaces.
* Prompt Input: A larger text area where users enter a description for the DAG they wish to generate.
* Code Editor: A text area displaying the generated DAG code, with syntax highlighting and line numbers for ease of use.
* Buttons: Functional buttons for submitting the prompt to generate the DAG, checking the syntax of the generated code, and submitting the DAG code to the backend server.
* Loading Indicators: Visual feedback to inform users of ongoing processes, such as generating the DAG or checking syntax.
The frontend integrates with Pyodide to run Python code directly in the browser and communicates with a backend server via HTTP requests to process and submit DAGs.

##### Backend
The backend for the DAG Automation project is built using Flask, with the following key functionalities:

Code Directory Management: Stores generated DAG Python code in a specified directory. Ensures the directory exists and writes code files based on user input.

* Endpoints:

    * /upload_code: Receives POST requests to save generated DAG code to a file. The request must include code and dag_name. The code is saved with the provided DAG name as the filename.
    * /generate_dag: Receives POST requests with a prompt to generate DAG code. It uses Azure OpenAI's GPT-4 to generate the DAG code based on the provided prompt and system instructions.
    Azure OpenAI Integration: Utilizes Azure OpenAI's GPT-4 model to generate Python DAG code. The API key and endpoint configuration are set via environment variables.

### Setup Guide
###### Frontend:
Run these following commands:
To install dependencies:
```npm install```
To start the dev server:
```npm run dev```
Frontend will be running on : http://localhost:5173

##### Backend:
Install Dependencies:
```pip install flask openai```
Run the code:
```python3 app.py```


To check if Airflow DAG has been created go to http://localhost:8880