# Helm

Helm is used to package the Kubernetes resources for the Cloud-Native
Thumbnail Pipeline into a reusable and configurable chart.

The Helm chart was built from the verified Kubernetes deployment and
provides a structured way to configure and manage the application and
MinIO resources.

## Chart

The primary chart is located at:

```text id="2p9h0d"
helm/thumbnail-pipeline/
```

Its structure includes:

```text id="k5n1vw"
helm/thumbnail-pipeline/
├── Chart.yaml
├── values.yaml
├── .helmignore
└── templates/
```

The templates represent the application and MinIO resources required by
the deployment.

## Configuration

`values.yaml` provides configurable deployment values without requiring
the Kubernetes templates to be edited directly.

The chart provides configuration for:

* application image and tag
* replica count
* service configuration
* resource requests and limits
* application configuration
* tracing configuration
* Secret handling
* MinIO image and configuration
* persistent storage
* MinIO initialization

The chart supports optional Secret creation. For GitOps deployment,
sensitive credentials can be supplied separately rather than stored as
plaintext values in the Git repository.

Local development values can be maintained separately from the default
chart configuration.

## Resources

The chart represents the core Kubernetes resources used by the
application and MinIO deployment:

* application Deployment
* application Service
* application ConfigMap
* application Secret
* MinIO Deployment
* MinIO Service
* MinIO Secret
* MinIO PersistentVolumeClaim
* MinIO initialization Job

The rendered chart preserves important runtime configuration including:

* namespace
* selectors
* container images
* container ports
* liveness and readiness probes
* resource requests and limits
* configuration references
* Secret references
* PVC references

## Validation

The chart was validated using Helm linting and template rendering.

The rendered manifests were compared with the verified Kubernetes
baseline to confirm that the expected resources were represented and
that important runtime configuration remained intact.

Validation included:

```text id="x2kj3d"
helm lint
      ↓
helm template
      ↓
resource and configuration comparison
```

The chart was also exercised through Helm upgrades during the project's
Kubernetes and failure-recovery work.

## Helm Release Management

Helm manages the Kubernetes resources as a release.

For example:

```bash id="2g5w3f"
helm upgrade thumbnail-pipeline ./helm/thumbnail-pipeline \
  -n thumbnail-pipeline
```

Helm release revisions provide a history of configuration changes and
allow deployment state to be managed through Helm.

The project also used Helm upgrades to restore Kubernetes resources after
controlled configuration and failure experiments.

## Why Helm?

Helm provides:

* reusable Kubernetes packaging
* centralized configuration through `values.yaml`
* release and revision management
* repeatable installation and upgrades
* configurable deployment values
* a clean deployment interface for GitOps tooling

Helm does not replace Kubernetes. It packages and renders Kubernetes
resources and manages them as releases.

## Helm and GitOps

Helm acts as the Kubernetes packaging layer, while Argo CD provides the
GitOps reconciliation layer.

The desired deployment configuration is stored in Git. Argo CD renders
the Helm chart and continuously reconciles the resulting Kubernetes
resources with the desired state.

This separation keeps the responsibilities clear:

```text id="eq6w3p"
Git Repository
      |
      v
    Argo CD
      |
      v
 Helm Chart
      |
      v
Kubernetes Resources
```

Helm therefore provides the deployment packaging and configuration
model, while Argo CD manages synchronization and drift reconciliation.
