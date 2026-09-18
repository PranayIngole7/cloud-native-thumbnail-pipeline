# Current Project Status

**Date:** 18 September 2026  
**Current Phase:** Phase 3 — MinIO Object Storage  
**Next Step:** Phase 3.1 — MinIO Concepts & Design

---

## Phase 1 — Build the Application ✅ COMPLETE

The smallest useful image-processing application was built and verified locally.

### Completed

- Created a FastAPI application using Python.
- Added `POST /thumbnails` for image upload and thumbnail generation.
- Added `GET /health` for application health checks.
- Added `GET /ready` for readiness checks.
- Added image validation based on actual image content rather than filename extension.
- Added support for JPEG, PNG, and WEBP images.
- Added a 10 MB upload-size limit.
- Added invalid-image and unsupported-format error handling.
- Added Pillow-based thumbnail generation with aspect-ratio preservation.
- Limited generated thumbnails to a maximum size of `320 × 320`.
- Added automated tests covering successful processing and important validation/error cases.

### Verification

```text
pytest
9 passed
```

The application was also manually verified locally by uploading an image and confirming the generated thumbnail dimensions.

### Design Principle

The application intentionally remains small. Infrastructure and operational engineering will provide the primary complexity of the capstone.

---

## Phase 2 — Containerization ✅ COMPLETE

The application was packaged as a production-oriented Docker container and progressively hardened.

### Completed

- Created a Dockerfile for the FastAPI application.
- Built and ran the application successfully inside Docker.
- Pinned direct Python dependencies for reproducible application environments.
- Added `.dockerignore` to exclude virtual environments, caches, and Python bytecode from the Docker build context.
- Configured the container to run as a dedicated non-root `appuser`.
- Added a Docker `HEALTHCHECK` that verifies the application's `/health` endpoint.
- Verified that Docker reports the container as `healthy`.
- Verified `/health` and `/ready` from the running container.
- Verified thumbnail processing inside the container.
- Cleaned up test containers after runtime verification.

### Verification

Docker image:

```text
thumbnail-service:0.1.4
```

Runtime verification:

```text
Container status       healthy
/health                passed
/ready                 passed
Thumbnail processing   passed
```

Application regression:

```text
9 passed
```

`git diff --check` completed successfully.

### Important Docker Checkpoints

```text
4253362  feat: containerize thumbnail service
73ab08c  chore: pin application dependencies
824a9ee  chore: add Docker build exclusions
35ec127  security: run container as non-root user
1d59f43  ops: add container healthcheck
```

The latest commit represents the completion of Phase 2.

---

## Phase 3 — MinIO Object Storage ⏳ NEXT

### Objective

Introduce persistent S3-compatible object storage while keeping the application itself deliberately simple.

### Planned Work

- Understand object-storage concepts and S3-compatible APIs.
- Run MinIO locally.
- Create and configure the required bucket.
- Externalize storage configuration appropriately.
- Store uploaded original images in MinIO.
- Generate thumbnails from stored images.
- Store generated thumbnails in MinIO.
- Add storage-related error handling.
- Test missing objects and storage failures.
- Document MinIO configuration and local setup.

### Target Flow

```text
Client
   |
   v
FastAPI
   |
   | store original
   v
MinIO
   |
   | process image
   v
Thumbnail
   |
   | store result
   v
MinIO
```

### Exit Criteria

The complete flow works reliably:

```text
Original Image
      ↓
    MinIO
      ↓
Thumbnail Generation
      ↓
Thumbnail
      ↓
    MinIO
```

**Current next step:** Phase 3.1 — MinIO Concepts & Design.

No MinIO implementation work has been started yet.