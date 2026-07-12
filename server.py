from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from supabase import create_client
import firebase_admin
from firebase_admin import credentials, auth
import os
import mimetypes


app = Flask(__name__)
CORS(app)


# Firebase Admin

cred = credentials.Certificate("firebase-key.json")

firebase_admin.initialize_app(cred)



# Supabase

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)


BUCKET = "files"



def get_user():

    token = request.headers.get("Authorization")

    if not token:
        return None


    token = token.replace("Bearer ", "")


    try:

        decoded = auth.verify_id_token(token)

        return decoded["uid"]

    except Exception as e:

        print(e)

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


    path = f"{uid}/{file.filename}"



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







# Dateien laden

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


        return jsonify(
            {
                "error":str(e)
            }
        ),500







# Download

@app.route("/files/<filename>")
def download(filename):


    uid = get_user()


    if not uid:

        return "Nicht angemeldet",401



    url = supabase.storage.from_(BUCKET).get_public_url(

        f"{uid}/{filename}"

    )


    return redirect(url)








# Löschen

@app.route("/delete", methods=["POST"])
def delete():


    uid = get_user()


    if not uid:

        return "Nicht angemeldet",401



    data = request.json

    filename = data.get("filename")



    try:


        supabase.storage.from_(BUCKET).remove(

            [
                f"{uid}/{filename}"
            ]

        )


        return "Gelöscht"



    except Exception as e:


        return str(e),500







# Umbenennen

@app.route("/rename", methods=["POST"])
def rename():


    uid = get_user()


    if not uid:

        return "Nicht angemeldet",401



    data = request.json


    old = data.get("oldName")

    new = data.get("newName")



    try:


        file_data = supabase.storage.from_(BUCKET).download(

            f"{uid}/{old}"

        )



        supabase.storage.from_(BUCKET).upload(

            f"{uid}/{new}",

            file_data,

            {
                "content-type":
                mimetypes.guess_type(new)[0]
                or "application/octet-stream"
            }

        )


        supabase.storage.from_(BUCKET).remove(

            [
                f"{uid}/{old}"
            ]

        )



        return "Umbenannt"



    except Exception as e:


        return str(e),500








if __name__ == "__main__":


    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port

    )
