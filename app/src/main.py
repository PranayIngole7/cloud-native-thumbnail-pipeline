from uuid import uuid4
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError

from .storage.factory import create_object_storage
from .storage.object_keys import original_key, thumbnail_key

app = FastAPI(
    title="Cloud-Native Thumbnail Pipeline",
    version="0.1.0",
)

storage = create_object_storage()

MAX_THUMBNAIL_SIZE = (320, 320)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/thumbnails")
async def create_thumbnail(file: UploadFile = File(...)) -> StreamingResponse:
    image_data = await file.read()

    if len(image_data) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Uploaded file is too large",
        )

    try:
        image = Image.open(BytesIO(image_data))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image",
        )

    if image.format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format",
        )

    image_id = uuid4()
    extension = image.format.lower()

    original_object_key = original_key(image_id, extension)

    storage.put_object(
        original_object_key,
        BytesIO(image_data),
        f"image/{extension}",
    )

    stored_original = storage.get_object(original_object_key)

    image = Image.open(BytesIO(stored_original))
    image.load()

    image.thumbnail(MAX_THUMBNAIL_SIZE)

    output = BytesIO()

    output_format = image.format
    if output_format == "JPEG":
        image = image.convert("RGB")

    image.save(output, format=output_format)
    output.seek(0)

    storage.put_object(
        thumbnail_key(image_id, extension),
        BytesIO(output.getvalue()),
        f"image/{extension}",
    )

    media_type = f"image/{output_format.lower()}"

    return StreamingResponse(
        output,
        media_type=media_type,
    )