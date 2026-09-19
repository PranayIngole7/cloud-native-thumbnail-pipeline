from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

import src.main as main
from src.main import app
from test_storage import InMemoryObjectStorage


client = TestClient(app)

test_storage = InMemoryObjectStorage()
main.storage = test_storage


def clear_storage() -> None:
    test_storage.objects.clear()

def create_test_image(
    image_format: str = "PNG",
    size: tuple[int, int] = (500, 500),
) -> BytesIO:
    image = Image.new("RGB", size, "red")
    output = BytesIO()
    image.save(output, format=image_format)
    output.seek(0)
    return output


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_create_thumbnail():
    clear_storage()
    image = create_test_image(size=(1000, 500))

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    thumbnail = Image.open(BytesIO(response.content))

    assert thumbnail.size == (320, 160)
    assert thumbnail.format == "PNG"

def test_create_thumbnail_stores_original_and_thumbnail():
    clear_storage()
    image = create_test_image(size=(1000, 500))
    original_data = image.getvalue()

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 200

    assert len(test_storage.objects) == 2

    keys = set(test_storage.objects.keys())

    original_keys = [
        key for key in keys if key.startswith("originals/")
    ]
    thumbnail_keys = [
        key for key in keys if key.startswith("thumbnails/")
    ]

    assert len(original_keys) == 1
    assert len(thumbnail_keys) == 1

    original_key = original_keys[0]
    thumbnail_key = thumbnail_keys[0]

    original_id = original_key.removeprefix("originals/").removesuffix(".png")
    thumbnail_id = thumbnail_key.removeprefix("thumbnails/").removesuffix(".png")

    assert original_id == thumbnail_id

    stored_original, original_content_type = test_storage.objects[original_key]
    stored_thumbnail, thumbnail_content_type = test_storage.objects[thumbnail_key]

    assert stored_original == original_data
    assert stored_thumbnail == response.content

    assert original_content_type == "image/png"
    assert thumbnail_content_type == "image/png"

def test_failed_upload_does_not_store_objects():
    clear_storage()

    response = client.post(
        "/thumbnails",
        files={
            "file": (
                "not-an-image.txt",
                b"this is not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Uploaded file is not a valid image"
    }

    assert test_storage.objects == {}

def test_unsupported_format_does_not_store_objects():
    clear_storage()
    image = create_test_image(image_format="BMP")

    response = client.post(
        "/thumbnails",
        files={"file": ("test.bmp", image, "image/bmp")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported image format"
    }

    assert test_storage.objects == {}

def test_create_jpeg_thumbnail():
    clear_storage()
    image = create_test_image(
        image_format="JPEG",
        size=(1920, 1080),
    )

    response = client.post(
        "/thumbnails",
        files={"file": ("photo.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    thumbnail = Image.open(BytesIO(response.content))

    assert thumbnail.size == (320, 180)
    assert thumbnail.format == "JPEG"

def test_create_jpeg_thumbnail_stores_jpeg_objects():
    clear_storage()
    image = create_test_image(
        image_format="JPEG",
        size=(1920, 1080),
    )

    response = client.post(
        "/thumbnails",
        files={"file": ("photo.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 200

    keys = set(test_storage.objects.keys())

    assert len(keys) == 2
    assert len([key for key in keys if key.startswith("originals/")]) == 1
    assert len([key for key in keys if key.startswith("thumbnails/")]) == 1

    assert all(key.endswith(".jpeg") for key in keys)

    for key in keys:
        _, content_type = test_storage.objects[key]
        assert content_type == "image/jpeg"

def test_create_webp_thumbnail():
    clear_storage()
    image = create_test_image(
        image_format="WEBP",
        size=(1000, 1500),
    )

    response = client.post(
        "/thumbnails",
        files={"file": ("photo.webp", image, "image/webp")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/webp"

    thumbnail = Image.open(BytesIO(response.content))

    assert thumbnail.size == (213, 320)
    assert thumbnail.format == "WEBP"

def test_create_webp_thumbnail_stores_webp_objects():
    clear_storage()
    image = create_test_image(
        image_format="WEBP",
        size=(1000, 1500),
    )

    response = client.post(
        "/thumbnails",
        files={"file": ("photo.webp", image, "image/webp")},
    )

    assert response.status_code == 200

    keys = set(test_storage.objects.keys())

    assert len(keys) == 2
    assert len([key for key in keys if key.startswith("originals/")]) == 1
    assert len([key for key in keys if key.startswith("thumbnails/")]) == 1

    assert all(key.endswith(".webp") for key in keys)

    for key in keys:
        _, content_type = test_storage.objects[key]
        assert content_type == "image/webp"

def test_image_content_is_validated_independently_of_filename():
    clear_storage()
    image = create_test_image(
        image_format="PNG",
        size=(500, 500),
    )

    response = client.post(
        "/thumbnails",
        files={"file": ("photo.jpg", image, "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    thumbnail = Image.open(BytesIO(response.content))

    assert thumbnail.format == "PNG"
    assert thumbnail.size == (320, 320)


def test_reject_invalid_image():
    clear_storage()
    response = client.post(
        "/thumbnails",
        files={
            "file": (
                "not-an-image.txt",
                b"this is not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Uploaded file is not a valid image"
    }


def test_reject_unsupported_image_format():
    clear_storage()
    image = create_test_image(image_format="BMP")

    response = client.post(
        "/thumbnails",
        files={"file": ("test.bmp", image, "image/bmp")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported image format"
    }

def test_oversized_upload_does_not_store_objects():
    clear_storage()

    oversized_data = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/thumbnails",
        files={
            "file": (
                "large.bin",
                oversized_data,
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded file is too large"
    }

    assert test_storage.objects == {}

def test_reject_oversized_upload():
    clear_storage()
    oversized_data = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/thumbnails",
        files={
            "file": (
                "large.bin",
                oversized_data,
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Uploaded file is too large"
    }
