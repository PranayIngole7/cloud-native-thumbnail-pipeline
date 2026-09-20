from typing import BinaryIO

from minio import Minio

from .exceptions import StorageError
from .object_storage import ObjectStorage


class MinioObjectStorage(ObjectStorage):

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ) -> None:
        self.bucket_name = bucket_name

        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def put_object(
        self,
        object_key: str,
        data: BinaryIO,
        content_type: str,
    ) -> None:
        data.seek(0)

        try:
            self.client.put_object(
                self.bucket_name,
                object_key,
                data,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=content_type,
            )
        except Exception as exc:
            raise StorageError(
                "Object storage put operation failed"
            ) from exc

    def get_object(self, object_key: str) -> bytes:
        try:
            response = self.client.get_object(
                self.bucket_name,
                object_key,
            )

            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        except Exception as exc:
            raise StorageError(
                "Object storage get operation failed"
            ) from exc
