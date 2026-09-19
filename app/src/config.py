import os


def get_minio_config() -> dict[str, str | bool]:
    return {
        "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
        "bucket_name": os.getenv("MINIO_BUCKET", "thumbnail-pipeline"),
        "secure": os.getenv("MINIO_SECURE", "false").lower() == "true",
    }
