from flask import Flask, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # 👈 DAS FIXT CORS

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Backend läuft"

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "Keine Datei", 400

    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "Upload erfolgreich"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
