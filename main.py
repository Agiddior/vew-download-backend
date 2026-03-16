from flask import Flask, request, jsonify, send_file, Response
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

        if fmt == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]/best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            ext = 'mp3' if fmt == 'mp3' else 'mp4'

        # Dosyayı bul
        final_path = None
        for f in os.listdir('/tmp'):
            if f.startswith(file_id):
                final_path = f"/tmp/{f}"
                break

        if not final_path or not os.path.exists(final_path):
            return jsonify({"error": "Dosya oluşturulamadı"}), 500

        mimetype = 'audio/mpeg' if fmt == 'mp3' else 'video/mp4'

        def cleanup():
            try:
                os.remove(final_path)
            except:
                pass

        response = send_file(
            final_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"{file_id}.{ext}"
        )

        threading.Timer(60, cleanup).start()
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
