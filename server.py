from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from supabase import create_client
import firebase_admin
from firebase_admin import credentials, auth
import os
import mimetypes


app = Flask(__name__)
CORS(app)


cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)


supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)


BUCKET = "files"



def get_user():

    header = request.headers.get("Authorization")

    if not header:
        return None


    token = header.replace("Bearer ", "")


    try:

        decoded = auth.verify_id_token(token)

        return decoded["uid"]

    except Exception:

        return None






@app.route("/")
def home():

    return "Backend läuft"






# Upload

@app.route("/upload", methods=["POST"])
def upload():


    uid = get_user()


    if not uid:
        return "Nicht angemeldet",401



    if "file" not in request.files:
        return "Keine Datei",400



    file = request.files["file"]


    path = uid + "/" + file.filename


    try:

        supabase.storage.from_(BUCKET).upload(

            path,

            file.read(),

            {
                "content-type":
                file.content_type or "application/octet-stream"
            }

        )


        return "Upload erfolgreich"



    except Exception as e:

        return str(e),500







# Dateien anzeigen

@app.route("/files")
def list_files():


    uid = get_user()


    if not uid:
        return jsonify([]),401



    try:


        files = supabase.storage.from_(BUCKET).list(uid)



        return jsonify(

            [

                f["name"]

                for f in files

            ]

        )



    except Exception as e:

        return jsonify({"error":str(e)}),500







# Download

@app.route("/files/<filename>")
def download(filename):


    uid = get_user()


    if not uid:
        return "Nicht angemeldet",401



    path = uid + "/" + filename



    url = supabase.storage.from_(BUCKET).get_public_url(path)



    return redirect(url)








# Umbenennen

@app.route("/rename", methods=["POST"])
def rename():


    uid = get_user()


    if not uid:
        return "Nicht angemeldet",401



    data = request.json


    old_name = data.get("oldName")

    new_name = data.get("newName")



    old_path = uid + "/" + old_name

    new_path = uid + "/" + new_name



    try:


        content = supabase.storage.from_(BUCKET).download(old_path)



        supabase.storage.from_(BUCKET).upload(

            new_path,

            content,

            {
                "content-type":
                mimetypes.guess_type(new_name)[0]
                or "application/octet-stream"
            }

        )



        supabase.storage.from_(BUCKET).remove(

            [old_path]

        )


        return "Umbenannt"



    except Exception as e:

        return str(e),500







# Löschen

@app.route("/delete", methods=["POST"])
def delete():


    uid = get_user()


    if not uid:
        return "Nicht angemeldet",401



    filename = request.json.get("filename")



    if not filename:
        return "Dateiname fehlt",400



    path = uid + "/" + filename



    try:


        supabase.storage.from_(BUCKET).remove(

            [path]

        )


        return "Gelöscht"



    except Exception as e:

        return str(e),500






if __name__ == "__main__":


    port = int(os.environ.get("PORT",10000))


    app.run(

        host="0.0.0.0",

        port=port

    )
