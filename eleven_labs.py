import requests

PATH_TO_VOCE = 'audio/audio.mp3'
URL = 'http://66.55.76.199/v1/text-to-speech/hU3rD0Yk7DoiYULTX1pD?output_format=mp3_44100_128'
URL_WITH_TIMESTAMPS = 'http://66.55.76.199/v1/text-to-speech/hU3rD0Yk7DoiYULTX1pD/with-timestamps?output_format=mp3_44100_128'
ELEVEN_LABS_API_KEY = 'sk_8b49f06b1b5be715f4c227f3a9afb950c6a20a24d7fe5aad'
ELEVEN_LABS_MODEL_ID = 'eleven_multilingual_v2'

def generate_speech(text):
    url = URL
    headers = {
        'xi-api-key': ELEVEN_LABS_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'model_id': ELEVEN_LABS_MODEL_ID
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open(PATH_TO_VOCE, "wb") as f:
            f.write(response.content)
    else:
        print(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    return PATH_TO_VOCE