from moviepy import *
import random
import os

from google_drive import upload_video
from vadoo import add_captions_to_video, get_video_url, download_video


def pick_random_videos(root_dir="video", num_files=4):
    files = os.listdir(root_dir)
    video_files = [f for f in files if f.startswith("video_")]
    selected = random.sample(video_files, num_files)
    return [os.path.join(root_dir, fname) for fname in selected]

def process_video(path_to_video, clip_duration=5):
    return (VideoFileClip(path_to_video)
            .subclipped(0, clip_duration)
            .resized((1080, 1920))
            .with_effects([vfx.FadeIn(1), vfx.FadeOut(1)]))


def generate_stock_mp4(path_to_mp3):
    audio_clip = AudioFileClip(path_to_mp3)
    audio_clip_duration = audio_clip.duration

    num_video_clips = int(audio_clip_duration // 7) + 1

    video_paths = pick_random_videos(num_files=num_video_clips)

    clip_list = []
    prev_video_clip = None

    for i in range(num_video_clips):
        base_clip = process_video(video_paths[i], 7)
        if prev_video_clip is not None:
            base_clip = base_clip.with_start(prev_video_clip.end)
        prev_video_clip = base_clip
        clip_list.append(base_clip)

    final_clip = CompositeVideoClip(clip_list).with_audio(audio_clip)
    path_to_mp4 = 'video_1.mp4'
    final_clip.write_videofile(path_to_mp4, fps=30, codec='libx264', audio_codec='aac')
    return path_to_mp4

def preprocess_text_via_chatGPT(text):
    return text

def generate_speech_via_google_cloud(text):
    path_to_downloaded_mp3 = 'audio_1.mp3'
    return path_to_downloaded_mp3

test_text = 'Coinbase Derivatives получила одобрение от Комиссии по торговле фьючерсами США на запуск контрактов на Solana и Hedera. Торги начнутся 18 февраля. Это сигнал роста институционального интереса, увеличения ликвидности и новых возможностей для хеджирования и спекуляций. Событие может позитивно повлиять на SOL и HBAR. '
vadoo_ai_api_key = 'dAyNSrz-6poJsNn-7kgL3HfykbG1XiXOzEjhZQd1Y0Q'

def start_pipeline(text):
    text = preprocess_text_via_chatGPT(text)
    path_to_mp3 = generate_speech_via_google_cloud(text)
    path_to_mp4 = generate_stock_mp4(path_to_mp3)
    public_url, direct_download_url = upload_video(path_to_mp4)
    vid = add_captions_to_video(direct_download_url, vadoo_ai_api_key)
    video_captioned_url = get_video_url(vid, vadoo_ai_api_key)
    download_video(video_captioned_url, vadoo_ai_api_key)


if __name__ == '__main__':
    start_pipeline('text')