# Containerization

The Cloud-Native Thumbnail Pipeline packages the FastAPI thumbnail
service as a Docker image so the application can run consistently across
local development, CI, and Kubernetes.

## Implementation

The application image is built from `app/Dockerfile` using:

* `python:3.10-slim` as the base image
* Python dependencies from `app/requirements.txt`
* `/app` as the working directory
* application source under `src/`
* Uvicorn serving the FastAPI application on port `8000`
* a dedicated non-root `appuser`
* a Docker `HEALTHCHECK` against `/health`

The repository also uses `.dockerignore` to exclude unnecessary local
files from the Docker build context.

## Image and Runtime

The image can be built with:

```bash
docker build -t thumbnail-service:<tag> ./app
```

The application listens on:

```text
0.0.0.0:8000
```

The Docker healthcheck verifies:

```text
http://localhost:8000/health
```

The container starts the FastAPI application through Uvicorn and runs
the application process as the non-root `appuser`.

## Why Containerize?

Containerization provides:

* a repeatable application artifact
* consistent runtime dependencies
* separation between the application and host environment
* a common artifact for CI and Kubernetes
* a clear boundary between application packaging and infrastructure

The same container image model is used during local verification,
GitHub Actions CI, and later Kubernetes deployment.

## CI Integration

The GitHub Actions workflow builds the Docker image after the Python
tests pass.

The CI workflow also starts the built container and verifies its runtime
health before cleaning up the container.

The current CI workflow **does not publish the image to an external
container registry**.

## Security and Reliability

The containerization implementation includes:

* a slim Python base image
* dependency version constraints from `requirements.txt`
* non-root application execution
* Docker healthcheck
* `.dockerignore`
* explicit application port
* deterministic startup through Uvicorn

Additional Kubernetes-level security controls are documented separately
in [`docs/security.md`](security.md).

Containerization itself does not provide image vulnerability scanning,
image signing, or registry publishing. These are separate concerns.

Trivy was used later in the project for container image vulnerability
scanning.

## Verification

Containerization was verified by building and running the image locally:

```bash
docker build -t thumbnail-service:<tag> ./app
docker run ...
docker ps
docker logs <container>
docker inspect <container>
```

The running container was verified through its health endpoint and
application behavior.

The resulting image was subsequently used as part of the Kubernetes
deployment and Helm-based deployment workflow.
