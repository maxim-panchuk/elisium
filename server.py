import os
from flask import Flask, request, jsonify

from generate import start_pipeline

app = Flask(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_VIDEO_TYPES = {"video/mp4"}

@app.route('/generate', methods=['POST'])
def generate():
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

    start_pipeline(text, saved_images, saved_videos)
    return jsonify({'success': 'Video generation successful'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)