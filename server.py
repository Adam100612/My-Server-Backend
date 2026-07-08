from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from supabase import create_client
import os
import mimetypes


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



# Upload
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return "Keine Datei", 400


    file = request.files["file"]


    content_type = file.content_type or "application/octet-stream"


    try:

        supabase.storage.from_(BUCKET).upload(
            file.filename,
            file.read(),
            {
                "content-type": content_type
            }
        )


        return "Upload erfolgreich"


    except Exception as e:

        return str(e), 500





# Dateien laden
@app.route("/files")
def list_files():

    try:

        files = supabase.storage.from_(BUCKET).list()

        return jsonify(
            [f["name"] for f in files]
        )


    except Exception as e:

        return jsonify({"error":str(e)}),500





# Download
@app.route("/files/<filename>")
def download(filename):

    url = supabase.storage.from_(BUCKET).get_public_url(filename)

    return redirect(url)





# Umbenennen
@app.route("/rename", methods=["POST"])
def rename():

    data = request.json


    old_name = data.get("oldName")
    new_name = data.get("newName")


    if not old_name or not new_name:

        return "Name fehlt",400



    try:

        # Datei holen
        file_data = supabase.storage.from_(BUCKET).download(old_name)



        # neuen Dateityp erkennen
        content_type = mimetypes.guess_type(new_name)[0]


        if not content_type:

            content_type = "application/octet-stream"



        # neue Datei speichern
        supabase.storage.from_(BUCKET).upload(
            new_name,
            file_data,
            {
                "content-type": content_type
            }
        )



        # alte Datei löschen
        supabase.storage.from_(BUCKET).remove(
            [old_name]
        )



        return "Umbenannt"



    except Exception as e:

        return str(e),500






if __name__ == "__main__":

    port = int(os.environ.get("PORT",10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
