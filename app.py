from flask import Flask, request, jsonify
import re

app = Flask(__name__)

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

    pattern = r"^https?://(www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?(\?.*)?$"

    if not re.match(pattern, url):
        return jsonify({
            "success": False,
            "message": "Please enter a valid Instagram Reel URL."
        }), 400

    return jsonify({
        "success": True,
        "message": "Reel link checked successfully. Video downloading is not available yet."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
