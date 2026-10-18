from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import re
import os
import glob
import shutil
import tempfile
import yt_dlp

app = Flask(name)

CORS(
app,
resources={r"/api/*": {"origins": "https://mush7860.github.io"}}
)

REEL_PATTERN = re.compile(
r"^https?://(www.)?instagram.com/reel/[A-Za-z0-9_-]+/?(?.*)?$"
)

@app.route("/")
def home():
return jsonify({
"status": "online",
"message": "Insta Reel Saver server is running!"
})

@app.route("/health")
def health():
return jsonify({"status": "ok"})

@app.route("/api/check", methods=["POST"])
def check_reel():
data = request.get_json(silent=True) or {}
url = data.get("url", "").strip()

if not REEL_PATTERN.match(url):
    return jsonify({
        "success": False,
        "message": "Please enter a valid Instagram Reel URL."
    }), 400

return jsonify({
    "success": True,
    "message": "Reel link is valid. You can try downloading it if you have permission."
})

@app.route("/api/download", methods=["POST"])
def download_reel():
data = request.get_json(silent=True) or {}
url = data.get("url", "").strip()

if not REEL_PATTERN.match(url):
    return jsonify({
        "success": False,
        "message": "Please enter a valid Instagram Reel URL."
    }), 400

temp_dir = tempfile.mkdtemp(prefix="reel_")

try:
    options = {
        "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "max_filesize": 100 * 1024 * 1024
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.download([url])

    files = [
        path for path in glob.glob(os.path.join(temp_dir, "*"))
        if os.path.isfile(path) and not path.endswith((".part", ".ytdl"))
    ]

    if not files:
        raise RuntimeError("No downloadable video file was produced.")

    video_path = max(files, key=os.path.getsize)

    response = send_file(
        video_path,
        as_attachment=True,
        download_name=os.path.basename(video_path),
        mimetype="video/mp4" if video_path.lower().endswith(".mp4")
        else "application/octet-stream"
    )

    response.call_on_close(
        lambda: shutil.rmtree(temp_dir, ignore_errors=True)
    )
    return response

except Exception:
    shutil.rmtree(temp_dir, ignore_errors=True)
    return jsonify({
        "success": False,
        "message": "Download failed. This Reel may not be available through supported public access."
    }), 400

if name == "main":
app.run(host="0.0.0.0", port=10000)
