from ..config import get_minio_config
from .minio_storage import MinioObjectStorage
from .object_storage import ObjectStorage


def create_object_storage() -> ObjectStorage:
    config = get_minio_config()

    return MinioObjectStorage(
        endpoint=str(config["endpoint"]),
        access_key=str(config["access_key"]),
        secret_key=str(config["secret_key"]),
        bucket_name=str(config["bucket_name"]),
        secure=bool(config["secure"]),
    )
