import base64
import json
import logging
import os

from elasticsearch import Elasticsearch
from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap
from google.cloud import storage
from werkzeug.exceptions import NotFound

from mdwiki_gae.assets.exceptions import AssetNotFound
from mdwiki_gae.assets.repos.gcs import GoogleCloudStorageAssetRepository
from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.model import Page
from mdwiki_gae.pages.repos.gcs import GoogleCloudStoragePageRepository

logger = logging.getLogger("mdwiki")
logger.setLevel(logging.INFO)

app = Flask(__name__, template_folder='templates')
Bootstrap(app)

ELASTICSEARCH_SITE = os.environ['ELASTICSEARCH_SITE']
TITLE = os.getenv("TITLE", "MDWiki")
THEME = os.getenv("THEME", "spacelab")
GCS_BUCKET = os.environ["GCS_BUCKET"]

client = storage.Client()

page_repo = GoogleCloudStoragePageRepository(GCS_BUCKET)
page_repo.storage_client = client

asset_repo = GoogleCloudStorageAssetRepository(GCS_BUCKET)
asset_repo.storage_client = client

elasticsearch_client = Elasticsearch(f'{ELASTICSEARCH_SITE}:443')


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

@app.route("/search.md")
def search_md():
    search_term = request.args.get("search_term", None)
    encoded_results = request.args.getlist("result")
    decoded_results = [base64.b64decode(encoded_result).decode('utf-8') for encoded_result in encoded_results]
    results = [json.loads(decoded_result) for decoded_result in decoded_results]
    return render_template("search.md", title=TITLE, search_term=search_term, results=results)

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

    encoded_id = base64.b64encode(page.name.encode('utf-8')).decode('utf-8')
    elasticsearch_client.index('pages', id=encoded_id, body={"text": page.contents, "title": page.title})

    return redirect(f"/index.html#!{page.name}")


@app.route("/search", methods=['POST'])
def search():
    search_term = request.form['search']
    search_body = {"query": {"match": {"text": search_term}}}
    search_response = elasticsearch_client.search('pages', body=search_body, _source=['title'])
    hits = search_response['hits']['hits']
    results = [{"title": hit['_source']['title'], "name": base64.b64decode(hit['_id']).decode('utf-8')} for hit in hits]
    json_results = [json.dumps(result) for result in results]
    encoded_results = [base64.b64encode(json_result.encode('utf-8')).decode('utf-8') for json_result in json_results]
    result_strings = [f'result={encoded_result}' for encoded_result in encoded_results]
    result_query_string = "&".join(result_strings)
    path = f"/index.html#!search.md?search_term={search_term}"

    if result_query_string:
        path += '&' + result_query_string

    return redirect(path)


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
