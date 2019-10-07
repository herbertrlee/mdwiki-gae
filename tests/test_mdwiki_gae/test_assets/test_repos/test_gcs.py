from unittest import TestCase

from mdwiki_gae.assets.exceptions import AssetNotFound
from mdwiki_gae.assets.repos.gcs import GoogleCloudStorageAssetRepository
from tests.fakes.gcs import FakeGcsClient


class GoogleCloudStorageAssetRepositoryTests(TestCase):

    def setUp(self):
        self.bucket_name = 'test-bucket'

        self.namespace = {}
        self.storage_client = FakeGcsClient(self.namespace)
        self.bucket = self.storage_client.create_bucket(self.bucket_name)

        self.repo = GoogleCloudStorageAssetRepository(self.bucket_name)
        self.repo.storage_client = self.storage_client

    def test_get_not_found(self):
        with self.assertRaises(AssetNotFound):
            self.repo.get('favicon.png')

    def test_get(self):
        blob = self.bucket.blob('favicon.png')
        blob.upload_from_string(b'hello world!')

        asset_contents = self.repo.get('favicon.png')

        self.assertEqual(b'hello world!', asset_contents)
