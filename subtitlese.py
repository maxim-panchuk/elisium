import json
import re
import math
import subprocess

from moviepy import *

def extract_words(text):
    text_no_punct = re.sub(r'[^\w\sа-яА-ЯёЁ]', '', text, flags=re.UNICODE)
    words = text_no_punct.split()
    return words

def parse_echogarden_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    words_info = []
    for segment in data:
        for sentence in segment.get("timeline", []):
            for word_item in sentence.get("timeline", []):
                if word_item.get("type") == "word":
                    words_info.append({
                        "word": word_item["text"],
                        "start": word_item["startTime"],
                        "end": word_item["endTime"]
                    })
    return words_info

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SUBTITLE_WIDTH = 900
SUBTITLE_LINE_SPACE = 150
SUBTITLE_WORD_SPACE = 20
HIGHLIGHT_COLOR = 'red'

def transcribe_audio(path_to_audio):
    cmd = [
        'echogarden',
        'transcribe',
        path_to_audio,
        'result.json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Результат force-alignment в файле result.json")
    else:
        print(f"Ошибка force-alignment (код {result.returncode}) при запуске echogarden")
        return None
    return 'result.json'

def calc_words_widths(words):
    word_widths = []
    for word in words:
        txt = word['word']
        clip = TextClip(
            text=txt,
            font='BebasNeue.ttf',
            font_size=140,
            color='white',
            margin=(None, 30),
            stroke_color='black',
            stroke_width=2
        )
        word_widths.append(clip.w)
    return word_widths

def calc_words_positions(words, word_widths):
    start_x = (VIDEO_WIDTH - SUBTITLE_WIDTH) / 2
    start_y = VIDEO_HEIGHT / 3 * 2

    curr_x = start_x
    curr_y = start_y
    positions_and_size = []

    for i in range(len(words)):
        curr_word_width = word_widths[i]
        font_size = 140
        if curr_x + curr_word_width - start_x > SUBTITLE_WIDTH:
            curr_x = start_x
            curr_y += SUBTITLE_LINE_SPACE
            if curr_x + curr_word_width > SUBTITLE_WIDTH:
                font_size = 105

        positions_and_size.append((curr_x, curr_y, font_size))

        curr_x += curr_word_width + SUBTITLE_WORD_SPACE

    return positions_and_size

def reformat_src_word_list(words_info):
    src_word_list = []
    for word in words_info:
        src_word_list.append(word['word'])
    return src_word_list

def make_subtitles(text, path_to_audio):
    path_to_transcription = transcribe_audio(path_to_audio)
    words_info = parse_echogarden_json(path_to_transcription)
    src_words_list = extract_words(text)

    if len(src_words_list) != len(words_info):
        src_words_list = reformat_src_word_list(words_info)

    i = 0
    n = len(words_info)
    all_clips = []

    while i < n:
        group = words_info[i: i + 4]
        for j in range(len(group)):
            group[j]['word'] = src_words_list[j + i].upper()

        i += 4

        group_end = max(w['end'] for w in group)
        words_widths = calc_words_widths(group)
        words_positions = calc_words_positions(group, words_widths)

        for idx, word in enumerate(group):
            word_text = word['word']
            start_time = word['start']
            end_time = word['end']

            pos_x, pos_y, font_size = words_positions[idx]

            white_clip = (
                TextClip(
                    text=word_text,
                    font = 'BebasNeue.ttf',
                    font_size=font_size,
                    color='white',
                    margin=(None, 30),
                    stroke_color='black',
                    stroke_width=2,
                )
                .with_position((pos_x, pos_y))
                .with_start(start_time)
                .with_end(group_end)
            )

            highlight_clip = (
                TextClip(
                    text=word_text,
                    font='BebasNeue.ttf',
                    font_size=font_size,
                    color=HIGHLIGHT_COLOR,
                    margin=(None, 30),
                    stroke_color='black',
                    stroke_width=2
                )
                .with_position((pos_x, pos_y))
                .with_start(start_time)
                .with_end(end_time)
            )

            all_clips.append(white_clip)
            all_clips.append(highlight_clip)

    return all_clips