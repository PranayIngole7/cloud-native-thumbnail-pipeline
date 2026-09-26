import time
from io import BytesIO
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from prometheus_client import Counter, Histogram, make_asgi_app

from .storage.exceptions import StorageError
from .storage.factory import create_object_storage
from .storage.object_keys import original_key, thumbnail_key


app = FastAPI(
    title="Cloud-Native Thumbnail Pipeline",
    version="0.1.0",
)


thumbnail_requests_total = Counter(
    "thumbnail_requests_total",
    "Total number of thumbnail pipeline HTTP requests",
)

thumbnail_errors_total = Counter(
    "thumbnail_errors_total",
    "Total number of failed thumbnail pipeline HTTP requests",
)

thumbnail_request_duration_seconds = Histogram(
    "thumbnail_request_duration_seconds",
    "Time spent processing thumbnail pipeline HTTP requests",
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    if request.url.path in {"/metrics", "/metrics/"}:
        return await call_next(request)

    start_time = time.perf_counter()

    response = await call_next(request)

    thumbnail_requests_total.inc()

    if response.status_code >= 400:
        thumbnail_errors_total.inc()

    thumbnail_request_duration_seconds.observe(
        time.perf_counter() - start_time
    )

    return response


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


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

    try:
        storage.put_object(
            original_object_key,
            BytesIO(image_data),
            f"image/{extension}",
        )

        stored_original = storage.get_object(original_object_key)
    except StorageError:
        raise HTTPException(
            status_code=503,
            detail="Object storage is temporarily unavailable",
        )

    image = Image.open(BytesIO(stored_original))
    image.load()

    image.thumbnail(MAX_THUMBNAIL_SIZE)

    output = BytesIO()

    output_format = image.format
    if output_format == "JPEG":
        image = image.convert("RGB")

    image.save(output, format=output_format)
    output.seek(0)

    try:
        storage.put_object(
            thumbnail_key(image_id, extension),
            BytesIO(output.getvalue()),
            f"image/{extension}",
        )
    except StorageError:
        raise HTTPException(
            status_code=503,
            detail="Object storage is temporarily unavailable",
        )

    media_type = f"image/{output_format.lower()}"

    return StreamingResponse(
        output,
        media_type=media_type,
    )