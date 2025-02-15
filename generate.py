from moviepy import *
import random
import os

from eleven_labs import generate_speech
from google_drive import upload_video
from vadoo import add_captions_to_video, get_video_url, download_video

clip_duration = 5

def pick_random_videos(root_dir="video/boxing", num_files=4):
    files = os.listdir(root_dir)
    video_files = [f for f in files if f.startswith("video_")]
    selected = random.sample(video_files, num_files)
    return [os.path.join(root_dir, fname) for fname in selected]

def process_video(path_to_video, clip_duration):
    return (VideoFileClip(path_to_video)
            .subclipped(0, clip_duration)
            .resized((1080, 1920))
            .with_effects([vfx.FadeIn(1), vfx.FadeOut(1)]))

def process_image(path_to_image, clip_duration):
    return(ImageClip(path_to_image)
           .with_duration(clip_duration)
           .resized((1080, 1920))
           .with_effects([vfx.FadeIn(1)]))

def get_paths_to_images():
    return ['images/image_1.jpg', 'images/image_2.jpg']


def generate_stock_mp4(path_to_mp3):
    audio_clip = AudioFileClip(path_to_mp3)
    audio_clip_duration = audio_clip.duration
    assert audio_clip_duration > 15

    image_paths = get_paths_to_images()
    num_video_clips = int((audio_clip_duration - len(image_paths) * clip_duration) // clip_duration) + 1
    video_paths = pick_random_videos(num_files=num_video_clips)

    clip_element_paths = image_paths + video_paths
    random.shuffle(clip_element_paths)

    num_clips = len(clip_element_paths)
    clip_list = []
    prev_clip = None

    for i in range(num_clips):
        clip = None
        if clip_element_paths[i].endswith('.mp4'):
            clip = process_video(clip_element_paths[i], clip_duration)
        else:
            clip = process_image(clip_element_paths[i], clip_duration)

        if prev_clip is not None:
            clip = clip.with_start(prev_clip.end)

        prev_clip = clip
        clip_list.append(clip)

    clip_list[-1].with_end(audio_clip_duration + 2)

    final_clip = CompositeVideoClip(clip_list).with_audio(audio_clip)
    final_clip.write_videofile('tmp/composed.mp4', fps=30, codec='libx264', audio_codec='aac')
    return 'tmp/composed.mp4'

vadoo_ai_api_key = 'dAyNSrz-6poJsNn-7kgL3HfykbG1XiXOzEjhZQd1Y0Q'

def start_pipeline(text):
    path_to_mp3 = generate_speech(text)
    path_to_mp4 = generate_stock_mp4(path_to_mp3)
    public_url, direct_download_url = upload_video(path_to_mp4)
    vid = add_captions_to_video(direct_download_url, vadoo_ai_api_key)
    video_captioned_url = get_video_url(vid, vadoo_ai_api_key)
    download_video(video_captioned_url, vadoo_ai_api_key)


if __name__ == '__main__':
    start_pipeline('Бокс продолжает набирать популярность, привлекая большие деньги и неожиданных участников. Джейк Пол, известный блогер и боец, недавно устроил поединок с Майком Тайсоном. Его брат Логан, менее известный, но тоже яркая фигура в соцсетях, вызвал на бой Лионеля Месси. Причиной стал конфликт из-за спортивных напитков. Логан обвиняет Месси в нарушении товарных знаков и предлагает решить разногласия на ринге. Несмотря на шумиху, бой маловероятен: разница в росте и весе слишком велика. Интрига остаётся, но поединок пока невозможен.')