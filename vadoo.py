import os
import time

import requests

def add_captions_to_video(video_url, api_key, theme='Luke', language='Russian'):
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

def download_video(video_url, api_key, save_dir='result', filename='downloaded_video.mp4'):
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


# Download
# video_url = 'https://dfsncplzrz5f2.cloudfront.net/renders/gwid8sthzm/out.mp4?Expires=1739441211&Signature=AunN5HJ~rLQrD~wVkWW~Q7U-1eMKwFju6KdR15Tsg5-crBtgsSdMf8wx36cEvs~zL~IB2TF5DhDdSj7acBJRuqjsTAnCVK4uVvbA35Cb4mcucAK~Bb7oxfiy4RNyK2uWK8-9tupxHr3DnQqwkHLmyNQrAJAaIuS3MQwpNOl0hXqAnyDY9AKzBspHbFLNWElRx-vaiHj3oYc~n~AzTPB75NSpGnhZufm9Okn9xEn4TWGQ9MZvZn67UEL15VuNAFQSOXIObE27S5GIFN2uGGqeraTuhQfUInUEvvpoR2AwitQnP~d5mAyAbJWZiIRtZfZuHHXLVpQxUU~GuTjeO70tSg__&Key-Pair-Id=K2G9P08V12PAM1'
# #api_key = 'dAyNSrz-6poJsNn-7kgL3HfykbG1XiXOzEjhZQd1Y0Q'
# try:
#     path = download_video(video_url, api_key)
#     print(f'Видео сохранено в {path}')
# except Exception as e:
#     print(str(e))


# Get Download URL
# video_id = '170451637489'
# api_key = 'dAyNSrz-6poJsNn-7kgL3HfykbG1XiXOzEjhZQd1Y0Q'
# try:
#     download_url = get_video_url(video_id, api_key)
#     print(f"Видео доступно по ссылке: {download_url}")
# except Exception as e:
#     print(str(e))


# video_url = 'https://drive.google.com/uc?export=download&id=1vpMHl2pRc55AmAeVWBH0y2I_nvo7x41H'
#api_key = 'dAyNSrz-6poJsNn-7kgL3HfykbG1XiXOzEjhZQd1Y0Q'
#
# try:
#     result = add_captions_to_video(video_url, api_key, language='Russian')
#     print(f"Видео успешно отправлено на обработку. ID видео: {result['vid']}")
# except Exception as e:
#     print(str(e))