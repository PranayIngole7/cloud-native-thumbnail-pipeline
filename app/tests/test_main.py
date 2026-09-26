from io import BytesIO
from typing import BinaryIO

from fastapi.testclient import TestClient
from PIL import Image

import src.main as main
from src.main import app
from src.storage.exceptions import StorageError
from test_storage import InMemoryObjectStorage


class TrackingObjectStorage(InMemoryObjectStorage):

    def __init__(self) -> None:
        super().__init__()
        self.get_calls: list[str] = []

    def get_object(self, object_key: str) -> bytes:
        self.get_calls.append(object_key)
        return super().get_object(object_key)

class FailingPutStorage(InMemoryObjectStorage):

    def put_object(
        self,
        object_key: str,
        data: BinaryIO,
        content_type: str,
    ) -> None:
        raise StorageError("storage unavailable")


class FailingGetStorage(InMemoryObjectStorage):

    def get_object(self, object_key: str) -> bytes:
        raise StorageError("storage unavailable")


class FailingThumbnailPutStorage(InMemoryObjectStorage):

    def put_object(
        self,
        object_key: str,
        data: BinaryIO,
        content_type: str,
    ) -> None:
        if object_key.startswith("thumbnails/"):
            raise StorageError("storage unavailable")

        super().put_object(object_key, data, content_type)

client = TestClient(app)

test_storage = TrackingObjectStorage()
main.storage = test_storage


def clear_storage() -> None:
    test_storage.objects.clear()
    test_storage.get_calls.clear()

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

def test_thumbnail_processing_reads_original_from_storage():
    clear_storage()
    image = create_test_image(size=(1000, 500))

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 200

    assert len(test_storage.get_calls) == 1

    retrieved_key = test_storage.get_calls[0]

    assert retrieved_key.startswith("originals/")
    assert retrieved_key.endswith(".png")
    assert retrieved_key in test_storage.objects

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

def test_storage_put_failure_returns_503():
    main.storage = FailingPutStorage()

    image = create_test_image()

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Object storage is temporarily unavailable"
    }

    main.storage = test_storage
    clear_storage()


def test_storage_get_failure_returns_503():
    storage = FailingGetStorage()

    image = create_test_image()

    main.storage = storage

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Object storage is temporarily unavailable"
    }

    main.storage = test_storage
    clear_storage()


def test_thumbnail_storage_put_failure_returns_503():
    storage = FailingThumbnailPutStorage()

    image = create_test_image()

    main.storage = storage

    response = client.post(
        "/thumbnails",
        files={"file": ("test.png", image, "image/png")},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Object storage is temporarily unavailable"
    }

    main.storage = test_storage
    clear_storage()

def test_metrics_endpoint_exposes_application_metrics():
    response = client.get("/metrics/")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    body = response.text

    assert "thumbnail_requests_total" in body
    assert "thumbnail_errors_total" in body
    assert "thumbnail_request_duration_seconds" in body


def test_metrics_request_counter_increments():
    before = client.get("/metrics/").text

    def metric_value(metrics_text: str, metric_name: str) -> float:
        for line in metrics_text.splitlines():
            if line.startswith(f"{metric_name} "):
                return float(line.split()[1])
        raise AssertionError(f"{metric_name} not found")

    before_value = metric_value(
        before,
        "thumbnail_requests_total",
    )

    response = client.get("/health")

    assert response.status_code == 200

    after = client.get("/metrics/").text

    after_value = metric_value(
        after,
        "thumbnail_requests_total",
    )

    assert after_value == before_value + 1


def test_metrics_error_counter_increments():
    before = client.get("/metrics/").text

    def metric_value(metrics_text: str, metric_name: str) -> float:
        for line in metrics_text.splitlines():
            if line.startswith(f"{metric_name} "):
                return float(line.split()[1])
        raise AssertionError(f"{metric_name} not found")

    before_value = metric_value(
        before,
        "thumbnail_errors_total",
    )

    response = client.post(
        "/thumbnails",
        files={
            "file": (
                "not-an-image.txt",
                b"not an image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    after = client.get("/metrics/").text

    after_value = metric_value(
        after,
        "thumbnail_errors_total",
    )

    assert after_value == before_value + 1


def test_metrics_duration_histogram_records_request():
    before = client.get("/metrics/").text

    def metric_value(metrics_text: str, metric_name: str) -> float:
        for line in metrics_text.splitlines():
            if line.startswith(f"{metric_name} "):
                return float(line.split()[1])
        raise AssertionError(f"{metric_name} not found")

    before_value = metric_value(
        before,
        "thumbnail_request_duration_seconds_count",
    )

    response = client.get("/health")

    assert response.status_code == 200

    after = client.get("/metrics/").text

    after_value = metric_value(
        after,
        "thumbnail_request_duration_seconds_count",
    )

    assert after_value == before_value + 1
