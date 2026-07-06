from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Backend läuft"

# 📤 Upload
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "Keine Datei", 400

    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "Upload erfolgreich"

# 📁 Datei Liste
@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

# 📥 Download
@app.route("/files/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
