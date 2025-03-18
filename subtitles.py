import json
import re
import subprocess
from moviepy import *
import os
from eleven_labs import transcribe_speech
# 1. Global constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

SUBTITLE_WIDTH = 900
SUBTITLE_LINE_SPACING = 150       # Distance between subtitle lines
SUBTITLE_WORD_SPACING = 20        # Distance between words
FONT_PATH = 'BebasNeue.ttf'
FONT_SIZE_DEFAULT = 120
FONT_SIZE_FALLBACK = 105          # Fallback font size for very long words
HIGHLIGHT_COLOR = 'red'
WHITE_COLOR = 'white'

RESULT_JSON_FILE = 'result.json'  # The file where echogarden will save the result


# 2. Utility functions (regex, subprocess, etc.)

def parse_elevenlabs_json(file_path: str) -> list[dict]:
    """
    Reads an ElevenLabs format JSON file and extracts a list of words
    with start and end timestamps.
    
    Only considers elements of type "word" and ignores spaces (type "spacing").
    
    Returns:
    [
      {"word": <str>, "start": <float>, "end": <float>},
      ...
    ]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    words_info = []
    
    for word_item in data.get("words", []):
        if word_item.get("type") == "word":
            words_info.append({
                "word": word_item["text"],
                "start": word_item["start"],
                "end": word_item["end"]
            })
    
    return words_info


# 3. Functions for forming subtitles (TextClip)

def calculate_word_widths(words: list[dict]) -> list[int]:
    """
    Creates a TextClip for each dictionary like {"word": "..."}
    and retrieves its width (.w).
    Returns a list of widths in order.
    """
    widths = []
    for w in words:
        clip = TextClip(
            text=w["word"],
            font=FONT_PATH,
            font_size=FONT_SIZE_DEFAULT,
            color=WHITE_COLOR,
            margin=(None, 30),
            stroke_color='black',
            stroke_width=2
        )
        widths.append(clip.w)
    return widths


def calculate_positions_and_sizes(words: list[dict], widths: list[int]) -> list[tuple]:
    """
    Calculates (x, y, fontsize) for each word.
    - Start from the left edge of the SUBTITLE_WIDTH area,
      which is centered along the X-axis.
    - If a word does not fit in the remaining width, move to a new line
      and reduce the font size if necessary.

    Returns a list of tuples (pos_x, pos_y, font_size).
    """
    start_x = (VIDEO_WIDTH - SUBTITLE_WIDTH) / 2
    #start_y = VIDEO_HEIGHT * 2/3  # Roughly the lower third
    start_y = VIDEO_HEIGHT * 1/2  # Roughly the lower third
    positions_and_sizes = []

    current_x = start_x
    current_y = start_y

    for w, w_width in zip(words, widths):
        font_size = FONT_SIZE_DEFAULT

        # Check if this word would exceed SUBTITLE_WIDTH
        if (current_x + w_width) - start_x > SUBTITLE_WIDTH:
            # Start a new line
            current_x = start_x
            current_y += SUBTITLE_LINE_SPACING

            # Potentially reduce font size if the word is still too wide
            if w_width > SUBTITLE_WIDTH:
                font_size = FONT_SIZE_FALLBACK

        positions_and_sizes.append((current_x, current_y, font_size))
        current_x += w_width + SUBTITLE_WORD_SPACING

    return positions_and_sizes


def create_text_clip(
    text: str,
    pos_x: float,
    pos_y: float,
    font_size: int,
    color: str,
    start: float,
    end: float
) -> TextClip:
    """
    A helper function to create a TextClip with the specified text,
    font, position, time interval, and color.
    """
    return (TextClip(
                text=text,
                font=FONT_PATH,
                font_size=font_size,
                color=color,
                margin=(None, 30),
                stroke_color='black',
                stroke_width=2
            )
            .with_position((pos_x, pos_y))
            .with_start(start)
            .with_end(end)
    )


def make_subtitles(text: str, path_to_voice: str) -> list[TextClip]:
    """
    1. Runs echogarden to get a JSON (result.json) with word timestamps.
    2. Compares the number of words in the input 'text' with the number in JSON:
       - If they do not match, use the words from the JSON directly.
    3. Splits words into groups of 4 and forms 'karaoke' subtitles:
       - A white clip (from the moment the word starts until the end of the group)
       - A highlight clip (only for the duration of that word)
    4. Returns a list of all TextClips, ready to be added to a CompositeVideoClip.
    """
    # Step 1: Transcribe / force-align
    path_to_transcription = transcribe_speech(path_to_voice)
    if not path_to_transcription:
        return []

    words_info = parse_elevenlabs_json(path_to_transcription)

    all_clips = []

    # Step 3: Group words by 4
    total_words = len(words_info)
    if total_words == 0:
        raise ValueError("No words found in transcription")
    
    i = 0
    while i < total_words:
        group = words_info[i: i + 4]

        i += 4
        group_end = max(w['end'] for w in group)

        # Calculate widths
        widths = calculate_word_widths(group)
        # Calculate positions
        positions_and_sizes = calculate_positions_and_sizes(group, widths)

        # For each word, create 2 clips (white and highlight)
        for idx, word_data in enumerate(group):
            word_text = word_data['word']
            start_time = word_data['start']
            end_time = word_data['end']

            pos_x, pos_y, font_size = positions_and_sizes[idx]

            # White clip: from the start of the word to the end of the group
            white_clip = create_text_clip(
                text=word_text,
                pos_x=pos_x,
                pos_y=pos_y,
                font_size=font_size,
                color=WHITE_COLOR,
                start=start_time,
                end=group_end
            )

            # Highlight clip: from the start of the word until it ends
            highlight_clip = create_text_clip(
                text=word_text,
                pos_x=pos_x,
                pos_y=pos_y,
                font_size=font_size,
                color=HIGHLIGHT_COLOR,
                start=start_time,
                end=end_time
            )

            all_clips.append(white_clip)
            all_clips.append(highlight_clip)

    return all_clips