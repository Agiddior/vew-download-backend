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
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            thumbnail = info.get('thumbnail', '')
            formats = info.get('formats', [])

            if fmt == 'mp3':
                # En iyi ses formatını bul
                audio_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' 
                    and f.get('vcodec') == 'none'
                    and f.get('url')
                ]
                if audio_formats:
                    audio_formats.sort(key=lambda x: x.get('abr') or 0, reverse=True)
                    download_url = audio_formats[0]['url']
                else:
                    # Ses+video birleşik format
                    combined = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]
                    if combined:
                        download_url = combined[-1]['url']
                    else:
                        return jsonify({"error": "Ses formatı bulunamadı"}), 400
            else:
                # Ses+video birleşik mp4 formatı bul
                mp4_combined = [
                    f for f in formats
                    if f.get('ext') == 'mp4'
                    and f.get('vcodec') != 'none'
                    and f.get('acodec') != 'none'
                    and f.get('url')
                ]
                
                if mp4_combined:
                    # En yüksek kaliteyi seç
                    mp4_combined.sort(key=lambda x: (x.get('height') or 0), reverse=True)
                    download_url = mp4_combined[0]['url']
                else:
                    # Birleşik format yok, en iyi genel formatı al
                    all_combined = [
                        f for f in formats
                        if f.get('vcodec') != 'none'
                        and f.get('acodec') != 'none'
                        and f.get('url')
                    ]
                    if all_combined:
                        all_combined.sort(key=lambda x: (x.get('height') or 0), reverse=True)
                        download_url = all_combined[0]['url']
                    else:
                        # Son çare - herhangi bir format
                        valid = [f for f in formats if f.get('url')]
                        if valid:
                            download_url = valid[-1]['url']
                        else:
                            return jsonify({"error": "İndirilebilir format bulunamadı"}), 400

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
