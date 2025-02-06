from moviepy import *
import os
import random
import math
import re

VIDEO_W, VIDEO_H = 1080, 1920
offset = int(VIDEO_H * 5/6)

test_text = (
    "Ончейн-мемы страдают от низкой ликвидности, что приводит к их быстрому падению. "
    "Во времена Ethereum, ликвидность была выше, в отличие от Solana, где монеты легко пампятся, "
    "но также и резко падают. Инвесторы часто ждут отскока, но сталкиваются с ещё большими потерями. "
    "Важно понимать, что продажа на пике падения может спасти половину ваших инвестиций. "
    "Большинство монет не возвращаются к предыдущим высотам, и ждать второго пампа — рискованно. "
    "Ликвидность — ключевой фактор, и в крипте важно быть готовым к переменам."
)

# def split_text(text, parts_num):
#     words = text.split()
#     total_words = len(words)
#
#     part_size = math.ceil(total_words / parts_num)
#
#     parts = []
#     start_index = 0
#
#     for i in range(parts_num):
#         end_index = start_index + part_size
#         if i == parts_num - 1:
#             end_index = total_words
#
#         chunk_words = words[start_index:end_index]
#         start_index = end_index
#
#         lines = []
#         line_size = 10
#         idx = 0
#
#         while idx < len(chunk_words):
#             line_slice = chunk_words[idx:idx + line_size]
#             lines.append(' '.join(line_slice))
#             idx += line_size
#
#         parts.append(lines)
#
#     return parts

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

# def process_text_part(part_lines, total_duration=5):
#     text_clips = []
#     if not part_lines:
#         return text_clips
#
#     line_duration = total_duration / len(part_lines)
#
#     current_start = 0
#     for line in part_lines:
#         txt_clip = (TextClip(text=line,
#                              font_size=40,
#                              color='yellow',
#                              bg_color='black',
#                              font='Arial',
#                              method='caption',
#                              size=(1000, None))
#                     .with_position(('center', offset))
#                     .with_start(current_start)
#                     .with_duration(line_duration))
#         text_clips.append(txt_clip)
#         current_start += line_duration
#
#     return text_clips

# def tts_run(text):
#     tts = gTTS(text, lang='ru')
#     tts.save("test.mp3")

def process_clip_part(clip_part):
    return TextClip(
        text=clip_part['captions'],
        font_size=40,
        color='white',
        margin=(20, 20, 20, 20),
        bg_color='black',
        font='Arial',
        method='caption',
        size=(1000, None)
    ).with_position(('center', offset)).with_start(clip_part['start']).with_end(clip_part['end'])

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    blocks = content.split('\n\n')
    results = []

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 2:
            continue

        index_str = lines[0].strip()
        try:
            index_num = int(index_str)
        except ValueError:
            index_num = None

        time_line = lines[1].strip()
        match = re.match(r"(\S+) --> (\S+)", time_line)
        if not match:
            continue

        start_str = match.group(1).replace(',', '.')
        end_str = match.group(2).replace(',', '.')

        captions = ' '.join(lines[2:])
        results.append({
            'index': index_num,
            'start': start_str,
            'end': end_str,
            'captions': captions
        })
    return results

if __name__ == '__main__':
    audio_clip = AudioFileClip("output.mp3")
    audio_clip_duration = audio_clip.duration

    num_video_clips = int(audio_clip_duration // 7) + 1

    caption_list = parse_srt("result.srt")
    video_paths = pick_random_videos(num_files=num_video_clips)

    clip_list = []
    prev_video_clip = None
    # for i in range(num_video_clips):
    #     base_clip = process_video(video_paths[i], 7)
    #     caption_clip_part = caption_list[i]
    #     caption_clip = process_clip_part(caption_clip_part)
    #
    #     if prev_video_clip is not None:
    #         base_clip = base_clip.with_start(prev_video_clip.end)
    #
    #     prev_video_clip = base_clip
    #
    #     clip_list.extend([base_clip, caption_clip])

    for i in range(num_video_clips):
        base_clip = process_video(video_paths[i], 7)
        if prev_video_clip is not None:
            base_clip = base_clip.with_start(prev_video_clip.end)
        prev_video_clip = base_clip
        clip_list.append(base_clip)

    for caption_block in caption_list:
        caption_clip = process_clip_part(caption_block)
        clip_list.append(caption_clip)

    final_clip = CompositeVideoClip(clip_list)
    final_clip = final_clip.with_audio(audio_clip)

    final_clip.write_videofile("test.mp4", fps=30, codec='libx264', audio_codec='aac')

# if __name__ == '__main__':
#     tts_run(test_text)
#
#     audio_clip = AudioFileClip("test.mp3")
#     audio_clip_duration = audio_clip.duration
#
#     num_video_clips = int(audio_clip_duration // 7) + 1
#
#     text_parts = split_text(test_text, num_video_clips)
#
#     video_paths = pick_random_videos(num_files=num_video_clips)
#
#     clip_list = []
#     for i in range(num_video_clips):
#         base_clip = process_video(video_paths[i], 7)
#
#         text_clip = text_parts[i]
#         text_overlays = process_text_part(text_clip, total_duration=base_clip.duration)
#         composed_clip = CompositeVideoClip([base_clip, *text_overlays])
#         clip_list.append(composed_clip)
#
#     final_clip = concatenate_videoclips(clip_list)
#     final_clip = final_clip.with_audio(audio_clip)
#
#     final_clip.write_videofile("result.mp4", fps=30, audio_codec='aac', codec='libx264')