from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os

app = Flask(__name__)
CORS(app)

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

BUCKET = "files"

@app.route("/")
def home():
    return "Backend läuft"

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "Keine Datei", 400

    file = request.files["file"]

    supabase.storage.from_(BUCKET).upload(
        file.filename,
        file.read()
    )

    return "Upload erfolgreich"


@app.route("/files")
def list_files():
    files = supabase.storage.from_(BUCKET).list()
    return jsonify([f["name"] for f in files])


@app.route("/files/<filename>")
def download(filename):
    url = supabase.storage.from_(BUCKET).get_public_url(filename)
    return url


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
