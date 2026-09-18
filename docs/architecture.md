# Architecture

## 1. Purpose

The Cloud-Native Thumbnail Pipeline is intentionally built around a small application and a deeper operational platform.

The application performs one primary business function:

> Accept an image, generate a thumbnail, and store both objects.

The surrounding platform demonstrates modern DevOps and cloud-native engineering practices including:

- containerization
- Kubernetes orchestration
- serverless-style serving
- CI
- container security scanning
- GitOps
- observability
- failure testing

The architecture is designed for local development using Minikube rather than paid cloud infrastructure.

---

## 2. Core Principle

> **The application stays deliberately small; the infrastructure and operational engineering provide the depth.**

This prevents application complexity from hiding the DevOps concepts being demonstrated.

There is intentionally one primary application service rather than multiple microservices.

---

## 3. High-Level Architecture

```text
                         Developer
                             │
                             │ git push
                             ▼
                          GitHub
                             │
                             ▼
                    ┌─────────────────┐
                    │ GitHub Actions  │
                    │                 │
                    │ Test            │
                    │ Build           │
                    │ Trivy Scan      │
                    │ Publish Image    │
                    └────────┬────────┘
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
                 ┌───────────────────────┐
                 │ Minikube / Kubernetes │
                 │                       │
                 │   Knative Serving     │
                 │          │            │
                 │          ▼            │
                 │   Thumbnail API       │
                 │   FastAPI + Pillow    │
                 │          │            │
                 │          ▼            │
                 │        MinIO          │
                 └───────────────────────┘
```

Observability operates alongside the application:

```text
Thumbnail API
     │
     ├──────── OpenTelemetry
     │
     └──────── Metrics
                   │
                   ▼
               Prometheus
                   │
                   ▼
                Grafana
```

---

## 4. Architectural Layers

The system is divided into five logical areas.

### 4.1 Application

Responsible for:

- HTTP API
- request validation
- image processing
- object storage interaction
- application health
- application telemetry

Technology:

- Python
- FastAPI
- Pillow
- MinIO client
- pytest

---

### 4.2 Platform

Responsible for running the application.

Technology:

- Docker
- Kubernetes
- Minikube
- kubectl
- Helm
- Knative Serving

Responsibilities include:

- workload scheduling
- networking
- configuration
- secrets
- health probes
- resource management
- restart/recovery
- security contexts
- scaling

---

### 4.3 Delivery

Responsible for getting verified application artifacts into the runtime environment.

Technology:

- Git
- GitHub
- GitHub Actions
- Container Registry
- Argo CD

The delivery model separates:

```text
CI
=
Build and verify artifacts

GitOps
=
Declare desired deployment state

Argo CD
=
Reconcile desired state with Kubernetes
```

---

### 4.4 Observability

Responsible for understanding runtime behavior.

Technology:

- OpenTelemetry
- Prometheus
- Grafana

The observability layer should expose enough information to investigate:

- request volume
- request failures
- latency
- storage failures
- processing failures
- application restarts
- scaling behavior

---

### 4.5 Security

Security is implemented at multiple layers.

Application/container:

- minimal runtime image
- non-root execution where practical
- no hard-coded secrets

Kubernetes:

- security contexts
- dropped capabilities where appropriate
- read-only filesystem where practical
- resource limits
- secret/config separation

Supply chain:

- Trivy image scanning
- CI integration

---

## 5. Application Architecture

The application is intentionally a single FastAPI service.

```text
Client
  │
  ▼
FastAPI
  │
  ├── Validation
  │
  ├── Image ID generation
  │
  ├── MinIO original upload
  │
  ├── Pillow processing
  │
  ├── MinIO thumbnail upload
  │
  └── Response
```

The application does not contain separate services for:

- upload
- image processing
- storage
- metadata

Those responsibilities remain within one small service.

This keeps the application understandable while allowing the platform architecture to demonstrate distributed-system concepts.

---

## 6. API Design

The initial API contains:

### `POST /thumbnails`

Accepts an image upload.

Conceptual flow:

```text
Receive upload
    ↓
Validate content
    ↓
Generate image ID
    ↓
Store original
    ↓
Open image with Pillow
    ↓
Generate thumbnail
    ↓
Store thumbnail
    ↓
Return metadata
```

---

### `GET /thumbnails/{id}`

Retrieves the generated thumbnail associated with the image ID.

---

### `GET /health`

Provides basic process health.

This endpoint answers:

> Is the application process running?

---

### `GET /ready`

Provides readiness information.

This endpoint answers:

> Is the application ready to serve requests?

The exact readiness dependencies will be finalized during implementation.

---

## 7. Image Processing

Initial supported formats:

- JPEG
- PNG
- WEBP

The application validates the actual image content rather than relying only on the filename extension.

Thumbnail generation uses a fixed maximum dimension while preserving aspect ratio.

Examples:

```text
1920 × 1080
      ↓
320 × 180

1000 × 1500
      ↓
approximately 213 × 320
```

The exact maximum dimensions and image encoding settings will be finalized during implementation.

---

## 8. Object Storage

MinIO provides persistent object storage.

Logical layout:

```text
thumbnail-pipeline/
├── originals/
│   └── <image-id>.<extension>
│
└── thumbnails/
    └── <image-id>.<extension>
```

The same logical image ID identifies the original and generated thumbnail.

The application does not depend on local container filesystem persistence.

---

## 9. Storage Consistency

MinIO operations are separate storage operations and are not automatically equivalent to a database transaction.

For example:

```text
Store original
      │
      ▼
Generate thumbnail
      │
      X
   FAILURE
```

At this point the original may exist while the thumbnail does not.

This creates an intentional failure scenario.

The implementation must define how this partial state is handled.

Possible strategies include:

1. delete the original when thumbnail generation fails
2. retain the original and record failure state
3. introduce metadata describing processing state

The initial implementation should choose the simplest approach that provides predictable behavior.

This decision will be documented after implementation and testing.

---

## 10. Docker Architecture

The application is packaged as a Docker image.

The image contains:

- Python runtime
- application dependencies
- FastAPI application
- Pillow
- required configuration

The image should be:

- reproducible
- reasonably small
- configured through environment variables
- free of hard-coded secrets
- non-root where practical

The container should not depend on files written to the local filesystem for persistent image storage.

---

## 11. Kubernetes Architecture

Minikube provides the local Kubernetes cluster.

Kubernetes is responsible for:

- workload execution
- networking
- configuration
- secrets
- resource limits
- health probes
- restart behavior
- security contexts

The project intentionally uses Kubernetes concepts that are useful for production environments without attempting to reproduce an entire production platform locally.

---

## 12. Helm

Helm packages the application deployment configuration.

The Helm chart is responsible for application-level deployment configuration such as:

- image
- replicas or serving configuration
- resources
- environment variables
- secrets/configuration references
- service configuration
- health probes
- security settings

Infrastructure dependencies remain conceptually separate from the application chart where practical.

---

## 13. Knative Serving

Knative Serving provides the serverless-style HTTP serving layer.

Its purpose in this project is to demonstrate:

- request-driven serving
- revision-based deployment concepts
- dynamic scaling
- serverless-style application lifecycle
- potentially scale-to-zero behavior

Local Minikube behavior must be validated experimentally.

The project will not assume that every Knative production feature behaves identically in the local environment.

Knative is therefore used because it demonstrates a meaningful platform concept, not simply because it is another technology to install.

---

## 14. CI Architecture

GitHub Actions performs continuous integration.

The initial pipeline is conceptually:

```text
git push
   │
   ▼
GitHub Actions
   │
   ├── Install dependencies
   │
   ├── Run tests
   │
   ├── Build Docker image
   │
   ├── Run Trivy scan
   │
   └── Publish image
```

CI should verify the artifact before it becomes available for deployment.

The exact image tagging strategy will be finalized during implementation.

---

## 15. GitOps Architecture

Deployment configuration is maintained as desired state.

The intended flow is:

```text
Application Change
       │
       ▼
GitHub Actions
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
Kubernetes
```

Argo CD continuously compares the desired state with the cluster state.

This allows the project to demonstrate:

- declarative deployment
- reconciliation
- drift detection
- Git as the deployment source of truth

GitHub Actions should not become the primary mechanism for directly applying Kubernetes resources.

---

## 16. Observability Architecture

Observability will be introduced incrementally.

Conceptually:

```text
                  Thumbnail API
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   OpenTelemetry                Metrics
          │                         │
          │                         ▼
          │                    Prometheus
          │                         │
          └────────────┬────────────┘
                       ▼
                    Grafana
```

The goal is to correlate application behavior with infrastructure behavior.

Example investigation:

```text
Request latency increased
        ↓
Check application metrics
        ↓
Check thumbnail processing time
        ↓
Check MinIO interaction
        ↓
Check container/resource behavior
        ↓
Check Kubernetes/Knative behavior
```

This turns observability into an operational debugging tool rather than simply a dashboard exercise.

---

## 17. Security Architecture

Security controls are layered.

### Container

- run as non-root
- minimize unnecessary packages
- avoid hard-coded credentials
- scan images with Trivy

### Kubernetes

- security contexts
- resource limits
- read-only filesystem where practical
- dropped capabilities where appropriate
- explicit configuration and secret handling

### CI

```text
Source
  ↓
Test
  ↓
Build
  ↓
Trivy Scan
  ↓
Publish only according to project policy
```

The initial project does not implement a custom authentication system.

---

## 18. Failure Architecture

Failure testing is treated as a first-class engineering concern.

Important scenarios include:

### Invalid input

```text
Client
  ↓
Invalid image
  ↓
Validation failure
  ↓
Controlled API response
```

### MinIO failure

```text
Application
    ↓
MinIO
    X
 unavailable
    ↓
Application handles storage error
```

### Processing failure

```text
Original stored
      ↓
Pillow processing
      X
    failure
```

This scenario is particularly important because it can produce partial state.

### Application crash

```text
Running container
      ↓
Application crash
      ↓
Kubernetes/Knative detects failure
      ↓
Workload recovery
```

### GitOps drift

```text
Desired state ≠ Cluster state
          ↓
       Argo CD
          ↓
     Reconciliation
```

These scenarios demonstrate operational behavior rather than only happy-path functionality.

---

## 19. Repository Boundaries

```text
app/
    Application implementation

helm/
    Application deployment packaging

k8s/
    Kubernetes infrastructure configuration

gitops/
    Desired deployment state

.github/
    CI automation

docs/
    Technical documentation
```

The primary boundary is:

```text
Application
    ≠
Infrastructure
    ≠
Delivery
```

Keeping these boundaries clear makes the project easier to reason about and allows individual platform technologies to be introduced incrementally.

---

## 20. Environment Strategy

The initial environment is local development.

```text
Developer Machine
       │
       ▼
Docker Engine
       │
       ▼
Minikube
       │
       ▼
Kubernetes
       │
       ├── Knative
       ├── Thumbnail API
       └── MinIO
```

The project does not initially introduce separate:

- development
- staging
- production

environments.

The objective is to establish a complete, reproducible local platform first.

---

## 21. Technology Selection Rationale

### Minikube

Selected for beginner-friendly local Kubernetes learning and straightforward Kubernetes experimentation.

### Docker Engine

Selected as the container runtime on the Linux development environment.

### Helm

Provides reusable and parameterized Kubernetes application packaging.

### Knative Serving

Adds a meaningful serverless-style serving and scaling layer.

### GitHub Actions

Provides accessible CI automation integrated with the source repository.

### Argo CD

Demonstrates declarative GitOps and reconciliation.

### MinIO

Provides local S3-compatible object storage without requiring paid cloud infrastructure.

### OpenTelemetry

Provides a standard telemetry model for application instrumentation.

### Prometheus

Provides metrics collection and querying.

### Grafana

Provides operational visualization.

### Trivy

Provides container vulnerability scanning.

---

## 22. Explicitly Out of Scope

The initial architecture intentionally excludes:

- Kafka
- Redis
- AI/LLM
- authentication systems
- multiple application microservices
- service mesh
- custom Kubernetes operators/controllers
- paid cloud infrastructure
- multi-region architecture
- multi-cloud architecture
- K3s
- kind
- Docker Desktop

These technologies may be useful in other projects, but adding them here would increase complexity without improving the core learning objective.

---

## 23. Architecture Evolution

Architecture changes should follow the project's development workflow:

```text
Concept
   ↓
Why
   ↓
Design
   ↓
Implement
   ↓
Test
   ↓
Debug
   ↓
Improve
   ↓
Document
   ↓
Interview Questions
   ↓
Next Phase
```

A new technology should be introduced only when there is a clear engineering reason for it.

The project should remain understandable at every stage.

---

## 24. Initial Architecture Decision

The initial architecture is therefore:

```text
FastAPI + Pillow
        │
        ▼
      MinIO
        │
        ▼
Docker Container
        │
        ▼
Kubernetes / Minikube
        │
        ▼
Knative Serving
        │
        ├──────── Observability
        │          ├── OpenTelemetry
        │          ├── Prometheus
        │          └── Grafana
        │
        └──────── Delivery
                   ├── GitHub Actions
                   ├── Container Registry
                   └── Argo CD
```

This provides a deliberately small application with a broad but coherent DevOps learning surface.