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
