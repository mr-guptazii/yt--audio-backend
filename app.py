from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/get_stream', methods=['POST'])
def get_stream():
    data = request.json or {}
    playlist_url = data.get("url")
    
    if not playlist_url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_flat': False,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            tracks = []
            
            if 'entries' in info:
                entries = info['entries']
            else:
                entries = [info]

            for entry in entries:
                if entry:
                    tracks.append({
                        "title": entry.get("title", "Unknown Title"),
                        "download_url": entry.get("url")
                    })
                    
            return jsonify({"tracks": tracks})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
