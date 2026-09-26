# Containerization

The Cloud-Native Thumbnail Pipeline packages the FastAPI thumbnail
service as a Docker container so the same application artifact can be
run consistently across local development, Kubernetes, CI, and later
delivery stages.

## Implementation

The application image is built from `app/Dockerfile` using:

- `python:3.10-slim` as the base image
- `app/requirements.txt` for pinned Python dependencies
- `/app` as the working directory
- the application source under `src/`
- Uvicorn serving the FastAPI application on port `8000`
- a dedicated non-root `appuser`
- a Docker `HEALTHCHECK` against `/health`

The repository also uses `.dockerignore` to keep unnecessary local files
out of the Docker build context.

## Image and Runtime

The image is built as:

``` bash
docker build -t thumbnail-service:<tag> ./app
```

The container listens on:

``` text
0.0.0.0:8000
```

The Docker healthcheck verifies:

``` text
http://localhost:8000/health
```

The image was validated by building and running the container and
checking the application’s health and thumbnail-processing behavior. The
container also runs as the non-root `appuser`.

## Why Containerize?

Containerization provides:

- a repeatable application artifact
- consistent runtime dependencies
- isolation from the host environment
- a common artifact for CI and Kubernetes
- a clear boundary between application and infrastructure

The Docker image is built before Kubernetes deployment and is also built
and runtime-validated by the GitHub Actions CI workflow.

## Security and Reliability

The containerization implementation includes:

- pinned Python dependencies
- a slim Python base image
- non-root application execution
- Docker healthcheck
- `.dockerignore`
- explicit application port
- deterministic application startup through Uvicorn

Containerization does not by itself provide image vulnerability
scanning, signing, or registry publishing; those are separate concerns
in this project.

## Verification

Containerization was verified through:

``` bash
docker build -t thumbnail-service:<tag> ./app
docker run ...
docker ps
docker logs <container>
docker inspect <container>
```

The final image was also integrated into the Kubernetes deployment used
in later phases.
