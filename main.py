from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

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
        if fmt == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            thumbnail = info.get('thumbnail', '')
            
            # Direkt indirme URL'ini al
            if fmt == 'mp3':
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    download_url = audio_formats[-1].get('url', '')
                else:
                    download_url = formats[-1].get('url', '') if formats else ''
            else:
                formats = info.get('formats', [])
                mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
                if mp4_formats:
                    download_url = mp4_formats[-1].get('url', '')
                else:
                    download_url = formats[-1].get('url', '') if formats else ''

        if not download_url:
            return jsonify({"error": "Video URL bulunamadı"}), 400

        return jsonify({
            "success": True,
            "title": title,
            "thumbnail": thumbnail,
            "downloadUrl": download_url,
            "format": fmt
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
