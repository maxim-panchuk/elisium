import json
import re
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

def make_subtitles(text):
    video_width = 1080
    video_height = 1920
    highlight_color = 'red'

    words_info = parse_echogarden_json('./result.json')
    words_list = extract_words(text)

    i = 0
    n = len(words_info)
    all_clips = []

    spacing = 20

    while i < n:
        group = words_info[i: i + 4]
        for j in range(len(group)):
            group[j]['word'] = words_list[j + i]
        i += 4

        group_end = max(w['end'] for w in group)
        word_widths = []
        for w in group:
            txt = w['word'].upper()
            tmp_clip = TextClip(text=txt,
                                font='/Users/mpanchuk/Desktop/folders/ttv/BebasNeue.ttf',
                                font_size=140,
                                color='white',
                                method='label',
                                margin=(None, 30),
                                stroke_color='black',
                                stroke_width=2)
            word_widths.append(tmp_clip.w)

        total_width = sum(word_widths) + spacing * (len(group) - 1)

        if total_width > 800:
            left_x = (video_width - total_width / 2) / 4
        else:
            left_x = (video_width - total_width) / 2.0


        offset_x = 0
        pos_y = video_height / 3 * 2

        for idx, w in enumerate(group):
            word_text = w['word'].lower()
            start_time = w['start']
            end_time = w['end']
            current_width = word_widths[idx]

            pos_x = left_x + offset_x
            if pos_x + word_widths[idx] > video_width:
                pos_y += 150
                pos_x = (video_width - word_widths[idx]) / 2

            if total_width > 800 and (idx == 2):
                pos_y += 150

            white_clip = (TextClip(text=word_text,
                                   font='/Users/mpanchuk/Desktop/folders/ttv/BebasNeue.ttf',
                                   font_size=140,
                                   color='white',
                                   method='label',
                                   margin=(None, 30),
                                   stroke_color='black',
                                   stroke_width=2)
                          .with_position((pos_x, pos_y))
                          .with_start(start_time)
                          .with_end(group_end)
                          )

            highlight_clip = (TextClip(text=word_text,
                                       font='/Users/mpanchuk/Desktop/folders/ttv/BebasNeue.ttf',
                                       font_size=140,
                                       color=highlight_color,
                                       method='label',
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

            if 800 < total_width < 1000 and idx == 1:
                offset_x = 70
            elif total_width > 1000 and idx == 1:
                offset_x = 0
            else:
                offset_x += current_width + spacing

    return all_clips