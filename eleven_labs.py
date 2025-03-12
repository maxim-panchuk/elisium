import requests
import time
from config import config
import os
import subprocess

def generate_speech(text: str) -> str:
    """
    Sends the given text to the Eleven Labs text-to-speech API
    and saves the resulting audio to a local file.
    Returns the path to the saved audio file.
    Retries up to 3 times on failure.
    """
    max_retries = 3
    retry_count = 0
    wait_time = 15 # sec

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

def transcribe_speech(path_to_voice: str) -> str:
    """
    Sends the given audio file to the Eleven Labs transcription API
    and returns the resulting text.
    """
    if os.path.exists(config.path_to_transcription):
        os.remove(config.path_to_transcription)
    
    cmd = ['curl', '-X', 'POST',
           config.transcription_url,
           '-H', 'xi-api-key: ' + config.eleven_labs_api_key,
           '-H', 'Content-Type: multipart/form-data',
           '-H', 'language_code: rus',
           '-F', 'model_id=' + config.transcription_model_id,
           '-F', 'file=@' + path_to_voice]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        with open(config.path_to_transcription, 'w') as f:
            f.write(result.stdout)
        return config.path_to_transcription
    else:
        print(f"Error transcribing speech: {result.returncode}, response: {result.stderr}")
        return None