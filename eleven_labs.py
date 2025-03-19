import requests
import time
from config import config
import os
import subprocess


def generate_speech(text: str) -> str:
    headers = {
        'xi-api-key': config.eleven_labs_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'model_id': config.eleven_labs_model_id
    }

    response = requests.post(config.url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(config.path_to_voice, "wb") as f:
            f.write(response.content)
        return config.path_to_voice
    else:
        print(f"Error generating speech: {response.status_code}, response: {response.text}")
        raise Exception(f"Error generating speech: {response.status_code}, response: {response.text}")

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
        raise Exception(f"Error transcribing speech: {result.returncode}, response: {result.stderr}")