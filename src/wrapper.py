import os
import argparse
#import base64
import requests
from urllib.parse import urlparse
import time

import runpod
#from runpod.serverless.utils.rp_validator import validate
#from runpod.serverless.utils.rp_upload import upload_file_to_bucket
#from runpod.serverless.utils import rp_download, rp_cleanup


def download_and_save(url, save_dir, save_filename):
    '''
    Download a file from a URL and save it to the specified directory.
    '''
    try:
        parsed_url = urlparse(url)
        download_url = url
        
        if parsed_url.netloc == "civitai.com" and args.civitai_token:
            separator = '&' if '?' in url else '?'
            download_url = f"{url}{separator}token={args.civitai_token}"
            
        response = requests.get(download_url)
        response.raise_for_status()
        
        os.makedirs("/workspace" + save_dir, exist_ok=True)
        save_path = os.path.join("/workspace" + save_dir, save_filename)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        return save_path
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def wait_for_server(port, max_retries=30, delay=1):
    '''
    Ждём, пока сервер станет доступен.
    max_retries: максимальное количество попыток
    delay: задержка между попытками в секундах
    '''
    for attempt in range(max_retries):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/internal/ping")
            if response.status_code == 200:
                print(f"Сервер доступен после {attempt + 1} попыток")
                return True
        except requests.exceptions.RequestException:
            print(f"Ожидание сервера, попытка {attempt + 1}/{max_retries}")
            time.sleep(delay)
    
    raise TimeoutError(f"Сервер не запустился после {max_retries} попыток")

def run(job):
    '''
    Run inference on the model.
    '''
    print("Received job:", job)

    job_input = job['input']
    if 'method' not in job_input:
        return {"error": "Method is required in input"}

    job_method = job_input['method'] # GET, POST, DOWNLOAD
    job_path = job_input['path'] # /sdapi/v1/loras
    job_port = job_input['port'] # 8081

    # Input validation
    if job_method == "DOWNLOAD":
        return download_and_save(job_input['url'], job_input['save_dir'], job_input['save_filename'])
    elif job_method == "GET":
        wait_for_server(job_port)
        response = requests.get(f"http://127.0.0.1:{job_port}{job_path}")
        response.raise_for_status()
        return response.json()
    elif job_method == "POST":
        wait_for_server(job_port)
        response = requests.post(f"http://127.0.0.1:{job_port}{job_path}", json=job_input['body'])
        response.raise_for_status()
        return response.json()
    elif job_method == "UPLOAD":
        files = job_input.get('files', [])
        if isinstance(files, str):
            files = [files]  # преобразуем строку в список, если передан один файл
            
        target_url = job_input.get('target_url')
        auth_token = job_input.get('auth_token')
        
        if not files or not target_url:
            return {"error": "Files and target_url are required for upload"}
            
        uploaded_files = []
        failed_files = []
        
        headers = {}
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
            
        for file_path in files:
            try:
                if not os.path.exists(file_path):
                    failed_files.append({
                        "path": file_path,
                        "error": "File not found"
                    })
                    continue
                    
                with open(file_path, 'rb') as f:
                    files_data = {'file': (os.path.basename(file_path), f)}
                    response = requests.post(target_url, 
                                          files=files_data,
                                          headers=headers)
                    response.raise_for_status()
                    
                uploaded_files.append({
                    "path": file_path,
                    "response": response.json() if response.content else "Success"
                })
                
            except Exception as e:
                failed_files.append({
                    "path": file_path,
                    "error": str(e)
                })
                
        return {
            "uploaded": uploaded_files,
            "failed": failed_files
        }
    else:
        return {"error": "Invalid method"}

'''
Entry point.
'''
# Grab args
parser = argparse.ArgumentParser()
parser.add_argument('--civitai_token', type=str, help='Civitai API token')

if __name__ == "__main__":
    args = parser.parse_args()
    runpod.serverless.start({"handler": run})