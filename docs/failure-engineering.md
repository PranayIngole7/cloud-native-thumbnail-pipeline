# Failure Engineering & Recovery

Phase 11 validates how the Cloud-Native Thumbnail Pipeline behaves under controlled failures and how Kubernetes, GitOps, persistent storage, and observability support recovery.

## Failure Scenarios

| Scenario                    | Observed behavior                                                                                                                           | Recovery / verification                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Application process failure | Terminating PID 1 caused the application container to restart and the restart count increased.                                              | Container recovered automatically; `/health` and `/ready` returned successfully.          |
| Pod deletion                | Deployment recreated the application Pod with a new Pod identity.                                                                           | Replacement Pod reached `1/1 Running`.                                                    |
| MinIO Pod failure           | Replacement MinIO Pod entered `CreateContainerConfigError` when its required Secret was absent.                                             | Restoring `minio-secret` allowed MinIO to start with the existing PVC.                    |
| NetworkPolicy drift         | Manually deleting the application egress policy created live-state drift. Argo CD reconciled the policy back to the desired state.          | Policy was restored and Argo CD remained synchronized.                                    |
| Readiness probe failure     | An invalid readiness endpoint produced a Kubernetes `Unhealthy` event with HTTP 404 during the rollout experiment.                          | Helm restored the intended probe configuration.                                           |
| Liveness probe experiment   | An invalid liveness endpoint was introduced during a Deployment rollout, but a clean liveness-triggered container restart was not observed. | Helm restored the intended configuration and the application returned healthy.            |
| Resource-pressure test      | A disposable Pod with a 16Mi memory limit successfully wrote 32 MB and completed; `OOMKilled` was not reproduced.                           | Test Pod was deleted; no application resources were changed.                              |
| Node scheduling failure     | Cordoning the single Minikube node caused a replacement application Pod to remain `Pending`.                                                | Uncordoning the node allowed the scheduler to place the Pod and it reached `1/1 Running`. |

## Persistent Storage

The MinIO PVC remained `Bound` during Pod replacement and the replacement MinIO Pod mounted the same `/data` volume. Existing MinIO data directories were visible after recovery.

## Observability & Troubleshooting

Kubernetes Events provided evidence for readiness failures, scheduling failures, Pod lifecycle transitions, and historical image-pull errors. Application logs continued to show successful health, readiness, and metrics requests after recovery. Jaeger remained available as the tracing backend.

The troubleshooting sequence used during the tests was:

1. Check Pod, Service, PVC, and node status.
2. Inspect the affected Pod with `kubectl describe`.
3. Review namespace Events.
4. Inspect application/container logs.
5. Check Secrets, ConfigMaps, probes, and persistent volumes.
6. Check NetworkPolicy and GitOps desired/live state.
7. Restore the root cause and verify health, readiness, and synchronization.

## Final Recovery State

The final verification confirmed:

* Thumbnail service: `1/1 Running`
* MinIO: `1/1 Running`
* Jaeger: `1/1 Running`
* MinIO PVC: `Bound`, 2 GiB
* Minikube node: `Ready`
* Argo CD: `Synced / Healthy`
* `/health`: `{"status":"ok"}`
* `/ready`: `{"status":"ready"}`

These experiments were performed on a single-node Minikube environment. Multi-node rescheduling was therefore not tested.
