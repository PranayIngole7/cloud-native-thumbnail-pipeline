from uuid import UUID


def original_key(image_id: UUID, extension: str) -> str:
    return f"originals/{image_id}.{extension}"


def thumbnail_key(image_id: UUID, extension: str) -> str:
    return f"thumbnails/{image_id}.{extension}"
