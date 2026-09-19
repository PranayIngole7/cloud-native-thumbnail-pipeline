from typing import BinaryIO

from src.storage.object_storage import ObjectStorage


class InMemoryObjectStorage(ObjectStorage):

    def __init__(self) -> None:
        self.objects: dict[str, tuple[bytes, str]] = {}

    def put_object(
        self,
        object_key: str,
        data: BinaryIO,
        content_type: str,
    ) -> None:
        self.objects[object_key] = (data.read(), content_type)

    def get_object(self, object_key: str) -> bytes:
        return self.objects[object_key][0]
