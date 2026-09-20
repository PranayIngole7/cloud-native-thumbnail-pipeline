# Cloud-Native Thumbnail Pipeline

A small image-processing service designed to demonstrate modern DevOps and cloud-native engineering practices.

The application accepts an image, stores the original in MinIO object storage, retrieves it for Pillow-based thumbnail processing, and stores the generated thumbnail back in MinIO. The application remains deliberately small so the project can focus on containerization, object storage, Kubernetes, CI/CD, observability, security, and failure testing.

> **Core principle:** The application stays deliberately small; the infrastructure and operational engineering provide the depth.

---

## Overview

The project currently provides a containerized thumbnail-processing API using Python and FastAPI.

### Implemented

- FastAPI application
- Pillow-based image processing
- Docker containerization
- Non-root application container
- Docker healthcheck
- MinIO S3-compatible object storage
- Persistent object storage using Docker volumes
- Original and thumbnail object persistence
- Storage abstraction and failure handling
- Automated application tests
- Docker-based failure and recovery verification

### Planned Platform Extensions

The project will progressively introduce:

- Kubernetes orchestration
- Minikube for local Kubernetes development
- Helm-based application packaging
- Knative Serving
- GitHub Actions CI
- Container registry integration
- Argo CD GitOps deployment
- OpenTelemetry
- Prometheus
- Grafana
- Trivy security scanning
- Kubernetes security controls
- Additional failure and recovery testing

The project is intentionally designed for local development and learning without requiring paid cloud infrastructure.
---

## Goals

The project is intended to demonstrate practical understanding of:

- containerized application development
- Docker image design
- Kubernetes fundamentals
- Kubernetes resource management
- Helm
- serverless/container-based serving with Knative
- CI pipelines
- container image scanning
- container registries
- GitOps
- Argo CD reconciliation
- object storage
- application observability
- metrics and dashboards
- distributed-system failure scenarios
- Kubernetes security practices
- reproducible local environments

The goal is to build a **small application surrounded by realistic production-style engineering practices**.

---

## Architecture

### Current Architecture

```text
Client
   │
   ▼
FastAPI Application
   │
   ├── Validate Image
   │
   ├── Store Original
   │       │
   │       ▼
   │     MinIO
   │
   ├── Retrieve Original
   │
   ├── Process with Pillow
   │
   └── Store Thumbnail
           │
           ▼
         MinIO
```
### Planned Architecture
```text
Developer
   │
   │ git push
   ▼
GitHub
   │
   ▼
GitHub Actions
   ├── Tests
   ├── Build
   ├── Trivy Scan
   └── Docker Image
          │
          ▼
   Container Registry
          │
          ▼
   GitOps Configuration
          │
          ▼
       Argo CD
          │
          ▼
   Minikube / Kubernetes
          │
          ▼
    Knative Serving
          │
          ▼
 Thumbnail API
 FastAPI + Pillow
          │
          ▼
        MinIO
```

Observability is provided through:

```text
Application
    │
    ├── OpenTelemetry
    │
    └── Prometheus
            │
            ▼
         Grafana
```

The detailed architecture is documented in [`docs/architecture.md`](docs/architecture.md).

---

## Application Workflow

The current API provides three endpoints:

| Endpoint           | Purpose                                  |
| ------------------ | ---------------------------------------- |
| `POST /thumbnails` | Upload an image and generate a thumbnail |
| `GET /health`      | Basic process health                     |
| `GET /ready`       | Application readiness                    |

The thumbnail creation flow is:

```text
Client
  │
  ▼
FastAPI
  │
  ├── Validate upload
  │
  ├── Generate image ID
  │
  ├── Store original in MinIO
  │
  ├── Retrieve original from MinIO
  │
  ├── Process image with Pillow
  │
  ├── Generate thumbnail
  │
  └── Store thumbnail in MinIO
  │
  ▼
Return thumbnail
```

---

## Technology Stack

### Application

- Python
- FastAPI
- Pillow
- pytest
- MinIO

### Containerization

- Docker Engine
- Docker

### Kubernetes Platform

- Kubernetes
- Minikube
- kubectl
- Helm

### Serverless Serving

- Knative Serving

### CI/CD and GitOps

- GitHub Actions
- Container Registry
- Argo CD
- Git

### Observability

- OpenTelemetry
- Prometheus
- Grafana

### Security

- Trivy
- Kubernetes security controls

---

## Repository Structure

```text
cloud-native-thumbnail-pipeline/
│
├── app/
│   ├── src/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── helm/
│   └── thumbnail-service/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── k8s/
│   └── infrastructure/
│
├── gitops/
│   ├── dev/
│   └── argocd/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── architecture.md
│   ├── kubernetes.md
│   ├── knative.md
│   ├── gitops.md
│   ├── observability.md
│   ├── security.md
│   ├── failure-testing.md
│   └── troubleshooting.md
│
├── README.md
├── LICENSE
└── .gitignore
```

### Responsibility boundaries

- `app/` — application implementation and tests
- `helm/` — application deployment packaging
- `k8s/` — Kubernetes infrastructure configuration
- `gitops/` — desired deployment state
- `.github/` — CI workflows
- `docs/` — detailed technical documentation

The project keeps application code separate from infrastructure and delivery configuration.

---

## DevOps Lifecycle

The project follows this general lifecycle:

```text
Code
  ↓
Test
  ↓
Build
  ↓
Security Scan
  ↓
Publish Image
  ↓
Update Desired State
  ↓
Argo CD Reconciliation
  ↓
Kubernetes / Knative
  ↓
Observe
  ↓
Test Failures
  ↓
Improve
```

GitHub Actions is responsible for validating and building artifacts.

Argo CD is responsible for reconciling the declared deployment state with the Kubernetes environment.

The primary deployment mechanism is therefore GitOps rather than directly applying deployment manifests from the CI pipeline.

---

## Object Storage

MinIO provides S3-compatible object storage for the application.

The logical storage layout is:

```text
thumbnail-pipeline/
├── originals/
│   └── <image-id>.jpg
│
└── thumbnails/
    └── <image-id>.jpg
```

The container filesystem is not used as persistent image storage.

---

## Observability

The project will progressively introduce:

- application metrics
- request telemetry
- distributed tracing concepts
- Prometheus collection
- Grafana dashboards

Observability should answer practical operational questions such as:

- How many requests were received?
- How many requests failed?
- What is the request latency?
- Did MinIO operations fail?
- Did thumbnail processing fail?
- What happens when the application restarts?
- How does the service behave when it scales?

Observability components will be introduced incrementally rather than all at once.

---

## Security

Security practices demonstrated by the project include:

- non-root containers where practical
- read-only filesystems where practical
- dropped Linux capabilities where appropriate
- Kubernetes resource limits
- Kubernetes security contexts
- separation of configuration and secrets
- container vulnerability scanning with Trivy
- avoiding hard-coded credentials

The project focuses on practical container and Kubernetes security rather than building a separate authentication system.

---

## Failure Testing

Failure testing is a core part of the project.

Scenarios include:

- invalid image uploads
- empty uploads
- MinIO unavailable
- application crashes
- Pillow processing failures
- original successfully stored but thumbnail generation failing
- thumbnail storage failure
- vulnerable container image
- GitOps configuration drift

The objective is to understand not only how the system works when healthy, but also how it behaves when individual components fail.

---

## Design Philosophy

The project intentionally avoids unnecessary complexity.

The following are outside the initial scope:

- Kafka
- Redis
- AI/LLM integration
- authentication systems
- multiple application microservices
- service mesh
- custom Kubernetes operators/controllers
- paid cloud infrastructure
- multi-region deployment
- multi-cloud deployment

Complexity is added only when it demonstrates a meaningful engineering concept.

---

## Documentation

Detailed documentation will be maintained under `docs/`.

- [`Architecture`](docs/architecture.md)
- [`Kubernetes`](docs/kubernetes.md)
- [`Knative`](docs/knative.md)
- [`GitOps`](docs/gitops.md)
- [`Observability`](docs/observability.md)
- [`Security`](docs/security.md)
- [`Failure Testing`](docs/failure-testing.md)
- [`Troubleshooting`](docs/troubleshooting.md)

---

## Project Status

The repository is currently in the foundation and architecture stage.

The initial work focuses on establishing:

1. project scope
2. repository structure
3. architecture
4. application boundaries
5. infrastructure responsibilities
6. CI/CD and GitOps responsibilities
7. observability and security strategy

Implementation will proceed incrementally from the application foundation toward the complete cloud-native platform.

---

## License

See [`LICENSE`](LICENSE).