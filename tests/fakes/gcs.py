from functools import total_ordering
from typing import Dict, Iterator, Union

from google.cloud.exceptions import NotFound, Conflict


class FakeGcsClient:

    def __init__(self, namespace: Dict):
        self._namespace = namespace

    def list_buckets(self) -> Iterator['FakeGcsBucket']:
        return iter(self._init_bucket(bucket_name) for bucket_name in sorted(self._namespace.keys()))

    def get_bucket(self, bucket_name: str) -> 'FakeGcsBucket':
        if bucket_name in self._namespace:
            return self._init_bucket(bucket_name)
        raise NotFound("Bucket {} not found.".format(bucket_name))

    def _init_bucket(self, bucket_name: str) -> 'FakeGcsBucket':
        return FakeGcsBucket(self, bucket_name, self._namespace)

    def create_bucket(self, bucket_name: str) -> 'FakeGcsBucket':
        if bucket_name in self._namespace:
            raise Conflict('Bucket {} already exists.'.format(bucket_name))
        self._namespace[bucket_name] = {}
        return self._init_bucket(bucket_name)

    def bucket(self, bucket_name: str) -> 'FakeGcsBucket':
        return self._init_bucket(bucket_name)

    def lookup_bucket(self, bucket_name: str) -> Union['FakeGcsBucket', None]:
        try:
            return self.get_bucket(bucket_name)
        except NotFound:
            return None


class FakeGcsBucket:

    def __init__(self, client: FakeGcsClient, bucket_name: str, namespace: Dict):
        self._client = client
        self._name = bucket_name
        self._namespace = namespace

    @property
    def client(self) -> FakeGcsClient:
        return self._client

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other: 'FakeGcsBucket'):
        return self.name == other.name and self.client == other.client

    def __repr__(self):
        return str({'name': self.name})

    def exists(self) -> bool:
        bucket = self._client.lookup_bucket(self.name)
        return bucket is not None

    def list_blobs(self, prefix: str = None) -> Iterator['FakeGcsBlob']:
        return [
            self.blob(blob_id)
            for blob_id in sorted(self._namespace[self.name].keys())
            if prefix is None or blob_id.startswith(prefix)
        ]

    def get_blob(self, blob_id: str) -> 'FakeGcsBlob':
        return self.blob(blob_id) if blob_id in self._namespace[self.name] else None

    def blob(self, blob_id: str) -> 'FakeGcsBlob':
        return FakeGcsBlob(self, blob_id, self._namespace)


@total_ordering
class FakeGcsBlob:

    def __init__(self, bucket: FakeGcsBucket, blob_id: str, namespace: Dict):
        self._bucket = bucket
        self._blob_id = blob_id
        self._namespace = namespace
        self._metadata = {}

    @property
    def bucket(self) -> FakeGcsBucket:
        return self._bucket

    @property
    def name(self) -> str:
        return self._blob_id

    @property
    def metadata(self) -> Dict[str, str]:
        return self._namespace[self._bucket.name][self._blob_id].get('metadata', {})

    @metadata.setter
    def metadata(self, metadata: Dict[str, str]):
        self._metadata = metadata

    def __eq__(self, other: 'FakeGcsBlob'):
        return self.bucket == other.bucket and self.name == other.name

    def __le__(self, other: 'FakeGcsBlob'):
        return self.name < other.name

    def __repr__(self):
        return str({"blob_id": self.name, "bucket": self.bucket})

    def upload_from_string(self, data: bytes):
        self._namespace[self._bucket.name][self._blob_id] = {"data": data, "metadata": self._metadata}

    def download_as_string(self) -> bytes:
        return self._namespace[self._bucket.name][self._blob_id]["data"]
