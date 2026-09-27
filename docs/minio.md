# MinIO Object Storage

The Cloud-Native Thumbnail Pipeline uses MinIO as its local
S3-compatible object-storage layer.

MinIO provides a dedicated storage boundary for original images and
generated thumbnails instead of storing image data in the application
container filesystem.

## Architecture

```text
Client
  |
  v
FastAPI Thumbnail Service
  |
  v
Storage Abstraction
  |
  v
MinIO
  |
  +-- Original Images
  |
  +-- Generated Thumbnails
```

The application communicates with MinIO through the Python MinIO SDK.

## Local Implementation

MinIO was introduced into the local development environment using
Docker Compose.

The Compose setup provides:

* a MinIO service
* persistent storage through a Docker volume
* an application-accessible MinIO endpoint
* initialization of the `thumbnail-pipeline` bucket

Storage configuration is provided through environment variables rather
than being hard-coded into the application.

Important configuration values include:

```text
MINIO_ENDPOINT
MINIO_BUCKET
MINIO_SECURE
```

Credentials are supplied separately through environment configuration
and Kubernetes Secrets where applicable.

## Application Integration

The storage layer provides operations for:

* storing original images
* storing generated thumbnails
* retrieving stored objects

The application uses a storage abstraction so API-level logic does not
depend directly on MinIO-specific implementation details.

Storage failures are handled through the application's `StorageError`
path and can result in an HTTP `503 Service Unavailable` response when
the storage dependency is unavailable.

## Kubernetes Deployment

The same storage model is used in Kubernetes:

```text
Thumbnail Service
       |
       | MINIO_ENDPOINT=minio:9000
       v
     MinIO
       |
       v
PersistentVolumeClaim
```

The Kubernetes MinIO deployment uses a `PersistentVolumeClaim` named
`minio-data` for persistent object storage.

The application connects to MinIO through the Kubernetes Service
`minio` on port `9000`.

## Persistence

MinIO persistence was verified in both normal operation and failure
recovery testing.

The Kubernetes verification confirmed that:

* the `minio-data` PVC remained `Bound`
* a replacement MinIO Pod mounted the same PVC
* the existing MinIO data directory structure was visible after Pod
  replacement

This demonstrates that the storage volume is independent of the
lifecycle of an individual MinIO Pod.

The verification focused on PVC attachment and retained storage
structure rather than claiming independent recovery of every individual
object.

## Failure Handling

The application includes explicit storage failure handling.

During failure testing, MinIO Pod deletion was used to verify Kubernetes
replacement behavior. A missing `minio-secret` initially prevented the
replacement Pod from starting, producing `CreateContainerConfigError`.

Reapplying the required Secret restored the MinIO deployment.

This demonstrated that Kubernetes can recreate the Pod, while required
configuration dependencies must still be present for successful
startup.

## Verification

MinIO integration was verified through:

* original-image upload
* thumbnail generation
* thumbnail storage
* object retrieval
* storage failure handling
* MinIO service outage and recovery testing
* persistent-volume verification
* automated application tests

The application and storage integration were also exercised as part of
the later Kubernetes, observability, security, and failure-recovery
phases.

## Scope

MinIO provides the project's object-storage layer.

It is not the application's transactional database and is not intended
to replace relational transactional state.

For this local and free implementation, MinIO provides an
S3-compatible object-storage experience without requiring a cloud
storage account.
