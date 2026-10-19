from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import re
import os
import glob
import shutil
import tempfile

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "https://mush7860.github.io"
        }
    }
)


def valid_url(url):
    pattern = (
        r"^https?://(www\.)?instagram\.com/"
        r"(reel|reels|p)/[A-Za-z0-9_-]+/?(\?.*)?$"
    )
    return bool(re.match(pattern, url))


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

    if not valid_url(url):
        return jsonify({
            "success": False,
            "message": "Please enter a valid Instagram Reel URL."
        }), 400

    return jsonify({
        "success": True,
        "message": "Reel link is valid."
    })


@app.route("/api/download", methods=["POST"])
def download_reel():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not valid_url(url):
        return jsonify({
            "success": False,
            "message": "Please enter a valid Instagram Reel URL."
        }), 400

    folder = tempfile.mkdtemp()

    try:
        options = {
            "outtmpl": os.path.join(folder, "%(id)s.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 25,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        files = glob.glob(os.path.join(folder, "*"))

        if not files:
            raise Exception("No video file was created.")

        response = send_file(
            files[0],
            as_attachment=True,
            download_name="instagram_reel.mp4"
        )

        response.call_on_close(
            lambda: shutil.rmtree(folder, ignore_errors=True)
        )

        return response

    except Exception:
        shutil.rmtree(folder, ignore_errors=True)

        return jsonify({
            "success": False,
            "message": (
                "Download failed. Instagram may require "
                "authentication or may block this request."
            )
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
