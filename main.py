from flask import Flask, redirect
from google.cloud import storage
from werkzeug.exceptions import NotFound

app = Flask(__name__)

client = storage.Client()
bucket = client.bucket("herbert-dev.appspot.com")


@app.route("/")
def index():
    return redirect("/index.html")


@app.route("/<path>")
def serve_from_gcs(path):
    blob = bucket.blob(path)
    if not blob.exists():
        raise NotFound

    return blob.download_as_string()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
