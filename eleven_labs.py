import requests
import configparser
import os
import time
# Load config
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

# Retrieve values from config
ELEVEN_LABS_API_KEY = config["API_KEYS"]["ELEVEN_LABS_API_KEY"]
ELEVEN_LABS_MODEL_ID = config["API_KEYS"]["ELEVEN_LABS_MODEL_ID"]
URL = config["URLS"]["URL"]
URL_WITH_TIMESTAMPS = config["URLS"]["URL_WITH_TIMESTAMPS"]
PATH_TO_VOICE = config["PATHS"]["PATH_TO_VOICE"]

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
        'xi-api-key': ELEVEN_LABS_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'model_id': ELEVEN_LABS_MODEL_ID
    }

    while retry_count < max_retries:
        try:
            response = requests.post(URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                with open(PATH_TO_VOICE, "wb") as f:
                    f.write(response.content)
                return PATH_TO_VOICE
                
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