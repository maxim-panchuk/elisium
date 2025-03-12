import os
from flask import Flask, request, jsonify, send_file
import threading

from generate import start_pipeline

app = Flask(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_VIDEO_TYPES = {"video/mp4"}

# A global Lock to limit resource access (only one video generation at a time)
generation_lock = threading.Lock()

@app.errorhandler(Exception)
def handle_exception(e):
    """
    A global error handler that catches any Exception not otherwise handled.
    Returns a JSON with the error message.
    """
    # You can log the exception here (e.g., using app.logger or print)
    return jsonify({
        "error": "An unexpected error occurred.",
        "details": str(e)
    }), 500

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
        path_to_mp4 = start_pipeline(text, saved_images, saved_videos)
        
        return send_file(path_to_mp4, mimetype='video/mp4', as_attachment=True)

    finally:
        # Always release the lock, even if there was a return or an error
        generation_lock.release()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)