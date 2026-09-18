from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from src.main import app


client = TestClient(app)


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


def test_create_jpeg_thumbnail():
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


def test_create_webp_thumbnail():
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


def test_image_content_is_validated_independently_of_filename():
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
    image = create_test_image(image_format="BMP")

    response = client.post(
        "/thumbnails",
        files={"file": ("test.bmp", image, "image/bmp")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported image format"
    }


def test_reject_oversized_upload():
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
