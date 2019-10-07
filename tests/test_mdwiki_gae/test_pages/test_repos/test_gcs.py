from unittest import TestCase

from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.repos.gcs import GoogleCloudStoragePageRepository
from tests.fakes.gcs import FakeGcsClient


class GoogleCloudStoragePageRepositoryTests(TestCase):

    def test_get_not_found(self):
        namespace = {}
        storage_client = FakeGcsClient(namespace)
        storage_client.create_bucket('test-bucket')

        repo = GoogleCloudStoragePageRepository('test-bucket')
        repo.storage_client = storage_client

        with self.assertRaises(PageNotFound):
            repo.get('index.md')

    def test_get(self):
        namespace = {}
        storage_client = FakeGcsClient(namespace)
        bucket = storage_client.create_bucket('test-bucket')

        blob = bucket.blob('index.md')
        blob.upload_from_string(b'hello world!')

        repo = GoogleCloudStoragePageRepository('test-bucket')
        repo.storage_client = storage_client

        page_contents = repo.get('index.md')
        self.assertEqual('hello world!', page_contents)
