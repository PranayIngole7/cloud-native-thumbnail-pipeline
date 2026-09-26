# Argo CD & GitOps

## Overview

The project uses **Argo CD** to implement GitOps-based deployment for the Cloud-Native Thumbnail Pipeline.

Git acts as the declarative source of truth, while Argo CD continuously compares the desired state with the live Kubernetes state and reconciles differences.

```text
GitHub
   |
   v
Argo CD
   |
   | Helm
   v
Kubernetes / Minikube
   |
   +-- Thumbnail Service
   +-- MinIO
   +-- ConfigMap
   +-- PVC
   +-- Services
```

## Implementation

The Argo CD Application is defined in:

```text
argocd/application.yaml
```

It deploys the Helm chart from:

```text
helm/thumbnail-pipeline/
```

Configuration:

```text
Repository: main branch
Chart:      helm/thumbnail-pipeline
Namespace:  thumbnail-pipeline
```

The workflow is:

```text
Git commit
    ↓
GitHub
    ↓
Argo CD
    ↓
Helm rendering
    ↓
Kubernetes reconciliation
```

## GitOps Features Verified

### Synchronization

Argo CD successfully synchronized the Helm-based application to Minikube.

### Drift Detection

A Kubernetes ConfigMap was intentionally modified outside Git.

Argo CD detected the difference and reported the application as `OutOfSync`.

### Self-Healing

Automated self-healing was enabled and tested.

After intentional Kubernetes drift, Argo CD automatically restored the resource to the desired Git-defined state.

```text
Live state differs
       ↓
Argo CD detects drift
       ↓
Automatic reconciliation
       ↓
Desired state restored
```

### Secret Handling

Secrets are excluded from the normal GitOps render.

The Helm chart supports optional Secret creation for local testing, while credentials are kept outside the committed Git configuration.

## Verification

Phase 8 was verified through:

* Argo CD installation and readiness
* Application synchronization
* Helm + Argo CD integration
* Drift detection
* Automated self-healing
* Kubernetes workload health
* Clean Git working tree

Final state:

```text
Application: Synced
Health:      Healthy
Self-healing: Enabled
```

