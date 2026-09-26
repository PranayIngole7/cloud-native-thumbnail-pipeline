# MinIO Object Storage

The Cloud-Native Thumbnail Pipeline uses MinIO as its local
S3-compatible object storage layer.

MinIO was introduced to move image data out of application-local
memory/filesystem handling and provide a storage boundary that can be
used by the application in both local and Kubernetes environments.

## Architecture

``` text
Client
  |
  v
FastAPI Thumbnail Service
  |
  v
Storage abstraction
  |
  v
MinIO
  |
  +-- original images
  |
  +-- generated thumbnails
```

The application communicates with MinIO through the Python MinIO SDK.

## Local Implementation

MinIO was added to the local development environment with Docker
Compose.

The Compose setup provides:

- a MinIO service
- persistent storage through a Docker volume
- application-accessible MinIO endpoint
- automatic initialization of the `thumbnail-pipeline` bucket

The application receives storage configuration through environment
variables rather than hard-coding storage connection details.

Important configuration values include:

``` text
MINIO_ENDPOINT
MINIO_BUCKET
MINIO_SECURE
```

## Application Integration

The storage layer provides operations for:

- storing original images
- storing generated thumbnails
- retrieving stored objects

The application uses a storage abstraction so the API layer does not
need to contain MinIO-specific implementation details.

Storage failures are translated into the application’s `StorageError`
handling path and exposed as an HTTP `503 Service Unavailable` response
when the storage dependency cannot be used.

## Persistence

Persistence was verified by storing objects in MinIO, restarting the
relevant services, and confirming that stored data remained available
through the persistent volume.

This demonstrates that object data is not dependent on the lifetime of
the application container.

## Kubernetes

The same storage model was carried into Kubernetes:

``` text
thumbnail-service
       |
       | MINIO_ENDPOINT=minio:9000
       v
     MinIO
       |
       v
PersistentVolumeClaim
```

The Kubernetes MinIO deployment uses a PVC for persistent object
storage.

## Verification

The MinIO integration was verified through:

- successful original-image upload
- thumbnail generation
- thumbnail storage
- object retrieval
- storage failure handling
- service outage/recovery testing
- persistence verification
- automated application tests

At the completed integration stage, the test suite contained 19 tests.

## Scope

MinIO provides the project’s object-storage layer. It is not the
database source of truth and is not used as a replacement for
PostgreSQL-style transactional state.

For this local/free implementation, MinIO provides an S3-compatible
object-storage experience without requiring a cloud storage account.
