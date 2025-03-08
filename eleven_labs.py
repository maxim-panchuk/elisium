import requests
import time
from config import config

def generate_speech(text: str) -> str:
    """
    Sends the given text to the Eleven Labs text-to-speech API
    and saves the resulting audio to a local file.
    Returns the path to the saved audio file.
    Retries up to 3 times on failure.
    """
    max_retries = 3
    retry_count = 0
    wait_time = 1 # sec

    headers = {
        'xi-api-key': config.eleven_labs_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'model_id': config.eleven_labs_model_id
    }

    while retry_count < max_retries:
        try:
            response = requests.post(config.url, headers=headers, json=payload)
            
            if response.status_code == 200:
                with open(config.path_to_voice, "wb") as f:
                    f.write(response.content)
                return config.path_to_voice
                
            print(f"Attempt {retry_count + 1} failed. Status: {response.status_code}, response: {response.text}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(wait_time)
                wait_time *= 2
            
        except Exception as e:
            print(f"Error on attempt {retry_count + 1}: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(wait_time)
                wait_time *= 2
            
    print("Maximum number of retries exceeded")
    return ""