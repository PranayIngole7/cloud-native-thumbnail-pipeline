# Kubernetes Deployment

## Overview

The Cloud-Native Thumbnail Pipeline runs the thumbnail service and its
MinIO object-storage backend on Kubernetes.

The deployment uses a dedicated namespace, ConfigMaps, Secrets, health
probes, resource requests and limits, persistent storage, internal
ClusterIP services, and Kubernetes security controls.

The project uses Minikube as its local Kubernetes environment.

## Architecture

```text
Kubernetes Cluster
└── Namespace: thumbnail-pipeline
    │
    ├── Thumbnail Service
    │   ├── Deployment
    │   ├── ConfigMap
    │   ├── Secret
    │   └── ClusterIP Service
    │
    └── MinIO
        ├── Deployment
        ├── Secret
        ├── PersistentVolumeClaim
        ├── ClusterIP Service
        └── Initialization Job
```

The application connects to MinIO through the Kubernetes Service:

```text
minio:9000
```

## Kubernetes Resources

### Application

The application deployment includes:

* Namespace: `thumbnail-pipeline`
* Deployment: `thumbnail-service`
* ConfigMap: `thumbnail-service-config`
* Secret containing MinIO credentials
* ClusterIP Service: `thumbnail-service`
* Liveness probe: `/health`
* Readiness probe: `/ready`
* CPU and memory requests and limits
* Container security context

### MinIO

The MinIO deployment includes:

* Deployment
* Secret
* PersistentVolumeClaim
* ClusterIP Service
* Initialization Job

The MinIO data volume is provided through the `minio-data` PVC.

## Configuration

Non-sensitive application configuration is provided through the
ConfigMap:

```text
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=thumbnail-pipeline
MINIO_SECURE=false
```

Sensitive MinIO credentials are provided through Kubernetes Secrets.

Secret files containing credentials are excluded from the public
repository and are not committed as plaintext configuration.

## Health Probes

The application exposes:

```text
/health
/ready
```

Kubernetes uses these endpoints for different purposes:

* **Liveness probe** — checks whether the application process is
  functioning.
* **Readiness probe** — determines whether the Pod should receive
  traffic.

This separates application process health from traffic readiness.

The configured probes use HTTP requests against port `8000`.

## Resource Management

The application container defines:

```text
Requests:
    CPU:    100m
    Memory: 128Mi

Limits:
    CPU:    500m
    Memory: 256Mi
```

These values provide basic resource requests for scheduling and memory
and CPU limits suitable for the project's local Minikube environment.

## Persistent Storage

MinIO uses a `PersistentVolumeClaim` with:

```text
Storage: 2Gi
Access Mode: ReadWriteOnce
```

The PVC separates MinIO storage from the lifecycle of an individual
MinIO Pod.

During failure testing, the MinIO Pod was replaced while the PVC
remained `Bound` and the replacement Pod mounted the same storage
volume.

## Service Discovery

The application communicates with MinIO through Kubernetes internal DNS:

```text
minio:9000
```

Both application and MinIO Services use the `ClusterIP` type because
their communication is internal to the Kubernetes cluster.

The thumbnail service itself can be exposed locally during development
using Kubernetes port-forwarding.

## Security Controls

The application deployment includes Kubernetes-level security
hardening such as:

* non-root container execution
* dropped Linux capabilities
* disabled privilege escalation
* `RuntimeDefault` seccomp profile
* disabled automatic ServiceAccount token mounting

NetworkPolicy controls restrict application egress to required
dependencies such as MinIO, Jaeger, and cluster DNS.

Namespace Pod Security labels are also configured for additional
policy enforcement, auditing, and warnings.

The application does not require access to the Kubernetes API, so no
custom application RBAC permissions are required.

Detailed security controls and verification are documented separately
in [`docs/security.md`](security.md).

## Deployment Verification

The Kubernetes deployment was verified through:

* namespace creation
* Deployment rollout
* Pod startup
* Service availability
* ConfigMap configuration
* Secret references
* health-probe behavior
* resource requests and limits
* MinIO persistent storage
* application-to-MinIO connectivity
* Kubernetes security configuration

The application and MinIO workloads were successfully deployed in the
`thumbnail-pipeline` namespace.

## Failure and Recovery

Kubernetes failure and recovery behavior was tested during the project's
failure-engineering phase.

Examples included:

* application container termination and automatic container restart
* application Pod deletion and Deployment-based Pod replacement
* MinIO Pod replacement
* missing Secret causing MinIO startup failure
* temporary readiness-probe failure
* single-node scheduling failure after node cordoning
* recovery after restoring the node to schedulable state
* persistent-volume verification after MinIO Pod replacement

Some failure experiments were intentionally limited by the local
single-node Minikube environment. In particular, scheduling recovery
was demonstrated by cordoning and uncordoning the only node rather
than by moving workloads between multiple nodes.

The complete failure-testing evidence is documented in
[`docs/failure-engineering.md`](failure-engineering.md).

## Directory Structure

```text
k8s/
├── application/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── secret.yaml
│   └── service.yaml
│
├── minio/
│   ├── deployment.yaml
│   ├── job.yaml
│   ├── pvc.yaml
│   ├── secret.yaml
│   └── service.yaml
│
└── knative/
    └── thumbnail-service.yaml
```

The `knative/` manifest is maintained separately from the core
Deployment resources because Knative provides an additional serving
model.

## Current Scope

The Kubernetes implementation provides:

* Kubernetes-based container orchestration
* Minikube-based local deployment
* Kubernetes service discovery
* ConfigMap-based configuration
* Secret-based sensitive configuration
* Liveness and readiness probes
* CPU and memory requests and limits
* Persistent MinIO storage
* MinIO initialization
* Internal ClusterIP services
* Container security hardening
* NetworkPolicy controls

Helm provides the reusable deployment packaging layer, while Knative
provides an additional serving and autoscaling capability. These are
documented separately.
