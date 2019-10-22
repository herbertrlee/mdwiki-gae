import os

from elasticsearch import Elasticsearch
from google.cloud import storage

API_KEY = os.environ['API_KEY']
ELASTICSEARCH_SITE = os.environ['ELASTICSEARCH_SITE']
GCS_BUCKET = os.environ['GCS_BUCKET']

elasticsearch_client = Elasticsearch(f'https://site:{API_KEY}@{ELASTICSEARCH_SITE}:443')

elasticsearch_client.indices.create(index='pages', ignore=400)

storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)

for blob in bucket.list_blobs():
    blob_id = blob.name

    if blob_id.endswith(".md"):
        blob_contents = blob.download_as_string().decode('utf-8')

        document = {"text": blob_contents, "name": blob_id}
        elasticsearch_client.index(index='pages', body=document)
