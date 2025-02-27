import os
from flask import Flask, request, jsonify
import threading

from generate import start_pipeline

app = Flask(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_VIDEO_TYPES = {"video/mp4"}

# A global Lock to limit resource access (only one video generation at a time)
generation_lock = threading.Lock()


@app.route('/generate', methods=['POST'])
def generate():
    """
    Handles a request to generate a video.
    If the server is already busy (the lock is "taken"), it immediately returns a 429 (Too Many Requests)
    or another status indicating "try again later".
    """
    # Attempt to acquire the lock without waiting (non-blocking).
    locked = generation_lock.acquire(blocking=False)
    if not locked:
        # Could not acquire the lock, meaning the server is currently busy
        return jsonify({"error": "The server is busy generating another video. Please try again later."}), 429

    try:
        # If we are here, it means the lock was successfully acquired,
        # and we can process the request.
        images_count = 0
        videos_count = 0

        text = request.form.get('text', None)

        saved_images = []
        saved_videos = []

        for file_key in request.files:
            file_obj = request.files[file_key]
            if not file_obj or file_obj.filename == '':
                continue

            mime_type = file_obj.content_type

            if mime_type in ALLOWED_IMAGE_TYPES:
                if images_count >= 3:
                    return jsonify({"error": "Too many images, max 3"}), 400
                images_count += 1
                filename = file_obj.filename
                save_path = os.path.join('uploads', 'images', filename)
                file_obj.save(save_path)
                saved_images.append(save_path)

            elif mime_type in ALLOWED_VIDEO_TYPES:
                if videos_count >= 2:
                    return jsonify({"error": "Too many videos, max 2"}), 400
                videos_count += 1
                filename = file_obj.filename
                save_path = os.path.join('uploads', 'videos', filename)
                file_obj.save(save_path)
                saved_videos.append(save_path)

            else:
                return jsonify({"error": f"Unsupported mime type: {mime_type}"}), 400

        # Invoke the function that takes a significant amount of time to generate the video
        start_pipeline(text, saved_images, saved_videos)

        return jsonify({'success': 'Video generation successful'}), 200

    finally:
        # Always release the lock, even if there was a return or an error
        generation_lock.release()


if __name__ == '__main__':
    """
    Launches the server on 0.0.0.0:8080.
    If two parallel requests arrive, the second returns 429 while
    the first one has not finished yet (thanks to the Lock).
    """
    os.makedirs('uploads/images', exist_ok=True)
    os.makedirs('uploads/videos', exist_ok=True)

    app.run(host='0.0.0.0', port=8080)