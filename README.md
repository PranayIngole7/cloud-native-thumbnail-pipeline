# Cloud-Native Thumbnail Pipeline

A containerized image-processing service demonstrating practical cloud-native and DevOps engineering with **FastAPI, Docker, Kubernetes, Helm, Knative, GitHub Actions, Argo CD, observability, security, and failure engineering**.

The application accepts an image, stores the original in MinIO, generates a Pillow-based thumbnail, and stores the resulting thumbnail back in MinIO.

> **Core principle:** Keep the application small and use the surrounding infrastructure to demonstrate real engineering practices.

## Architecture

```text
                         GitHub
                           │
                           ▼
                    GitHub Actions
                  Tests + Docker Build
                           │
                           ▼
                       Argo CD
                           │
                           ▼
                Kubernetes / Minikube
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     Thumbnail Service                MinIO
      FastAPI + Pillow             Object Storage
              │                         │
              └──────────┬──────────────┘
                         │
                         ▼
                  PersistentVolume

Observability:
FastAPI → OpenTelemetry → Jaeger
FastAPI → Prometheus → Grafana
FastAPI → Kubernetes Logs

Additional serving capability:
Knative Serving → Thumbnail Service
```

## Key Features

* FastAPI thumbnail-processing API
* Pillow-based image processing
* MinIO S3-compatible object storage
* Dockerized application with non-root execution
* Kubernetes deployment on Minikube
* Liveness and readiness probes
* CPU and memory requests/limits
* Persistent storage with Kubernetes PVC
* Helm-based deployment packaging
* Knative Serving with autoscaling and scale-to-zero
* GitHub Actions CI
* Argo CD GitOps deployment and self-healing
* Prometheus metrics and Grafana dashboards
* OpenTelemetry distributed tracing with Jaeger
* Kubernetes security controls and NetworkPolicy
* Trivy container image scanning
* Controlled failure and recovery testing
* Operational troubleshooting documentation

## Technology Stack

| Area               | Technologies                        |
| ------------------ | ----------------------------------- |
| Application        | Python, FastAPI, Pillow             |
| Object Storage     | MinIO                               |
| Containerization   | Docker                              |
| Orchestration      | Kubernetes, Minikube                |
| Packaging          | Helm                                |
| Serverless Serving | Knative Serving                     |
| CI                 | GitHub Actions                      |
| GitOps             | Argo CD, Git                        |
| Metrics            | Prometheus                          |
| Dashboards         | Grafana                             |
| Tracing            | OpenTelemetry, Jaeger               |
| Security           | Trivy, Kubernetes security controls |

## Application Flow

```text
Client
  │
  ▼
FastAPI
  │
  ├── Validate image
  ├── Store original → MinIO
  ├── Retrieve original
  ├── Generate thumbnail → Pillow
  └── Store thumbnail → MinIO
```

### API Endpoints

| Endpoint           | Purpose                                  |
| ------------------ | ---------------------------------------- |
| `POST /thumbnails` | Upload an image and generate a thumbnail |
| `GET /health`      | Process health                           |
| `GET /ready`       | Application readiness                    |
| `GET /metrics/`    | Prometheus metrics                       |

## Local Development

### Requirements

* Python 3.10+
* Docker
* Docker Compose
* Minikube
* kubectl
* Helm

Create a Python environment and install dependencies:

```bash
cd app

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Run the application locally:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Run tests:

```bash
pytest -q
```

The project also provides Docker Compose configuration for local
application and MinIO development.

## Docker

Build the application image:

```bash
docker build -t thumbnail-service:0.1.9 ./app
```

Run the container:

```bash
docker run --rm \
  -p 8000:8000 \
  thumbnail-service:0.1.9
```

The image includes a Docker healthcheck and runs the application as a
non-root user.

## Kubernetes Deployment

Start Minikube:

```bash
minikube start --driver=docker
```

Deploy using Helm:

```bash
helm upgrade --install thumbnail-pipeline \
  ./helm/thumbnail-pipeline \
  -n thumbnail-pipeline \
  --create-namespace
```

Verify:

```bash
kubectl get pods -n thumbnail-pipeline
kubectl get svc -n thumbnail-pipeline
kubectl get pvc -n thumbnail-pipeline
```

Access the application locally:

```bash
kubectl port-forward \
  -n thumbnail-pipeline \
  svc/thumbnail-service 8000:8000
```

Then:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Knative

The project also includes a Knative Serving configuration.

The Knative manifest is located at:

```text
k8s/knative/thumbnail-service.yaml
```

Knative was used to study and demonstrate:

* revisions
* request-driven serving
* autoscaling
* scale-to-zero
* cold-start behavior

Standard Kubernetes Deployment remains the core deployment model.

See [`docs/knative.md`](docs/knative.md) for details.

## CI and GitOps

### CI

GitHub Actions validates changes by:

```text
Code
  ↓
Tests
  ↓
Docker Build
  ↓
Container Runtime Validation
  ↓
Healthcheck
```

The current workflow builds and validates the image but does not publish
it to an external container registry.

### GitOps

Argo CD manages the Kubernetes deployment from Git:

```text
Git Repository
      ↓
   Argo CD
      ↓
 Helm Chart
      ↓
 Kubernetes
```

The project demonstrates synchronization, drift detection, and
self-healing.

## Observability

The project includes:

* **Prometheus** — application metrics
* **Grafana** — dashboards
* **OpenTelemetry** — application instrumentation
* **Jaeger** — distributed traces
* **Kubernetes/application logs** — operational troubleshooting

The thumbnail-processing workflow includes custom tracing spans for
important processing and storage operations.

See [`docs/observability.md`](docs/observability.md).

## Security

Security controls include:

* non-root application container
* `runAsNonRoot`
* `RuntimeDefault` seccomp
* dropped Linux capabilities
* disabled privilege escalation
* disabled automatic ServiceAccount token mounting
* Kubernetes Secrets
* Pod Security Admission labels
* NetworkPolicy
* resource requests and limits
* Trivy image scanning

The verified Trivy scan reported `0` CRITICAL findings, while remaining
HIGH findings were associated with Debian OS packages. The project does
not claim that the image is vulnerability-free.

See [`docs/security.md`](docs/security.md).

## Failure & Recovery

Failure engineering was used to deliberately test system behavior.

Examples include:

```text
Application process failure
        ↓
Container restart
        ↓
Health / readiness verification
```

```text
Pod deletion
        ↓
Deployment creates replacement Pod
        ↓
Application recovers
```

```text
NetworkPolicy drift
        ↓
Argo CD detects drift
        ↓
Desired state restored
```

```text
Node cordon
        ↓
Replacement Pod Pending
        ↓
Node uncordon
        ↓
Pod scheduled and Running
```

The experiments were performed on a single-node Minikube environment.

See [`docs/failure-engineering.md`](docs/failure-engineering.md) and
[`docs/troubleshooting.md`](docs/troubleshooting.md).

## Project Documentation

* [`Architecture`](docs/architecture.md)
* [`Containerization`](docs/containerization.md)
* [`Kubernetes`](docs/kubernetes.md)
* [`MinIO`](docs/minio.md)
* [`Helm`](docs/helm.md)
* [`Knative`](docs/knative.md)
* [`CI`](docs/ci.md)
* [`GitOps`](docs/gitops.md)
* [`Observability`](docs/observability.md)
* [`Security`](docs/security.md)
* [`Failure Engineering`](docs/failure-engineering.md)
* [`Troubleshooting`](docs/troubleshooting.md)
* [`Project Status`](docs/project-status-devops.md)

## Repository Structure

```text
cloud-native-thumbnail-pipeline/
├── app/                    # FastAPI application and tests
├── helm/                   # Helm charts
├── k8s/                    # Kubernetes and Knative manifests
├── argocd/                 # Argo CD Application
├── monitoring/             # Prometheus and Grafana configuration
├── docs/                   # Technical documentation
├── .github/workflows/      # GitHub Actions CI
├── docker-compose.yml      # Local development environment
├── README.md
├── LICENSE
└── .gitignore
```

## Project Status

**Status: ✅ Complete**

The technical implementation covers application development,
containerization, Kubernetes, Helm, Knative, CI, GitOps, observability,
security, controlled failure/recovery testing and documentation.


## License

See [`LICENSE`](LICENSE).
