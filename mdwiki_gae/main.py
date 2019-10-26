import os

from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap
from google.cloud import storage
from werkzeug.exceptions import NotFound

from mdwiki_gae.assets.exceptions import AssetNotFound
from mdwiki_gae.assets.repos.gcs import GoogleCloudStorageAssetRepository
from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.model import Page
from mdwiki_gae.pages.repos.gcs import GoogleCloudStoragePageRepository

app = Flask(__name__, template_folder='templates')
Bootstrap(app)

TITLE = os.getenv("TITLE", "MDWiki")
THEME = os.getenv("THEME", "spacelab")
GCS_BUCKET = os.environ["GCS_BUCKET"]

client = storage.Client()

page_repo = GoogleCloudStoragePageRepository(GCS_BUCKET)
page_repo.storage_client = client

asset_repo = GoogleCloudStorageAssetRepository(GCS_BUCKET)
asset_repo.storage_client = client


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

@app.route("/hotkeys.md")
def hotkeys_md():
    return render_template('hotkeys.md', title=TITLE)

@app.route("/new")
@app.route("/<path:file_name>:new")
def new_document(file_name=""):
    page = Page(name=file_name, contents="")
    return render_template("edit.html", page=page)

@app.route("/save", methods=['POST'])
def save_document():
    page = Page(
        name=request.form['file_name'],
        title=request.form['file_title'],
        contents=request.form['editor']
    )

    page_repo.save(page)

    return redirect(f"/index.html#!{page.name}")


@app.route("/<path:file_name>:edit")
def edit_document(file_name):
    try:
        page = page_repo.get(file_name)
    except PageNotFound:
        raise NotFound

    return render_template("edit.html", page=page)


@app.route("/<path:markdown_file>.md")
def serve_markdown_file(markdown_file):
    file_name = f"{markdown_file}.md"

    try:
        page = page_repo.get(file_name)
    except PageNotFound:
        return render_template("not_found.md", file_name=file_name)

    return render_template("editable_page.md", page=page)


@app.route("/<file_name>")
def serve_from_gcs(file_name):
    try:
        return asset_repo.get(file_name)
    except AssetNotFound:
        raise NotFound


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
