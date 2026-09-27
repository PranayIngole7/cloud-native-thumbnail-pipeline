# Architecture

## 1. Purpose

The Cloud-Native Thumbnail Pipeline combines a deliberately small image-processing application with a broader cloud-native and DevOps platform.

The application:

* accepts an image upload
* validates the image
* stores the original in MinIO
* retrieves the original for processing
* generates a thumbnail using Pillow
* stores the generated thumbnail in MinIO
* exposes health and readiness endpoints

The surrounding platform demonstrates:

* Docker containerization
* Kubernetes orchestration
* Helm packaging
* Knative Serving
* GitHub Actions CI
* GitOps with Argo CD
* OpenTelemetry tracing
* Prometheus metrics
* Grafana dashboards
* Jaeger trace visualization
* Kubernetes security controls
* Trivy image scanning
* failure and recovery testing

The project is designed for local development and experimentation using Minikube.

---

## 2. Architectural Principle

> **The application stays deliberately small; the infrastructure and operational engineering provide the depth.**

The project intentionally uses one primary application service rather than multiple application microservices. This keeps the business logic understandable while allowing the platform to demonstrate realistic operational concerns.

---

## 3. High-Level Architecture

```text
                         Developer
                             │
                             │ git push / pull request
                             ▼
                          GitHub
                             │
                             ▼
                    ┌─────────────────┐
                    │ GitHub Actions  │
                    │                 │
                    │ Dependencies    │
                    │ Tests           │
                    │ Docker Build    │
                    │ Image Validation│
                    └─────────────────┘

                             │
                             │ Git repository
                             ▼
                         Argo CD
                             │
                             │ GitOps reconciliation
                             ▼
                 ┌─────────────────────────┐
                 │   Minikube / Kubernetes │
                 │                         │
                 │  Helm-managed workload  │
                 │          │              │
                 │          ▼              │
                 │   Thumbnail API         │
                 │   FastAPI + Pillow      │
                 │          │              │
                 │          ▼              │
                 │        MinIO             │
                 │          │              │
                 │       Persistent         │
                 │        Volume             │
                 └─────────────────────────┘

      Observability
            │
            ├── OpenTelemetry → Jaeger
            ├── Prometheus
            └── Grafana
```

Knative Serving is also installed and configured in the Kubernetes environment to demonstrate revision-based and request-driven serving concepts.

---

## 4. Application Architecture

The application is a single FastAPI service.

```text
Client
  │
  ▼
FastAPI
  │
  ├── Validate image
  │
  ├── Generate image ID
  │
  ├── Store original ──────► MinIO
  │
  ├── Retrieve original ◄── MinIO
  │
  ├── Generate thumbnail
  │        │
  │        └── Pillow
  │
  └── Store thumbnail ─────► MinIO
```

The application contains the following primary responsibilities:

* HTTP request handling
* image validation
* image ID generation
* image processing
* MinIO object storage operations
* health/readiness endpoints
* logging
* metrics
* OpenTelemetry tracing
* controlled error handling

There are no separate application services for upload, processing, storage, or metadata.

---

## 5. API

The primary application endpoints are:

| Endpoint               | Purpose                                   |
| ---------------------- | ----------------------------------------- |
| `POST /thumbnails`     | Upload an image and generate a thumbnail  |
| `GET /thumbnails/{id}` | Retrieve a generated thumbnail            |
| `GET /health`          | Process health check                      |
| `GET /ready`           | Application readiness check               |
| `GET /metrics/`        | Prometheus-compatible application metrics |

The thumbnail processing flow is:

```text
Receive upload
      │
      ▼
Validate image
      │
      ▼
Generate image ID
      │
      ▼
Store original in MinIO
      │
      ▼
Retrieve original
      │
      ▼
Process with Pillow
      │
      ▼
Store thumbnail in MinIO
      │
      ▼
Return response
```

---

## 6. Object Storage

MinIO provides S3-compatible object storage for the application.

The application stores original and generated thumbnail objects separately.

```text
MinIO
└── thumbnail-pipeline/
    ├── originals/
    │   └── <image-id>.<extension>
    │
    └── thumbnails/
        └── <image-id>.<extension>
```

MinIO data is backed by a Kubernetes PersistentVolumeClaim.

The application does not use its container filesystem as the persistent storage layer for uploaded images.

---

## 7. Kubernetes Architecture

Minikube provides the local Kubernetes environment.

Kubernetes is responsible for:

* workload scheduling
* service discovery
* networking
* configuration
* secrets
* health probes
* resource requests and limits
* container restart behavior
* security contexts
* persistent storage

The application is deployed as a Kubernetes Deployment and exposed through a ClusterIP Service.

The MinIO deployment uses:

* Deployment
* Service
* Secret
* PersistentVolumeClaim
* initialization Job

The application and MinIO are isolated within the `thumbnail-pipeline` namespace.

---

## 8. Helm Architecture

Helm provides reusable and parameterized deployment packaging.

The project Helm chart manages the application platform configuration, including:

* application image
* replica count
* service
* resources
* configuration
* secrets
* health probes
* MinIO deployment
* MinIO service
* MinIO persistent storage
* MinIO initialization

Configuration is maintained through `values.yaml`.

Local secret values are kept outside version-controlled configuration.

Helm supports the deployment lifecycle:

```text
Install
   ↓
Upgrade
   ↓
Verify
   ↓
Rollback
```

---

## 9. Knative Serving

Knative Serving is included to demonstrate serverless-style Kubernetes serving concepts.

The project uses Knative to explore:

* revisions
* request-driven serving
* traffic management
* autoscaling
* scale-to-zero behavior
* cold-start behavior
* revision recovery

Knative is an additional platform capability rather than a requirement for the core thumbnail-processing application.

This allows the project to demonstrate both conventional Kubernetes deployment and serverless-style serving concepts without making the application itself dependent on Knative-specific business logic.

---

## 10. CI Architecture

GitHub Actions provides continuous integration.

The current CI workflow performs:

```text
Git push / Pull Request
        │
        ▼
GitHub Actions
        │
        ├── Set up Python 3.10
        ├── Install dependencies
        ├── Run pytest
        ├── Build Docker image
        ├── Inspect image
        ├── Run container
        └── Verify Docker healthcheck
```

The CI workflow verifies that application changes can be tested, containerized, and started successfully.

Container vulnerability scanning with Trivy was performed as part of the project's security work and is documented separately.

The current CI workflow does not publish images to an external container registry.

---

## 11. GitOps and Argo CD

Argo CD provides GitOps-based Kubernetes deployment management.

The desired deployment configuration is stored in Git and reconciled against the Kubernetes cluster.

```text
Git Repository
      │
      ▼
   Argo CD
      │
      ├── Compare desired state
      │
      ├── Detect drift
      │
      └── Reconcile
             │
             ▼
        Kubernetes
```

The project demonstrates:

* declarative deployment
* Git-based desired state
* synchronization
* drift detection
* reconciliation
* self-healing
* deployment recovery

GitHub Actions performs CI validation; Argo CD performs GitOps reconciliation.

These responsibilities remain separate.

---

## 12. Observability Architecture

The project provides application and platform observability through metrics, logs, and distributed tracing.

```text
                    Thumbnail API
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        Logs        OpenTelemetry     Metrics
          │              │              │
          │              ▼              ▼
          │           Jaeger        Prometheus
          │                             │
          │                             ▼
          └──────────────────────────► Grafana
```

### Metrics

Prometheus collects application metrics for operational visibility.

### Dashboards

Grafana provides visualization of collected metrics.

### Tracing

OpenTelemetry instruments application operations and exports traces to Jaeger.

Custom application spans include important processing and storage operations.

### Logs

Application logs provide request and runtime information useful during troubleshooting.

Observability is also used during failure testing to correlate application behavior with Kubernetes events and workload state.

---

## 13. Security Architecture

Security controls are applied at the container and Kubernetes layers.

### Container security

The application container:

* runs as a non-root user
* drops unnecessary Linux capabilities
* prevents privilege escalation
* uses the Kubernetes runtime default seccomp profile
* avoids hard-coded credentials

### Kubernetes security

The deployment uses:

* security contexts
* resource requests and limits
* Kubernetes Secrets
* NetworkPolicy controls
* namespace-level Pod Security labels
* disabled automatic service-account token mounting where applicable

The application does not require access to the Kubernetes API, so no custom application RBAC permissions are required.

### Image security

Trivy is used to scan container images for known vulnerabilities.

The project records the scan results and remediation performed rather than claiming that the final image is vulnerability-free.

---

## 14. Failure and Recovery Architecture

Failure testing is part of the project's operational verification.

Tested scenarios include:

* application/container termination
* Pod deletion and replacement
* MinIO Pod failure
* missing configuration Secret
* GitOps drift
* readiness probe failure
* liveness configuration failure
* controlled memory-pressure testing
* Kubernetes scheduling failure
* persistent-volume verification
* final recovery verification

The tests demonstrated Kubernetes restart/replacement behavior, GitOps reconciliation, storage mounting, scheduling behavior, and troubleshooting workflows.

Not every failure experiment reproduced the exact intended failure condition. For example, a clean liveness-triggered restart and `OOMKilled` condition were not successfully reproduced during the controlled tests. These limitations are documented in the failure-engineering documentation.

---

## 15. Security and Delivery Boundaries

The project separates three major concerns:

```text
Application
    │
    ├── FastAPI
    ├── Pillow
    └── MinIO client

Platform
    │
    ├── Kubernetes
    ├── Minikube
    ├── Helm
    └── Knative

Delivery
    │
    ├── GitHub
    ├── GitHub Actions
    └── Argo CD
```

This separation keeps application functionality independent from deployment and delivery mechanisms.

---

## 16. Repository Structure

```text
cloud-native-thumbnail-pipeline/
│
├── app/
│   ├── src/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── helm/
│   └── thumbnail-pipeline/
│
├── k8s/
│   ├── application/
│   ├── minio/
│   ├── knative/
│   └── observability/
│
├── monitoring/
│   ├── prometheus/
│   └── grafana/
│
├── argocd/
│   └── application.yaml
│
├── .github/
│   └── workflows/
│
├── docs/
│
├── docker-compose.yml
├── README.md
└── LICENSE
```

The main architectural boundaries are:

```text
Application
    ≠
Platform configuration
    ≠
Delivery automation
    ≠
Documentation
```

---

## 17. Environment Strategy

The project uses a local Kubernetes environment:

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
       ├── Thumbnail API
       ├── MinIO
       ├── Knative
       ├── Argo CD
       ├── Jaeger
       ├── Prometheus
       └── Grafana
```

The project intentionally focuses on a reproducible local environment rather than introducing separate development, staging, and production clusters or paid cloud infrastructure.

---

## 18. Technology Selection

| Technology       | Purpose                             |
| ---------------- | ----------------------------------- |
| Python / FastAPI | Thumbnail-processing API            |
| Pillow           | Image processing                    |
| MinIO            | S3-compatible object storage        |
| Docker           | Application containerization        |
| Kubernetes       | Container orchestration             |
| Minikube         | Local Kubernetes environment        |
| Helm             | Kubernetes application packaging    |
| Knative Serving  | Serverless-style serving concepts   |
| GitHub Actions   | Continuous integration              |
| Argo CD          | GitOps continuous delivery          |
| OpenTelemetry    | Application tracing instrumentation |
| Jaeger           | Trace collection and visualization  |
| Prometheus       | Metrics collection                  |
| Grafana          | Metrics visualization               |
| Trivy            | Container vulnerability scanning    |

---

## 19. Explicitly Out of Scope

The project intentionally does not introduce:

* multiple application microservices
* Kafka
* Redis
* service mesh
* custom Kubernetes operators
* custom Kubernetes controllers
* multi-region deployment
* multi-cloud deployment
* paid cloud infrastructure
* authentication/authorization for the application API
* AI/LLM processing

These would add complexity without being required for the project's core objective.

---

## 20. Final Architecture

The resulting architecture can be summarized as:

```text
                         GitHub
                           │
                           ▼
                    GitHub Actions
                    ┌──────┴──────┐
                    │             │
                  Tests       Docker Build
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                      Git Repository
                           │
                           ▼
                        Argo CD
                           │
                           ▼
                 ┌─────────────────────┐
                 │ Minikube / Kubernetes│
                 │                     │
                 │   Helm-managed      │
                 │   Thumbnail API     │
                 │         │           │
                 │         ▼           │
                 │       MinIO         │
                 │         │           │
                 │        PVC           │
                 │                     │
                 │   Knative Serving   │
                 └─────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Prometheus       OpenTelemetry      Logs
          │                │
          ▼                ▼
       Grafana           Jaeger
```

The architecture keeps the application intentionally small while providing a complete local platform for containerization, Kubernetes deployment, CI, GitOps, observability, security, and failure/recovery engineering.
