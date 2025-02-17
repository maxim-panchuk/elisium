import os
import time

import requests

def add_captions_to_video(video_url, api_key, theme='Iman', language='Russian'):
    url = 'https://viralapi.vadoo.tv/api/add_captions'
    headers = {
        'X-API-KEY': api_key
    }
    data = {
        'url': video_url,
        'theme': theme,
        'language': language
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        vid = result.get('vid')
        return vid
    else:
        raise Exception(f"Ошибка при добавлении субтитров: {response.status_code} - {response.text}")


def get_video_url(video_id, api_key):
    url = f'https://viralapi.vadoo.tv/api/get_video_url?id={video_id}'
    headers = {
        'X-API-KEY': api_key
    }

    while True:
        print('attempting to get video url from vadoo ai')
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if len(result['url']) > 0:
                print(f'vadoo ai url: {result["url"]}')
                return result['url']
        else:
            raise Exception(f'Ошибка при получении ссылки на видео: {response.status_code} - {response.text}')

        time.sleep(5)

def download_video(video_url, api_key, save_dir='result', filename='downloaded_video_1.mp4'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print(video_url)
    file_path = os.path.join(save_dir, filename)

    headers = {
        'X-API-KEY': api_key
    }

    response = requests.get(video_url, stream=True, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'Видео успещно скачано: {file_path}')
        return file_path
    else:
        raise Exception(f'Ошибка при скачивании видео: {response.status_code} - {response.text}')