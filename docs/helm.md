# Helm

Helm is used to package the Kubernetes resources for the Cloud-Native
Thumbnail Pipeline into a reusable and configurable chart.

The Helm implementation was built from the known-good Kubernetes
deployment created in Phase 4.

## Chart

The chart is located at:

``` text
helm/thumbnail-pipeline/
```

The chart contains:

``` text
helm/thumbnail-pipeline/
├── Chart.yaml
├── values.yaml
└── templates/
```

The templates represent the application and MinIO resources required by
the Kubernetes deployment.

## Configuration

`values.yaml` provides configurable deployment values instead of
requiring Kubernetes manifests to be edited directly for every
environment.

The chart covers configuration for the application and MinIO deployment,
including:

- image configuration
- application service configuration
- resource requests and limits
- application configuration
- secrets
- MinIO configuration
- persistent storage
- initialization

Sensitive values are not committed as plaintext application secrets.

## Resources

The chart represents the Phase 4 Kubernetes resources, including:

- application Deployment
- application Service
- application ConfigMap
- application Secret
- MinIO Deployment
- MinIO Service
- MinIO Secret
- MinIO PVC
- MinIO initialization Job

The chart preserves the important runtime behavior from the verified
Kubernetes manifests, including:

- namespace
- selectors
- probes
- container images
- ports
- resource requests/limits
- secret references
- PVC references

## Validation

The chart was validated using Helm linting and rendering.

The rendered output was compared with the Phase 4 Kubernetes baseline to
confirm that the expected resources were represented and that their
important configuration remained intact.

The chart was also exercised through the Helm lifecycle:

``` text
lint
  ↓
render
  ↓
install
  ↓
upgrade
  ↓
rollback
```

This verifies that the application can be managed as a Helm release
rather than only as manually maintained YAML files.

## Why Helm?

Helm provides:

- reusable Kubernetes packaging
- centralized configuration through `values.yaml`
- release/version management
- repeatable installation and upgrades
- rollback support
- cleaner environment-specific configuration

Helm does not replace Kubernetes. It generates and manages Kubernetes
resources.

## Relationship to Later Delivery

Helm is the packaging/deployment layer for Kubernetes resources.

The project’s later GitOps workflow can use the Helm chart as the
Kubernetes deployment definition, while Argo CD remains responsible for
reconciling the desired state.
