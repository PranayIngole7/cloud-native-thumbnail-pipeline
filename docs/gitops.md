# Argo CD & GitOps

## Overview

The project uses Argo CD to implement GitOps-based deployment for the
Cloud-Native Thumbnail Pipeline.

The Git repository contains the declarative deployment configuration.
Argo CD compares the desired state defined in Git with the live
Kubernetes state and reconciles differences.

```text id="7q5c8m"
Git Repository
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

```text id="5x8z2a"
argocd/application.yaml
```

The Application points Argo CD to the Helm chart:

```text id="4w3m6s"
helm/thumbnail-pipeline/
```

The configured deployment target is:

```text id="0j4y1k"
Repository: main branch
Chart:     helm/thumbnail-pipeline
Namespace: thumbnail-pipeline
```

The GitOps workflow is:

```text id="v5m7dr"
Git Commit
    |
    v
Git Repository
    |
    v
Argo CD
    |
    v
Helm Rendering
    |
    v
Kubernetes Resources
    |
    v
Live Cluster State
```

Argo CD is responsible for synchronization and reconciliation, while
Helm provides the Kubernetes packaging and configuration model.

## Synchronization

Argo CD successfully synchronized the Helm-based application to the
Minikube Kubernetes cluster.

The Argo CD Application reported the expected synchronized and healthy
state after deployment.

## Drift Detection

GitOps drift detection was deliberately tested by modifying a
Kubernetes ConfigMap outside the Git-managed configuration.

Argo CD detected the difference between the desired Git state and the
live Kubernetes state and reported the Application as `OutOfSync`.

Conceptually:

```text id="d4z8qa"
Desired State
     |
     | Git
     v
   Argo CD
     |
     | comparison
     v
Live Kubernetes State
     |
     +-- Difference detected
             |
             v
         OutOfSync
```

## Self-Healing

Automated self-healing was enabled and tested.

After intentional Kubernetes drift, Argo CD automatically reconciled the
affected resource back to the desired Git-defined state.

```text id="e9x3pt"
Live State Differs
       |
       v
Argo CD Detects Drift
       |
       v
Automatic Reconciliation
       |
       v
Desired State Restored
```

This demonstrates the core GitOps reconciliation model used by the
project.

## Secret Handling

Sensitive credentials are not stored as plaintext Git configuration.

The Helm chart supports optional Secret creation for local deployment,
while the GitOps configuration can leave Secret creation disabled and
allow credentials to be supplied separately.

This keeps sensitive runtime values separate from the declarative
application configuration stored in Git.

## Failure Recovery and Drift

GitOps reconciliation was also exercised during the project's failure
engineering work.

A Kubernetes NetworkPolicy was intentionally deleted from the live
cluster. Argo CD reconciled the resource back into the cluster, restoring
the Git-defined desired state.

This demonstrated that GitOps reconciliation can recover configuration
drift even when the resource is removed outside the Git workflow.

## Verification

The GitOps implementation was verified through:

* Argo CD installation and readiness
* Argo CD Application configuration
* Helm and Argo CD integration
* Application synchronization
* drift detection
* automated self-healing
* Kubernetes workload health
* configuration reconciliation after intentional resource deletion

The verified final Application state was:

```text id="2y7n4w"
Application: Synced
Health:      Healthy
Self-healing: Enabled
```

## Scope

The GitOps implementation uses Argo CD locally with Minikube.

It demonstrates declarative Kubernetes deployment, Helm integration,
drift detection, synchronization, and automated reconciliation.

It does not claim a production-grade multi-cluster GitOps platform,
external secret-management system, or highly available Argo CD
deployment.
