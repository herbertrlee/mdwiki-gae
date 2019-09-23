import os

from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap
from google.cloud import storage
from werkzeug.exceptions import NotFound

app = Flask(__name__, template_folder='templates')
Bootstrap(app)

TITLE = os.getenv("TITLE", "MDWiki")
THEME = os.getenv("THEME", "spacelab")
GCS_BUCKET = os.environ["GCS_BUCKET"]

client = storage.Client()
bucket = client.bucket(GCS_BUCKET)


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
    return render_template('navigation.md', title=TITLE, theme=THEME)

@app.route("/documents", methods=['GET', 'POST'])
def new_document():
    if request.method == "GET":
        return render_template("documents/new.html")

    file_name = request.form['file_name']
    file_contents = request.form['editor']

    blob = bucket.blob(file_name)
    blob.upload_from_string(file_contents)

    return redirect(f"/index.html#!{file_name}")


@app.route("/documents/<path:file_name>")
def edit_document(file_name):
    file_name = f"{file_name}.md"
    blob = bucket.blob(file_name)
    if not blob.exists():
        raise NotFound

    file_contents = blob.download_as_string()
    return render_template("documents/edit.html", file_name=file_name, file_contents=file_contents.decode('utf-8'))


@app.route("/<path:markdown_file>.md")
def serve_markdown_file(markdown_file):
    file_name = f"{markdown_file}.md"
    blob = bucket.blob(file_name)
    if not blob.exists():
        raise NotFound

    file_contents = blob.download_as_string()
    return render_template("editable_page.md", markdown_file=markdown_file, file_contents=file_contents.decode('utf-8'))


@app.route("/<file_name>")
def serve_from_gcs(file_name):
    blob = bucket.blob(file_name)
    if not blob.exists():
        raise NotFound

    return blob.download_as_string()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
