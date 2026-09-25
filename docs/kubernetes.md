# Kubernetes Deployment

## Overview

The project runs the thumbnail service and its MinIO object storage backend on Kubernetes.

The Kubernetes deployment uses a dedicated namespace, configuration and secrets, health probes, resource management, persistent storage, and internal ClusterIP services.

## Architecture

```text
Kubernetes Cluster
└── Namespace: thumbnail-pipeline
    │
    ├── thumbnail-service
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

The application connects to MinIO through the Kubernetes service name:

> minio:**9000** 

### Kubernetes Resources

The implementation currently defines:

**Application** 
- Namespace: `thumbnail-pipeline` 
- Deployment: `thumbnail-service` 
- ConfigMap: `thumbnail-service-config` 
- Secret: application MinIO credentials 
- Service: `thumbnail-service` 
- Liveness probe: `/health` 
- Readiness probe: `/ready` 
  
**MinIO** 
- Deployment 
- Secret 
- PersistentVolumeClaim 
- Service 
- Initialization Job 
 
### Configuration

Non-sensitive configuration is stored in the application ConfigMap:

```text
MINIO_ENDPOINT=minio:**9000** 
MINIO_BUCKET=thumbnail-pipeline 
MINIO_SECURE=false
```

Sensitive MinIO credentials are provided through Kubernetes Secrets and are not stored as plaintext repository configuration.

### Health Probes

The application exposes:
```text
/health 
/ready
```

Kubernetes uses these endpoints for:
- Liveness checks 
- Readiness checks

This allows Kubernetes to distinguish between a running container and an application that is ready to receive traffic.

### Resource Management

The application container defines:

```text
Requests:
    **CPU**:100m
    Memory: 128Mi

Limits:
    **CPU**:    500m
    Memory: 256Mi
```

These values provide basic resource scheduling and protection while remaining suitable for the project's local Minikube environment.

### Persistent Storage

MinIO uses a PersistentVolumeClaim with:

> Storage: 2Gi

The **PVC** keeps **MinIO** object data outside the container filesystem lifecycle.

### Service Discovery

The application communicates with MinIO through Kubernetes internal **DNS**:

> minio:**9000**

The services use the Kubernetes `ClusterIP` type because the application and MinIO communicate internally within the cluster.

### Deployment Verification

The Kubernetes deployment was verified by checking:

- Namespace creation 
- Pod startup 
- Deployment rollout 
- Service availability 
- ConfigMap configuration 
- Secret references 
- Health probes 
- Resource requests and limits 
- MinIO persistent storage 
- Application-to-MinIO connectivity

The application and MinIO workloads were successfully deployed in the `thumbnail-pipeline` namespace.

### Failure and Recovery

The Kubernetes deployment builds on the application's existing health and storage failure handling.

Health probes allow Kubernetes to detect unhealthy application containers.

Persistent storage protects MinIO data from normal container recreation.

Application-level storage failures are handled by the service rather than treating Kubernetes as the source of application business logic.

### Directory Structure

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

The `knative/` manifest is maintained separately from the core Kubernetes Deployment resources because Knative provides a different serving model.

### Current Scope

The Kubernetes implementation currently provides:

- Container orchestration with Kubernetes 
- Minikube-based local deployment 
- Kubernetes service discovery 
- ConfigMap-based configuration 
- Secret-based sensitive configuration 
- Liveness and readiness probes 
- **CPU** and memory requests/limits 
- Persistent MinIO storage 
- MinIO initialization 
- Internal ClusterIP services

Helm and Knative are maintained as separate project phases and documentation topics. 
