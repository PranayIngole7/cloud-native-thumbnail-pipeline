# Security

The Cloud-Native Thumbnail Pipeline applies container and Kubernetes
security controls based on least-privilege principles.

The security implementation focuses on reducing container privileges,
restricting unnecessary network access, protecting credentials, and
scanning the application image for known vulnerabilities.

## Security Controls

### Container Security

The thumbnail service container is configured to:

* run as a non-root user with UID/GID `1000`
* use Kubernetes `runAsNonRoot`
* use `seccompProfile: RuntimeDefault`
* disable privilege escalation
* drop all Linux capabilities
* disable automatic ServiceAccount token mounting

These controls reduce the privileges available to the application
process inside the Kubernetes workload.

### Kubernetes Security

The `thumbnail-pipeline` namespace uses Pod Security Admission labels
with:

```text
enforce: baseline
audit:   restricted
warn:    restricted
```

The application does not require access to the Kubernetes API.

Consequently, no custom `Role`, `RoleBinding`, `ClusterRole`, or
`ClusterRoleBinding` was introduced for the application.

This is an intentional least-privilege decision rather than an omitted
permission requirement.

### Network Security

A Kubernetes `NetworkPolicy` restricts application egress to the
dependencies required by the application:

| Destination    | Protocol | Port | Purpose                               |
| -------------- | -------- | ---: | ------------------------------------- |
| MinIO          | TCP      | 9000 | Object storage                        |
| Jaeger         | TCP      | 4317 | OTLP trace export                     |
| Kubernetes DNS | UDP/TCP  |   53 | Service discovery and name resolution |

The policy limits application egress to these required destinations.

NetworkPolicy behavior was verified during the security phase.

### Secrets

Application and MinIO credentials are supplied through Kubernetes
Secrets.

Sensitive local Secret manifests are excluded from version control.

The Helm chart supports optional Secret creation so that credentials
can be supplied separately from the Git-managed deployment
configuration.

Production deployments should use an appropriate external secret
management solution and suitable Kubernetes/etcd encryption controls.

These production controls are outside the scope of this local
implementation.

### Image Security

The application image was scanned using Trivy.

At the verified scan point:

* `0` CRITICAL OS vulnerabilities were reported.
* Python-package findings identified in an earlier scan were resolved by
  updating the affected dependency.
* `44` HIGH OS-package findings remained in the Debian-based image.
* The project therefore does **not** claim that the image is
  vulnerability-free.

The remaining OS-package findings were associated with the underlying
base image packages rather than the application's Python dependencies.

Trivy scanning was used as a security assessment step; it is not
currently part of the GitHub Actions CI workflow.

### Resource Controls

The application container defines resource requests and limits:

| Resource | Request |   Limit |
| -------- | ------: | ------: |
| CPU      |  `100m` |  `500m` |
| Memory   | `128Mi` | `256Mi` |

These settings provide basic resource boundaries and help Kubernetes
schedule and constrain the application workload.

## Verification

Security controls were verified against the running Kubernetes
workload, including:

* non-root execution
* container security context
* ServiceAccount token absence
* Pod Security namespace labels
* absence of unnecessary application RBAC permissions
* NetworkPolicy configuration and behavior
* resource requests and limits
* Trivy image scanning
* application health and readiness

The application remained operational after the security hardening
changes.

## Known Hardening Consideration

The current MinIO deployment has not been forced to run as a non-root
user.

The existing MinIO image and persistent-volume behavior were not
validated sufficiently to make that change safely within this project.

MinIO non-root hardening therefore remains a future improvement rather
than an unverified security claim.

## Security Scope

These controls demonstrate practical container and Kubernetes security
for a local cloud-native project.

They do not represent a complete production security program.

Production deployments would require additional controls such as
centralized secret management, stronger supply-chain controls, image
signing and verification, vulnerability remediation processes,
Kubernetes/etcd encryption, centralized security monitoring, and
environment-specific security policies.
