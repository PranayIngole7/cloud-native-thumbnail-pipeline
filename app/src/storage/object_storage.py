from abc import ABC, abstractmethod
from typing import BinaryIO


class ObjectStorage(ABC):

    @abstractmethod
    def put_object(
        self,
        object_key: str,
        data: BinaryIO,
        content_type: str,
    ) -> None:
        pass

    @abstractmethod
    def get_object(self, object_key: str) -> bytes:
        pass
