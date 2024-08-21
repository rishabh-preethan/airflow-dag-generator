from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from datetime import datetime
import datetime
import time
import datetime
import pyperclip
import json
import csv
import os
import base64
import re
from dotenv import load_dotenv
from openai import AzureOpenAI

def initial_setup():
    global client, system_prompt, validation_data
    load_dotenv()

    api_base = os.getenv('GRAPHRAG_LLM_API_BASE') 
    api_key=os.getenv('GRAPHRAG_LLM_API_KEY')
    deployment_name = os.getenv('GRAPHRAG_LLM_DEPLOYMENT_NAME')
    api_version = os.getenv('GRAPHRAG_LLM_API_VERSION') 

    client = AzureOpenAI(
        api_key=api_key,  
        api_version=api_version,
        base_url=f"{api_base}openai/deployments/{deployment_name}",
    )

    with open('system_prompt.txt', 'r') as file:
        # Read the entire contents of the file
        system_prompt = file.read()

    with open('validation_data.json', 'r') as file:
        validation_data = json.load(file)

def extract_json_section(text):
    """
    Extracts the JSON section from a text.
    
    Args:
    text (str): The input text containing JSON data.
    
    Returns:
    dict: The extracted JSON object.
    """
    # Regular expression to match JSON data between triple backticks
    json_pattern = re.compile(r'```json\s*([\s\S]*?)\s*```')
    
    # Find the first match of the pattern in the text
    match = json_pattern.search(text)
    
    if match:
        json_string = match.group(1)
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError:
            # Handle the case where the match is not valid JSON
            print(f"Warning: Failed to decode JSON: {json_string}")
            return {"graph_data": None}
    else:
        # Handle the case where no JSON section is found
        print("Warning: No JSON section found in the text.")
        return {"graph_data": None}

def search_dict(validation_data, graph_data):
    # Iterate over each item in validation_data
    for key, value in validation_data.items():
        # Compare if the graph_data matches the current validation_item
        if graph_data == value:
            return {"is_data_correct": True}
    
    # If no match is found, return False
    return {"is_data_correct": False}

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def send_to_test_llm(image_path):
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_path}"
                    }
                }
            ]
        }
    ]
    
    # Call the API
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        # stream=True,
        # max_tokens=5000
    )

    # Return the first choice from the response
    return response.choices[0].message.content

def clean_json_string(json_string):
    # Fix key-value formatting issues
    # Add missing commas between key-value pairs
    json_string = re.sub(r'(?<=\w)(:)(?=\w)', r': ', json_string)
    json_string = re.sub(r'(?<=\w)(,)(?=\w)', r', ', json_string)
    
    # Add missing commas after closing braces if needed
    json_string = re.sub(r'(?<=\w)(\n)(?=\w)', r',\n', json_string)
    
    # Ensure all keys and values are properly quoted
    json_string = json_string.replace('“', '"').replace('”', '"')
    
    # Add missing commas before closing braces
    json_string = re.sub(r'(?<=\S)(\n)(?=[}\]])', r',\n', json_string)
    
    return json_string

def run_automation():
    initial_setup()
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--headless')  # Disable notifications

    # Add preferences to handle clipboard access
    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.default_content_setting_values.clipboard": 1  # Allow clipboard access
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize WebDriver
    try:
        chrome_driver_path = r'D:\VS Code Projects 2024\Test Automation\chromedriver-win64\chromedriver.exe'
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    

        results = {}

        # List of prompts
        prompts = None

        with open('sample_prompts.json', 'r') as file:
            prompts = json.load(file)
            print('Prompts list: ', prompts)

        # Open the URL
        driver.get('https://trustonic.copilot.thirdray.ai/')
    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    wait = WebDriverWait(driver, 10)

    # Login
    # Locate email and password input
    email_input = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[3]/div/form/div[2]/div[1]/input')))
    # /html/body/div/div[1]/div/div[3]/div/form/div[2]/div[1]/input

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[3]/div/form/div[2]/div[2]/input')))
    print('Entering email and password')

    # Enter email and password
    email_input.send_keys('aditi.ladia@trustonic.com')
    password_input.send_keys('Tangoe@123')

    print('Entered email and password')
    # Click sign in button
    sign_in = driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[3]/div/form/div[3]/button')
    sign_in.click()

    # Close the updates
    wait = WebDriverWait(driver, 3)
    cross_button = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[1]/div[1]/button')))
    cross_button.click()
        
    print('Starting iteration')
    for key, value in prompts.items():
        
        new_chat_button = driver.find_element(By.CSS_SELECTOR, '.self-center.font-medium.text-sm.text-gray-850.dark\:text-white')
        new_chat_button.click()
        # Select model - Currently Analytics Assistant is selected as the default model

        # Enable toolkit
        wait = WebDriverWait(driver,100)
        plus_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.bg-gray-50.hover\\:bg-gray-100.text-gray-800.dark\\:bg-gray-850.dark\\:text-white.dark\\:hover\\:bg-gray-800.transition.rounded-full.p-2.outline-none.focus\\:outline-none')))
        plus_button.click()

        wait = WebDriverWait(driver,100)
        toolkit_toggle =  wait.until(EC.presence_of_element_located((By.XPATH, '(//span[contains(@class, "pointer-events-none") and contains(@class, "block") and contains(@class, "size-4") and contains(@class, "shrink-0") and contains(@class, "rounded-full") and contains(@class, "bg-white") and contains(@class, "transition-transform") and contains(@class, "data-[state=checked]:translate-x-3.5") and contains(@class, "data-[state=unchecked]:translate-x-0") and contains(@class, "data-[state=unchecked]:shadow-mini")])[2]')))
        
        # Check the 'data-state' attribute
        data_state = toolkit_toggle.get_attribute('data-state')
        
        # Click the button if the state is 'unchecked'
        if data_state == 'unchecked':
            driver.execute_script("arguments[0].click();", toolkit_toggle)
        # time.sleep(3)
        plus_button.click()

        # Give input prompt
        input_textbox = driver.find_element(By.XPATH, '//*[@id="chat-textarea"]')
        input_textbox.send_keys(value)
        input_textbox.send_keys(Keys.RETURN)

        wait = WebDriverWait(driver, 500)

        # Copy json
        copy_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.visible.p-1\\.5.hover\\:bg-black\\/5.dark\\:hover\\:bg-white\\/5.rounded-lg.dark\\:hover\\:text-white.hover\\:text-black.transition.copy-response-button')))
        driver.execute_script("arguments[0].click();", copy_button)
        wait = WebDriverWait(driver, 5)
        
        llm_response = pyperclip.paste()

        graph_data = extract_json_section(llm_response)
    
        print('---------------')
        print('Graph data from the LLM: ', graph_data)
        print(type(graph_data))


        data_result = search_dict(validation_data, graph_data)

        time.sleep(5)
        driver.save_screenshot(f'{key}_graph.png')

        encoded_image = encode_image(f'{key}_graph.png')
        # Send the screenshot to test llm
        chart_result_str = send_to_test_llm(encoded_image)
        chart_result = json.loads(chart_result_str)
        print('Result from the llm: ', chart_result)
        print('Result from the data: ', data_result)
        combined_dict = chart_result.copy()  
        # combined_dict = data_result.copy()
        combined_dict.update(data_result)
        results[key] = combined_dict


        time.sleep(3)
    print('Testing for all prompts completed, closing the browser')
    driver.close()
    # Define the CSV file name
    # date_str = datetime.now().strftime('%d%m%Y')
    date_str = datetime.datetime.now().strftime('%d%m%Y_%H%M%S')
    csv_file = f'test-reports/test_results_{date_str}.csv'

    # headers = ['prompt_key', 'is_data_correct', 'overall_result']
    headers = ['prompt_key', 'is_chart_present', 'is_chart_clean', 'is_data_correct', 'overall_result']

    # Write data to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the headers
        writer.writerow(headers)
        
        # Write the data rows
        for prompt_key, values in results.items():
            # Determine overall_result
            is_chart_present = values.get('is_chart_present')
            is_chart_clean = values.get('is_chart_clean')
            is_data_correct = values.get('is_data_correct')
            
            overall_result = is_data_correct
            
            # Write the row with overall_result
            row = [prompt_key, is_chart_present, is_chart_clean, is_data_correct, overall_result]
            writer.writerow(row)
    print('Created the test report')
    # return {"completion_status": True}
    

def get_file_details():
    """
    Fetches the details of all files present in the specified folder.

    Args:
        folder_path (str): The path to the folder containing the files.
        base_url (str): The base URL to construct the download URL.

    Returns:
        list: A list of dictionaries, where each dictionary contains the file details.
    """
    folder_path = 'test-reports'
    base_url = 'http://127.0.0.1:5000'
    
    file_details = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_stats = os.stat(file_path)
            download_url = f"{base_url}/test-reports/{filename}"
            file_details.append({
                'name': filename,
                'timestamp': datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': file_stats.st_size,
                'download_url': download_url
            })
    # for file in file_details:
    #     print(f"Name: {file['name']}, Timestamp: {file['timestamp']}, Size: {file['size']} bytes, Download: <a href='{file['download_url']}'>{file['download_url']}</a>")
    return file_details

# Example usage:
# folder_path = 'test-reports'
# file_details = get_file_details(folder_path)
# for file in file_details:
#     print(f"Name: {file['name']}, Timestamp: {file['timestamp']}, Size: {file['size']} bytes")