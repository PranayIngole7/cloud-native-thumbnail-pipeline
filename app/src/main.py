import logging
import time
import os
from io import BytesIO
from uuid import uuid4


from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from prometheus_client import Counter, Histogram, make_asgi_app

from .storage.exceptions import StorageError
from .storage.factory import create_object_storage
from .storage.object_keys import original_key, thumbnail_key

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor





logger = logging.getLogger(__name__)

resource = Resource.create(
    {
        "service.name": "thumbnail-service",
        "service.version": "0.1.0",
    }
)

tracer_provider = TracerProvider(resource=resource)

otlp_endpoint = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4317",
)

otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    insecure=True,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("thumbnail-service")

app = FastAPI(
    title="Cloud-Native Thumbnail Pipeline",
    version="0.1.0",
)

FastAPIInstrumentor.instrument_app(app)

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
    request_id = str(uuid4())

    logger.info(
        "thumbnail request received request_id=%s filename=%s content_type=%s",
        request_id,
        file.filename,
        file.content_type,
    )

    image_data = await file.read()

    logger.info(
        "upload read request_id=%s size_bytes=%d",
        request_id,
        len(image_data),
    )

    if len(image_data) > MAX_UPLOAD_SIZE:
        logger.warning(
            "upload rejected request_id=%s reason=file_too_large size_bytes=%d",
            request_id,
            len(image_data),
        )

        raise HTTPException(
            status_code=413,
            detail="Uploaded file is too large",
        )

    with tracer.start_as_current_span("image.validation") as span:
        span.set_attribute("image.size_bytes", len(image_data))

        try:
            image = Image.open(BytesIO(image_data))
            image.load()
        except (UnidentifiedImageError, OSError):
            span.set_attribute("validation.success", False)
            logger.warning(
                "upload rejected request_id=%s reason=invalid_image",
                request_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid image",
            )

        if image.format not in SUPPORTED_FORMATS:
            span.set_attribute("validation.success", False)
            span.set_attribute("image.format", image.format or "unknown")

            logger.warning(
                "upload rejected request_id=%s reason=unsupported_format format=%s",
                request_id,
                image.format,
            )

            raise HTTPException(
                status_code=400,
                detail="Unsupported image format",
            )

        span.set_attribute("validation.success", True)
        span.set_attribute("image.format", image.format)

    image_id = uuid4()
    extension = image.format.lower()

    logger.info(
        "image validated request_id=%s image_id=%s format=%s",
        request_id,
        image_id,
        image.format,
    )

    original_object_key = original_key(image_id, extension)

    try:
        with tracer.start_as_current_span("minio.put_original") as span:
            span.set_attribute("image.id", str(image_id))
            span.set_attribute("storage.object_key", original_object_key)
            span.set_attribute("image.size_bytes", len(image_data))

            storage.put_object(
                original_object_key,
                BytesIO(image_data),
                f"image/{extension}",
            )

            span.set_attribute("storage.success", True)

        logger.info(
            "original image stored request_id=%s image_id=%s",
            request_id,
            image_id,
        )

        with tracer.start_as_current_span("minio.get_original") as span:
            span.set_attribute("image.id", str(image_id))
            span.set_attribute("storage.object_key", original_object_key)

            stored_original = storage.get_object(original_object_key)

            span.set_attribute("storage.success", True)
            span.set_attribute("storage.bytes_read", len(stored_original))

        logger.info(
            "original image retrieved request_id=%s image_id=%s",
            request_id,
            image_id,
        )

    except StorageError:
        logger.exception(
            "object storage failure request_id=%s image_id=%s stage=original",
            request_id,
            image_id,
        )

        raise HTTPException(
            status_code=503,
            detail="Object storage is temporarily unavailable",
        )

    with tracer.start_as_current_span("thumbnail.generation") as span:
        span.set_attribute("image.id", str(image_id))
        span.set_attribute("thumbnail.max_width", MAX_THUMBNAIL_SIZE[0])
        span.set_attribute("thumbnail.max_height", MAX_THUMBNAIL_SIZE[1])

        image = Image.open(BytesIO(stored_original))
        image.load()

        original_width, original_height = image.size

        image.thumbnail(MAX_THUMBNAIL_SIZE)

        output = BytesIO()

        output_format = image.format
        if output_format == "JPEG":
            image = image.convert("RGB")

        image.save(output, format=output_format)
        output.seek(0)

        span.set_attribute("image.original_width", original_width)
        span.set_attribute("image.original_height", original_height)
        span.set_attribute("thumbnail.width", image.width)
        span.set_attribute("thumbnail.height", image.height)
        span.set_attribute("thumbnail.format", output_format)

        logger.info(
            "thumbnail generated request_id=%s image_id=%s format=%s",
            request_id,
            image_id,
            output_format,
        )

    try:
        with tracer.start_as_current_span("minio.put_thumbnail") as span:
            thumbnail_object_key = thumbnail_key(image_id, extension)
            thumbnail_data = output.getvalue()

            span.set_attribute("image.id", str(image_id))
            span.set_attribute("storage.object_key", thumbnail_object_key)
            span.set_attribute("thumbnail.size_bytes", len(thumbnail_data))

            storage.put_object(
                thumbnail_object_key,
                BytesIO(thumbnail_data),
                f"image/{extension}",
            )

            span.set_attribute("storage.success", True)

        logger.info(
            "thumbnail stored request_id=%s image_id=%s",
            request_id,
            image_id,
        )

    except StorageError:
        logger.exception(
            "object storage failure request_id=%s image_id=%s stage=thumbnail",
            request_id,
            image_id,
        )

        raise HTTPException(
            status_code=503,
            detail="Object storage is temporarily unavailable",
        )

    media_type = f"image/{output_format.lower()}"

    logger.info(
        "thumbnail request completed request_id=%s image_id=%s",
        request_id,
        image_id,
    )

    return StreamingResponse(
        output,
        media_type=media_type,
    )
