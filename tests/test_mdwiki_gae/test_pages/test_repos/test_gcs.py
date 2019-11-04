from unittest import TestCase

from mdwiki_gae.pages.exceptions import PageNotFound
from mdwiki_gae.pages.model import Page
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

        page = self.repo.get('index.md')

        expected_page = Page("index.md", "hello world!")
        self.assertEqual(expected_page, page)

    def test_get_with_title(self):
        blob = self.bucket.blob('index.md')
        blob.metadata = {"title": "Hello"}
        blob.upload_from_string(b'hello world!')

        page = self.repo.get("index.md")

        expected_page = Page("index.md", "hello world!", title="Hello")
        self.assertEqual(expected_page, page)

    def test_save(self):
        page = Page("index.md", "hello world!")
        self.repo.save(page)

        blob = self.bucket.get_blob('index.md')
        self.assertEqual('hello world!', blob.download_as_string())

    def test_save_with_title(self):
        page = Page("index.md", "hello world!", title="Hello")
        self.repo.save(page)

        blob = self.bucket.get_blob('index.md')
        self.assertEqual('hello world!', blob.download_as_string())
        self.assertEqual({"title": "Hello"}, blob.metadata)

    def test_delete(self):
        blob = self.bucket.blob('index.md')
        blob.upload_from_string(b'hello world!')

        self.repo.delete('index.md')

        blob = self.bucket.get_blob('index.md')
        self.assertIsNone(blob)
