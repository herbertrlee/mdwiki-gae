from unittest import TestCase

from pages.exceptions import PageNotFound
from pages.repos.gcs import GoogleCloudStoragePageRepository
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
