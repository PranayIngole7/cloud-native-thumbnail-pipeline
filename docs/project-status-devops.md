# Current Project Status

**Date:** 24 September 2026
**Current Phase:** Phase 4 — Kubernetes Deployment  ✅ COMPLETE
**Next Step:** Phase 5 — Helm

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

## Phase 3 — MinIO Object Storage ✅ COMPLETE

### Objective

Introduce persistent S3-compatible object storage while keeping the application itself deliberately simple.

### Completed

- Completed MinIO concepts and storage architecture design.
- Added MinIO to Docker Compose for local object storage.
- Added persistent MinIO storage using a Docker volume.
- Added automatic creation of the `thumbnail-pipeline` bucket.
- Externalized MinIO configuration through environment variables.
- Added an object-storage abstraction separate from the MinIO implementation.
- Stored uploaded original images in MinIO.
- Retrieved original images from MinIO before thumbnail processing.
- Generated thumbnails using Pillow.
- Stored generated thumbnails in MinIO.
- Added storage-specific failure handling using `StorageError`.
- Mapped object-storage failures to HTTP `503 Service Unavailable`.
- Added automated tests for storage PUT and GET failures.
- Verified normal processing, storage failure, and recovery using Docker and MinIO.
- Verified persistent original and thumbnail objects in MinIO.

### Verification

Application regression:

```text
19 passed
```

### Docker Verification:
```text
Application container     healthy
MinIO                     running
Normal thumbnail flow     passed
MinIO failure handling    HTTP 503
MinIO recovery             passed
Thumbnail validation       320 × 320 PNG
Object persistence         verified
```

### Important MinIO Checkpoints:
```text
dd0557f  feat: add local MinIO infrastructure
9ff3912  feat: integrate MinIO object storage
4ecf960  feat: integrate thumbnail processing with MinIO
96dc8be  feat: harden object storage failure handling
```
The latest commit represents the completion of Phase 2.
---

## Phase 4 — Kubernetes Deployment ✅ COMPLETE

### Objective

Deploy the thumbnail service and its MinIO dependency to Kubernetes while introducing core Kubernetes concepts such as Deployments, Services, ConfigMaps, Secrets, health probes, resource management, persistent storage, and internal service discovery.

### Completed

- Set up a local Kubernetes environment using Minikube with Docker Engine.
- Created the `thumbnail-pipeline` Kubernetes namespace.
- Created a Kubernetes Deployment for the thumbnail service.
- Exposed the thumbnail service using a Kubernetes `ClusterIP` Service.
- Added a Kubernetes ConfigMap for non-sensitive application configuration.
- Added a Kubernetes Secret for MinIO credentials.
- Configured the application Deployment to consume ConfigMap and Secret values using `envFrom`.
- Added HTTP liveness and readiness probes using `/health` and `/ready`.
- Added CPU and memory resource requests.
- Added CPU and memory resource limits.
- Verified Kubernetes QoS classification as `Burstable`.
- Deployed MinIO as a Kubernetes Deployment.
- Exposed MinIO internally using a Kubernetes `ClusterIP` Service.
- Exposed MinIO API port `9000` and console port `9001`.
- Added a `PersistentVolumeClaim` for MinIO data.
- Configured MinIO to persist data under `/data` using the PVC.
- Added a Kubernetes Job to initialize the `thumbnail-pipeline` bucket.
- Configured the thumbnail service to connect to MinIO through Kubernetes Service DNS using `minio:9000`.
- Verified application-to-MinIO network connectivity from the application Pod.
- Verified MinIO authentication from the application.
- Built and deployed `thumbnail-service:0.1.5` containing the MinIO integration.
- Diagnosed and fixed a stale application image that did not contain the MinIO Python SDK.
- Verified end-to-end thumbnail processing through the Kubernetes deployment.
- Verified that uploaded originals are persisted in MinIO.
- Verified that generated thumbnails are persisted in MinIO.
- Verified successful Kubernetes health and readiness probe execution.
- Protected the local MinIO credential manifest from Git tracking using `.gitignore`.

### Verification

Kubernetes application:

```text
Deployment rollout       passed
Application Pod          1/1 Running
Pod restarts             0
Health probe             passed
Readiness probe          passed
ConfigMap configuration  passed
Secret configuration     passed
```

MinIO:

```text
MinIO Pod                1/1 Running
MinIO Service            ClusterIP
MinIO API                :9000
MinIO Console            :9001
PVC                      2Gi / Bound
Bucket initialization    passed
Application connectivity passed
Authentication           passed
```

End-to-end verification:

```text
POST /thumbnails         HTTP 200
Original persistence     verified
Thumbnail persistence   verified
Thumbnail output        320 × 240 PNG
```

### Important Kubernetes Checkpoints

```text
19333c6  feat: add Kubernetes application deployment
1fee69c  feat: add Kubernetes application configmap
bbab11a  feat: expose thumbnail service on kubernetes
331d05d  feat: add kubernetes health probes
ad5ff77  feat: add kubernetes resource requests
bfed24d  ops: add Kubernetes resource limits
c860a3a  feat: deploy minio on kubernetes
```

### Important Debugging Checkpoint

During end-to-end verification, the Kubernetes application returned HTTP `200`, but the MinIO bucket initially contained no objects.

Investigation showed that the running Kubernetes Pod used an older application image that did not contain the MinIO Python SDK. A new image, `thumbnail-service:0.1.5`, was built, verified, loaded into Minikube, and deployed.

The final verification confirmed:

```text
Application → MinIO        passed
Original upload            passed
Original persistence       passed
Thumbnail generation       passed
Thumbnail persistence      passed
```
---

