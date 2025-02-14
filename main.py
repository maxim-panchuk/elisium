# from moviepy import *
# import os
# import random
# import re
#
# VIDEO_W, VIDEO_H = 1080, 1920
# offset = int(VIDEO_H * 5/6)
#
# test_text = (
#     "Привет, вот свежий крипто-дайджест! США предлагают регулировать стейблкоины с привязкой к доллару и гособлигациям. "
#     "Дональд Трамп-младший видит в криптовалюте шанс для экономики США. Но настроения на рынке остаются осторожными: "
#     "Bitcoin не удержался выше $105,500, рынок ожидает дальнейшего падения, а его доминирование составляет 62%. Будьте в курсе с нами!"
# )
#
# def pick_random_videos(root_dir="video", num_files=4):
#     files = os.listdir(root_dir)
#     video_files = [f for f in files if f.startswith("video_")]
#     selected = random.sample(video_files, num_files)
#     return [os.path.join(root_dir, fname) for fname in selected]
#
# def process_video(path_to_video, clip_duration=5):
#     return (VideoFileClip(path_to_video)
#             .subclipped(0, clip_duration)
#             .resized((1080, 1920))
#             .with_effects([vfx.FadeIn(1), vfx.FadeOut(1)]))
#
# def process_clip_part(clip_part):
#     temp_clip = TextClip(
#         text=clip_part['captions'],
#         font_size=40,
#         color='white',
#         font='Arial',
#     )
#
#     text_width, text_height = temp_clip.size
#
#     txt_clip = TextClip(
#         text=clip_part['captions'],
#         font_size=40,
#         color='white',
#         font='Arial',
#         method='caption',
#         bg_color='black',
#         margin=(20, 20, 20, 20),
#         size=(1000 if text_width > 1000 else text_width, None)
#     )
#
#     return txt_clip.with_position(("center", offset)).with_start(clip_part['start']).with_end(clip_part['end'])
#
# def parse_srt(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         content = f.read().strip()
#
#     blocks = content.split('\n\n')
#     results = []
#
#     for block in blocks:
#         lines = block.splitlines()
#         if len(lines) < 2:
#             continue
#
#         index_str = lines[0].strip()
#         try:
#             index_num = int(index_str)
#         except ValueError:
#             index_num = None
#
#         time_line = lines[1].strip()
#         match = re.match(r"(\S+) --> (\S+)", time_line)
#         if not match:
#             continue
#
#         start_str = match.group(1).replace(',', '.')
#         end_str = match.group(2).replace(',', '.')
#
#         captions = ' '.join(lines[2:])
#         results.append({
#             'index': index_num,
#             'start': start_str,
#             'end': end_str,
#             'captions': captions
#         })
#     return results
#
# if __name__ == '__main__':
#     audio_clip = AudioFileClip("audio.mp3")
#     audio_clip_duration = audio_clip.duration
#
#     num_video_clips = int(audio_clip_duration // 7) + 1
#
#     caption_list = parse_srt("result.srt")
#     video_paths = pick_random_videos(num_files=num_video_clips)
#
#     clip_list = []
#     prev_video_clip = None
#
#     for i in range(num_video_clips):
#         base_clip = process_video(video_paths[i], 7)
#         if prev_video_clip is not None:
#             base_clip = base_clip.with_start(prev_video_clip.end)
#         prev_video_clip = base_clip
#         clip_list.append(base_clip)
#
#     for caption_block in caption_list:
#         caption_clip = process_clip_part(caption_block)
#         clip_list.append(caption_clip)
#
#     final_clip = CompositeVideoClip(clip_list)
#     final_clip = final_clip.with_audio(audio_clip)
#
#     final_clip.write_videofile("video.mp4", fps=30, codec='libx264', audio_codec='aac')