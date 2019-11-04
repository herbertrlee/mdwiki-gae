from cached_property import cached_property
from google.cloud import storage

from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.model import Page


class GoogleCloudStoragePageRepository:

    TITLE = "title"
    UNTITLED = "Untitled"

    def __init__(self, bucket_name: str):
        self._bucket_name = bucket_name
        self._storage_client = None

    @property
    def storage_client(self) -> storage.Client:
        if self._storage_client is None:
            self._storage_client = storage.Client()
        return self._storage_client

    @storage_client.setter
    def storage_client(self, storage_client: storage.Client):
        self._storage_client = storage_client

    def get(self, page_name: str) -> Page:
        blob = self._bucket.get_blob(page_name)
        if blob is None:
            raise PageNotFound

        blob_bytes = blob.download_as_string()
        page_contents = blob_bytes.decode('utf-8')

        metadata = blob.metadata or {}
        title = metadata.get(self.TITLE, self.UNTITLED)

        return Page(page_name, page_contents, title=title)

    @cached_property
    def _bucket(self) -> storage.Bucket:
        return self.storage_client.get_bucket(self._bucket_name)

    def save(self, page: Page):
        blob = self._bucket.blob(page.name)
        blob.metadata = {self.TITLE: page.title}

        blob.upload_from_string(page.contents)

    def delete(self, page_name: str):
        blob = self._bucket.blob(page_name)

        blob.delete()
