# Security

The thumbnail pipeline applies Kubernetes and container security controls following least-privilege principles.

## Security Controls

### Container Security

The application container:

* Runs as a non-root user (`UID/GID 1000`)
* Uses Kubernetes `runAsNonRoot`
* Uses `seccompProfile: RuntimeDefault`
* Disables privilege escalation
* Drops all Linux capabilities
* Does not require a Kubernetes service-account token

### Kubernetes Security

The `thumbnail-pipeline` namespace uses Pod Security Admission with:

* `baseline` enforcement
* `restricted` audit
* `restricted` warning

The application does not require Kubernetes API access, so no custom Roles, RoleBindings, ClusterRoles, or ClusterRoleBindings are configured for it.

### Network Security

A Kubernetes `NetworkPolicy` restricts application egress to the required services:

* MinIO on TCP `9000`
* Jaeger on TCP `4317`
* Kubernetes DNS on TCP/UDP `53`

Other tested application egress ports were blocked by the policy.

### Secrets

Application and MinIO credentials are supplied through Kubernetes Secrets.

Helm templates support configurable secret values, while local development secret manifests are kept outside version control.

Production deployments should use an appropriate external secret-management solution and Kubernetes/etcd encryption controls.

### Image Security

The application image is scanned with Trivy.

The current application image has:

* `0` CRITICAL vulnerabilities
* No remaining Python package vulnerabilities identified by the scan
* Remaining HIGH findings are associated with the underlying Debian packages and are tracked separately

The project does not claim that the base image is vulnerability-free.

### Resource Controls

The application container defines resource requests and limits:

| Resource | Request |   Limit |
| -------- | ------: | ------: |
| CPU      |  `100m` |  `500m` |
| Memory   | `128Mi` | `256Mi` |

This provides basic resource isolation and helps prevent uncontrolled resource consumption.

## Verification

Security controls were verified against the running Kubernetes workload, including:

* non-root execution
* security context configuration
* service-account token absence
* Pod Security namespace labels
* RBAC configuration
* NetworkPolicy enforcement
* resource requests and limits
* Trivy image scanning
* application health and readiness endpoints

The application was verified running successfully after the security changes.

## Known Hardening Consideration

The current MinIO deployment has not been forced to run as a non-root user because its existing image and persistent-volume behavior have not been validated for that change.

It remains a future hardening consideration rather than an unverified configuration change.

## Scope

These controls demonstrate practical container and Kubernetes security for this learning project. They are not intended to represent a complete production security program.
