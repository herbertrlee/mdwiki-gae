import base64
import os

import elasticsearch.helpers
from elasticsearch import Elasticsearch
from google.cloud import storage

API_KEY = os.environ['API_KEY']
ELASTICSEARCH_SITE = os.environ['ELASTICSEARCH_SITE']
GCS_BUCKET = os.environ['GCS_BUCKET']

elasticsearch_client = Elasticsearch(f'https://site:{API_KEY}@{ELASTICSEARCH_SITE}:443')

elasticsearch_client.indices.create(index='pages', ignore=400)

storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)

def create_action(blob: storage.Blob):
    blob_id = blob.name
    encoded_id = base64.b64encode(blob_id.encode('utf-8')).decode('utf-8')
    blob_contents = blob.download_as_string().decode('utf-8')
    metadata = blob.metadata or {}
    title = metadata.get("title", "Untitled")
    return {"text": blob_contents, "title": title, "_id": encoded_id}

def should_process(blob: storage.Blob):
    return blob.name.endswith(".md")

actions = iter(create_action(blob) for blob in bucket.list_blobs() if should_process(blob))

elasticsearch.helpers.bulk(elasticsearch_client, actions, index="pages")
