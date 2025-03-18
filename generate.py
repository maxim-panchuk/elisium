import random
import os
from moviepy import (
    VideoFileClip,
    ImageClip,
    ColorClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    vfx,
    afx
)

from eleven_labs import generate_speech
from subtitles import make_subtitles
from config import config
import cv2

def pick_random_videos(root_dir="video/boxing", num_files=4):
    """
    Selects 'num_files' random videos from the 'root_dir' directory
    and returns a list of their paths.
    """
    files = os.listdir(root_dir)
    video_files = [f for f in files]
    selected = random.sample(video_files, num_files)
    return [os.path.join(root_dir, fname) for fname in selected]

def pick_random_music(root_dir="music"):
    """
    Selects random music from root_dir directory
    """
    files = os.listdir(root_dir)
    music_files = [f for f in files]
    selected = random.sample(music_files, 1)
    return os.path.join(root_dir, selected[0])

def blur_video(video_to_blur) -> str:
    BLURRED_VIDEO_PATH = 'tmp/blurred_video.mp4'
    TO_BLUR_VIDEO_PATH = 'tmp/video_to_blur.mp4'

    video_to_blur.write_videofile('tmp/video_to_blur.mp4', fps=30, codec='libx264', audio_codec='aac')

    cap = cv2.VideoCapture(TO_BLUR_VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(BLURRED_VIDEO_PATH, fourcc, fps, (width, height))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        blurred_frame = cv2.GaussianBlur(frame, (99, 99), 0)
        
        out.write(blurred_frame)

    cap.release()
    out.release()
    print(f'blurred video saved to {BLURRED_VIDEO_PATH}')
    video_clip = VideoFileClip(BLURRED_VIDEO_PATH)
    return video_clip

def process_video(path_to_video, clip_duration):
    """
    Loads a video from 'path_to_video', extracts a random subclip of length 'clip_duration',
    resizes it to 1080x1920, and adds fade-in/out effects.
    Returns a VideoClip object.
    """

    video_clip = VideoFileClip(path_to_video)
    total_duration = video_clip.duration

    if clip_duration >= total_duration:
        start_time = 0
        end_time = total_duration
    else:
        max_start = total_duration - clip_duration
        start_time = random.uniform(0, max_start)
        end_time = start_time + clip_duration

    subclip = video_clip.subclipped(start_time, end_time)

    scale = min(1080 / video_clip.w, 1920 / video_clip.h)
    scaled_clip = subclip.resized(scale)

    if scaled_clip.w < 1080 or scaled_clip.h < 1920:
        background = subclip.resized((1080, 1920))
        blurred_background = blur_video(background) 
        
        final_clip = CompositeVideoClip([
            blurred_background,
            scaled_clip.with_position(("center", "center"))
        ])
    else:
        final_clip = scaled_clip

    return final_clip

def blur_image(path_to_image):
    BLURRED_IMAGE_PATH = 'tmp/blurred_image.png'

    image = cv2.imread(path_to_image)
    image = cv2.resize(image, (1080, 1920))
    blurred_image = cv2.GaussianBlur(image, (99, 99), 0)
    cv2.imwrite(BLURRED_IMAGE_PATH, blurred_image)
    return BLURRED_IMAGE_PATH

def process_image(path_to_image, clip_duration):
    """
    Loads an image from 'path_to_image', creates an ImageClip of 'clip_duration',
    centers it on a 1080x1920 black background, and adds fade-in/out effects.
    Returns a VideoClip object representing that image clip.
    """
    img_clip = ImageClip(path_to_image, duration=clip_duration)

    scale = min(1080 / img_clip.w, 1920 / img_clip.h)
    scaled_clip = img_clip.resized(scale)

    background_path = blur_image(path_to_image)
    background = ImageClip(background_path, duration=clip_duration)

    final_clip = CompositeVideoClip([
        background,
        scaled_clip.with_position(("center", "center"))
    ])

    final_clip = (
        final_clip
        .with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
    )
    return final_clip

def generate_stock_mp4(path_to_mp3, text, saved_images, saved_videos):
    """
    1. Loads the voice audio (path_to_mp3) and measures its duration.
    2. Based on the voice duration, calculates how many random videos to pick
       (excluding the user-uploaded videos).
    3. Shuffles all clips (images + videos), creates subclips, and aligns them in a timeline.
    4. Adds subtitles (make_subtitles) overlay, plus background music with volume scaled.
    5. Outputs the final video to 'tmp/composed.mp4' and returns its path.
    """
    voice_clip = AudioFileClip(path_to_mp3)
    voice_duration = voice_clip.duration
    assert voice_duration > config.min_voice_duration, "Voice clip must be at least 10 seconds long."

    # Calculate how many random videos we need
    num_video_clips = int((voice_duration - len(saved_images) * config.clip_duration
                           - len(saved_videos) * config.clip_duration) // config.clip_duration) + 1
    
    if num_video_clips < 0:
        raise ValueError("voice duration is too short, load less images or videos")
    
    video_paths = pick_random_videos(num_files=num_video_clips)

    # Extend the list of videos with user-uploaded videos
    video_paths.extend(saved_videos)

    # Combine images with video paths, then shuffle
    clip_element_paths = saved_images + video_paths
    random.shuffle(clip_element_paths)

    # Build a list of subclips in sequence
    clip_list = []
    prev_clip = None

    for path in clip_element_paths:
        if path.endswith('.mp4') or path.endswith('.MP4'):
            clip = process_video(path, config.clip_duration)
        else:
            clip = process_image(path, config.clip_duration)

        if prev_clip is not None:
            clip = clip.with_start(prev_clip.end)

        prev_clip = clip
        clip_list.append(clip)

    # Ensure the last clip doesn't exceed voice duration
    clip_list[-1].with_end(voice_duration + 2)

    final_clip = CompositeVideoClip(clip_list)

    # Generate subtitles and overlay them
    subtitles = make_subtitles(text, path_to_mp3)
    final_clip = CompositeVideoClip([final_clip, *subtitles], size=(1080, 1920))

    # Add background music
    bg_music_path = pick_random_music()
    bg_clip = AudioFileClip(bg_music_path)

    final_duration = voice_duration + 2
    bg_music_loop = bg_clip.with_effects([afx.AudioLoop(duration=final_duration)]).with_volume_scaled(0.3)

    # Combine the voice-over and background music
    final_audio = CompositeAudioClip([voice_clip, bg_music_loop])
    final_audio = final_audio.with_duration(final_duration)

    final_clip = final_clip.with_audio(final_audio).with_duration(final_duration)
    final_clip.write_videofile('tmp/composed.mp4', fps=30, codec='libx264', audio_codec='aac')

    return 'tmp/composed.mp4'

def start_pipeline(text, saved_images, saved_videos):
    """
    1. Generates speech from text (TTS) and obtains path to the audio file (path_to_mp3).
    2. Generates a final video using 'generate_stock_mp4'.
    3. Prints the output path of the composed video.
    """
    # Проверяем количество слов в тексте
    word_count = len(text.split())
    
    if word_count < config.min_words_count:
        raise ValueError(f"Текст слишком короткий. Минимальное количество слов: {config.min_words_count}, получено: {word_count}")
    
    if hasattr(config, 'max_words_count') and word_count > config.max_words_count:
        raise ValueError(f"Текст слишком длинный. Максимальное количество слов: {config.max_words_count}, получено: {word_count}")
    
    path_to_mp3 = generate_speech(text)
    path_to_mp4 = generate_stock_mp4(path_to_mp3, text, saved_images, saved_videos)
    return path_to_mp4