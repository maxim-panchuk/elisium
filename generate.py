from moviepy import *
import random
import os

from eleven_labs import generate_speech
from subtitlese import make_subtitles

CLIP_DURATION = 5

def pick_random_videos(root_dir="video/boxing", num_files=4):
    files = os.listdir(root_dir)
    video_files = [f for f in files]
    selected = random.sample(video_files, num_files)
    return [os.path.join(root_dir, fname) for fname in selected]


def process_video(path_to_video, clip_duration):
    video_clip = VideoFileClip(path_to_video)
    total_duration = video_clip.duration

    if clip_duration >= total_duration:
        subclip = video_clip.subclipped(0, total_duration)
    else:
        max_start = total_duration - clip_duration
        start_time = random.uniform(0, max_start)
        end_time = start_time + clip_duration
        subclip = video_clip.subclipped(start_time, end_time)

    return (subclip
            .resized((1080, 1920))
            .with_effects([vfx.FadeIn(1), vfx.FadeOut(1)]))

def process_image(path_to_image, clip_duration):
    img_clip = ImageClip(path_to_image, duration=clip_duration)

    scale = min(1080 / img_clip.w, 1920 / img_clip.h)
    scaled_clip = img_clip.resized(scale)

    background = ColorClip(size=(1080, 1920), color=(0, 0, 0))
    background = background.with_duration(clip_duration)

    final_clip = CompositeVideoClip([
        background,
        scaled_clip.with_position(("center", "center"))
    ])

    final_clip = final_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
    return final_clip

def generate_stock_mp4(path_to_mp3, text, saved_images, saved_videos):
    voice_clip = AudioFileClip(path_to_mp3)
    voice_duration = voice_clip.duration
    assert voice_duration > 15

    num_video_clips = int((voice_duration - len(saved_images) * CLIP_DURATION - len(saved_videos) * CLIP_DURATION) // CLIP_DURATION) + 1
    video_paths = pick_random_videos(num_files=num_video_clips)
    video_paths.extend(saved_videos)

    clip_element_paths = saved_images + video_paths
    random.shuffle(clip_element_paths)

    num_clips = len(clip_element_paths)
    clip_list = []
    prev_clip = None

    for i in range(num_clips):
        clip = None
        if clip_element_paths[i].endswith('.mp4'):
            clip = process_video(clip_element_paths[i], CLIP_DURATION)
        else:
            clip = process_image(clip_element_paths[i], CLIP_DURATION)

        if prev_clip is not None:
            clip = clip.with_start(prev_clip.end)

        prev_clip = clip
        clip_list.append(clip)

    clip_list[-1].with_end(voice_duration + 2)

    final_clip = CompositeVideoClip(clip_list)
    subtitles = make_subtitles(text, path_to_mp3)
    final_clip = CompositeVideoClip([final_clip, *subtitles], size=(1080, 1920))

    bg_music_path = "music/Blood-Sweat-and-Tears.mp3"
    bg_clip = AudioFileClip(bg_music_path)
    final_duration = voice_duration + 2
    bg_music_loop = bg_clip.with_effects([afx.AudioLoop(duration=final_duration)]).with_volume_scaled(0.3)

    final_audio = CompositeAudioClip([voice_clip, bg_music_loop])
    final_audio = final_audio.with_duration(final_duration)

    final_clip = final_clip.with_audio(final_audio).with_duration(final_duration)
    final_clip.write_videofile('tmp/composed.mp4', fps=30, codec='libx264', audio_codec='aac')

    return 'tmp/composed.mp4'

def start_pipeline(text, saved_images, saved_videos):
    path_to_mp3 = generate_speech(text)
    path_to_mp4 = generate_stock_mp4(path_to_mp3, text, saved_images, saved_videos)
    print(f'Video saved to :{path_to_mp4}')