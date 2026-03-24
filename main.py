from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import threading

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

        ydl_opts = {
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }

        if fmt == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'best[ext=mp4]/best'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = 'mp3' if fmt == 'mp3' else 'mp4'
            title = info.get('title', 'video')

        final_path = None
        for f in os.listdir('/tmp'):
            if f.startswith(file_id):
                final_path = f"/tmp/{f}"
                break

        if not final_path or not os.path.exists(final_path):
            return jsonify({"error": "Dosya bulunamadı"}), 500

        file_size = os.path.getsize(final_path)
        if file_size < 1000:
            return jsonify({"error": "İndirilen dosya bozuk"}), 500

        mimetype = 'audio/mpeg' if fmt == 'mp3' else 'video/mp4'

        def cleanup():
            try:
                os.remove(final_path)
            except:
                pass

        threading.Timer(120, cleanup).start()

        return send_file(
            final_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"{file_id}.{ext}"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
