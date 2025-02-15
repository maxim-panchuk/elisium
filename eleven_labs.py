import requests

def generate_speech(text):
    url = "http://66.55.76.199/v1/text-to-speech/hU3rD0Yk7DoiYULTX1pD?output_format=mp3_44100_128"
    headers = {
        "xi-api-key": "sk_8b49f06b1b5be715f4c227f3a9afb950c6a20a24d7fe5aad",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open("audio/audio.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Ошибка: статус {response.status_code}, ответ: {response.text}")

    return "audio/audio.mp3"