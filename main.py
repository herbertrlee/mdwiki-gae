import os

from flask import Flask, redirect, url_for, render_template
from google.cloud import storage
from werkzeug.exceptions import NotFound

app = Flask(__name__, template_folder='templates')

client = storage.Client()
bucket = client.bucket("herbert-dev.appspot.com")


TITLE = os.getenv("TITLE", "MDWiki")


@app.route("/")
def root():
    return redirect(url_for('index_html'))

@app.route("/index.html")
def index_html():
    return render_template('index.html', title=TITLE)

@app.route("/config.json")
def config_json():
    return render_template('config.json', title=TITLE)

@app.route("/navigation.md")
def navigation_md():
    return render_template('navigation.md', title=TITLE)


@app.route("/<path>")
def serve_from_gcs(path):
    blob = bucket.blob(path)
    if not blob.exists():
        raise NotFound

    return blob.download_as_string()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
