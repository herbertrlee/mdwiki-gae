from google.cloud import storage

from mdwiki_gae.pages.exceptions import PageNotFound


class GoogleCloudStoragePageRepository:

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

    def get(self, page_id: str):
        raise PageNotFound
