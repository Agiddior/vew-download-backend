from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"status": "Vew Download Backend çalışıyor! 🚀"})

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    fmt = data.get('format', 'mp4')

    if not url:
        return jsonify({"error": "URL gerekli"}), 400

    try:
        file_id = str(uuid.uuid4())
        output_path = f"/tmp/{file_id}.%(ext)s"

        if fmt == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'quiet': True,
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_path,
                'quiet': True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            ext = 'mp3' if fmt == 'mp3' else info.get('ext', 'mp4')
            thumbnail = info.get('thumbnail', '')

        final_path = f"/tmp/{file_id}.{ext}"

        if not os.path.exists(final_path):
            # Dosyayı bul
            for f in os.listdir('/tmp'):
                if f.startswith(file_id):
                    final_path = f"/tmp/{f}"
                    break

        file_size = os.path.getsize(final_path)
        file_size_mb = f"{round(file_size / 1024 / 1024, 1)} MB"

        return send_file(
            final_path,
            as_attachment=True,
            download_name=f"{title}.{ext}",
            mimetype='video/mp4' if ext == 'mp4' else 'audio/mpeg'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
