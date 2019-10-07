from unittest import TestCase

from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.repos.gcs import GoogleCloudStoragePageRepository
from tests.fakes.gcs import FakeGcsClient


class GoogleCloudStoragePageRepositoryTests(TestCase):

    def setUp(self):
        self.bucket_name = 'test-bucket'

        self.namespace = {}
        self.storage_client = FakeGcsClient(self.namespace)
        self.bucket = self.storage_client.create_bucket(self.bucket_name)

        self.repo = GoogleCloudStoragePageRepository(self.bucket_name)
        self.repo.storage_client = self.storage_client

    def test_get_not_found(self):
        with self.assertRaises(PageNotFound):
            self.repo.get('index.md')

    def test_get(self):
        blob = self.bucket.blob('index.md')
        blob.upload_from_string(b'hello world!')

        page_contents = self.repo.get('index.md')

        self.assertEqual('hello world!', page_contents)

    def test_save(self):
        self.repo.save('index.md', 'hello world!')

        blob = self.bucket.get_blob('index.md')
        self.assertEqual('hello world!', blob.download_as_string())
