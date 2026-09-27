# Troubleshooting Guide

This guide provides a practical troubleshooting workflow for the
Cloud-Native Thumbnail Pipeline running on Kubernetes/Minikube.

The recommended approach is to identify the affected resource, inspect
Kubernetes events and logs, verify dependencies and configuration, fix
the root cause, and then confirm recovery.

## General Troubleshooting Workflow

Use the following sequence when a component is not behaving as
expected:

```text
1. Check workload status
2. Inspect the affected resource
3. Review Kubernetes Events
4. Check application/container logs
5. Verify Secrets and ConfigMaps
6. Check probes and resources
7. Check Services and NetworkPolicy
8. Check PVC/storage when applicable
9. Check Argo CD desired/live state
10. Restore the root cause
11. Verify health, readiness, and synchronization
```

Start with:

```bash
kubectl get pods -n thumbnail-pipeline
kubectl get svc -n thumbnail-pipeline
kubectl get pvc -n thumbnail-pipeline
kubectl get events -n thumbnail-pipeline --sort-by=.lastTimestamp
```

## Pod Not Running

Check the Pod state:

```bash
kubectl get pods -n thumbnail-pipeline
```

Inspect the affected Pod:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Check logs:

```bash
kubectl logs <pod-name> -n thumbnail-pipeline
```

For a previous container instance:

```bash
kubectl logs <pod-name> -n thumbnail-pipeline --previous
```

Pay particular attention to:

* `Pending`
* `CrashLoopBackOff`
* `ImagePullBackOff`
* `ErrImagePull`
* `CreateContainerConfigError`
* failed probes
* scheduling failures

## CreateContainerConfigError

This commonly indicates that a referenced configuration object is
missing or invalid.

Check the Pod description:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Check Secrets:

```bash
kubectl get secrets -n thumbnail-pipeline
```

Check ConfigMaps:

```bash
kubectl get configmaps -n thumbnail-pipeline
```

For example, during failure testing the MinIO Pod entered
`CreateContainerConfigError` because its required `minio-secret` was
absent.

Restoring the required Secret allowed the workload to start again:

```bash
kubectl apply -f k8s/minio/secret.yaml
```

Then verify:

```bash
kubectl get pods -n thumbnail-pipeline
```

## ImagePullBackOff / ErrImagePull

Inspect the Pod events:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Check the configured image:

```bash
kubectl get deployment thumbnail-service \
  -n thumbnail-pipeline \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

For local Minikube images, verify that the image is available inside
the Minikube environment.

For example:

```bash
minikube image ls | grep thumbnail-service
```

If the required local image is missing:

```bash
minikube image load thumbnail-service:<tag>
```

Then verify the Deployment and Pod again.

## Readiness or Liveness Probe Failure

Check Pod events:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Look for messages such as:

```text
Readiness probe failed
Liveness probe failed
```

The application exposes:

```text
/health
/ready
```

Test the application directly when port-forwarding is available:

```bash
kubectl port-forward -n thumbnail-pipeline \
  svc/thumbnail-service 8000:8000
```

Then:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses are:

```json
{"status":"ok"}
```

and:

```json
{"status":"ready"}
```

### Readiness vs Liveness

**Readiness failure** means Kubernetes should not send traffic to the
Pod.

**Liveness failure** can cause Kubernetes to restart the container.

During Phase 11 failure testing, an invalid readiness endpoint produced
an HTTP 404 readiness failure.

An invalid liveness endpoint was also tested during a Deployment
rollout, but a clean liveness-triggered restart was not observed.
Therefore, the project does not claim that this specific experiment
demonstrated a liveness-triggered restart.

## Service or Connectivity Problems

Check the Service:

```bash
kubectl get svc -n thumbnail-pipeline
```

Inspect it:

```bash
kubectl describe svc thumbnail-service -n thumbnail-pipeline
```

Check endpoints:

```bash
kubectl get endpoints -n thumbnail-pipeline
```

Verify that the expected Pods are selected by the Service.

For MinIO:

```bash
kubectl get svc minio -n thumbnail-pipeline
```

The application uses the Kubernetes service name:

```text
minio:9000
```

If connectivity fails, also check NetworkPolicy configuration:

```bash
kubectl get networkpolicy -n thumbnail-pipeline
kubectl describe networkpolicy -n thumbnail-pipeline
```

The application is expected to communicate with:

```text
MinIO  -> TCP 9000
Jaeger -> TCP 4317
DNS    -> TCP/UDP 53
```

## MinIO and Persistent Storage Problems

Check MinIO:

```bash
kubectl get pods -n thumbnail-pipeline
kubectl get svc minio -n thumbnail-pipeline
```

Check the PVC:

```bash
kubectl get pvc -n thumbnail-pipeline
kubectl describe pvc minio-data -n thumbnail-pipeline
```

Expected state:

```text
STATUS: Bound
```

The MinIO workload uses:

```text
PVC: minio-data
Mount: /data
Size: 2Gi
Access mode: ReadWriteOnce
```

During failure testing, the MinIO Pod was deleted and replaced. The
replacement Pod mounted the same PVC and the existing MinIO data
directory structure was visible.

This verifies PVC attachment and retained storage structure, but does
not constitute an independent proof that every individual stored object
survived the test.

## NetworkPolicy Troubleshooting

Check policies:

```bash
kubectl get networkpolicy -n thumbnail-pipeline
```

Inspect the application policy:

```bash
kubectl describe networkpolicy -n thumbnail-pipeline
```

If connectivity unexpectedly fails, verify:

* destination Pod labels
* destination ports
* namespace selectors
* DNS access
* MinIO service availability
* Jaeger availability

During Phase 10, an incorrect NetworkPolicy destination selector was
identified and corrected.

During Phase 11, deleting the application NetworkPolicy was used as a
GitOps drift test. Argo CD reconciled the policy back to the desired
state.

## Argo CD OutOfSync

Check the Argo CD Application:

```bash
kubectl get applications -n argocd
```

Inspect it:

```bash
kubectl describe application thumbnail-pipeline -n argocd
```

Check the current workload:

```bash
kubectl get pods -n thumbnail-pipeline
```

If Argo CD reports `OutOfSync`, compare the live Kubernetes state with
the Git-managed desired state.

For Helm-managed resources, validate the chart:

```bash
helm lint ./helm/thumbnail-pipeline
helm template thumbnail-pipeline \
  ./helm/thumbnail-pipeline \
  -n thumbnail-pipeline
```

Do not manually change GitOps-managed resources as a permanent fix.
Correct the declarative configuration in Git when appropriate and let
Argo CD reconcile it.

## Scheduling Problems

Check node status:

```bash
kubectl get nodes
```

Inspect the node:

```bash
kubectl describe node <node-name>
```

Check Pods:

```bash
kubectl get pods -n thumbnail-pipeline
```

A Pod stuck in `Pending` should be investigated through its events:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Look for:

```text
FailedScheduling
```

During Phase 11, the single Minikube node was deliberately cordoned.
After deleting the application Pod, the replacement Pod remained
`Pending` because the only node was unschedulable.

After uncordoning the node:

```bash
kubectl uncordon <node-name>
```

the replacement Pod was scheduled successfully.

This was a single-node scheduling experiment; multi-node rescheduling
was not tested.

## Resource Problems

Inspect configured resources:

```bash
kubectl get deployment thumbnail-service \
  -n thumbnail-pipeline \
  -o yaml
```

The application currently uses:

```text
CPU:
  request: 100m
  limit:   500m

Memory:
  request: 128Mi
  limit:   256Mi
```

Check Pod events for resource-related failures:

```bash
kubectl describe pod <pod-name> -n thumbnail-pipeline
```

Check the container termination state when applicable:

```bash
kubectl get pod <pod-name> \
  -n thumbnail-pipeline \
  -o jsonpath='{.status.containerStatuses[*].lastState}'
```

A controlled memory-pressure test was attempted during Phase 11, but
the disposable test Pod completed successfully and `OOMKilled` was not
reproduced.

## Observability Troubleshooting

### Application Metrics

Check the metrics endpoint:

```bash
kubectl port-forward -n thumbnail-pipeline \
  svc/thumbnail-service 8000:8000
```

Then:

```bash
curl http://localhost:8000/metrics/
```

### Application Logs

```bash
kubectl logs \
  -n thumbnail-pipeline \
  deployment/thumbnail-service
```

Follow logs:

```bash
kubectl logs \
  -n thumbnail-pipeline \
  deployment/thumbnail-service \
  -f
```

### Prometheus

Check the Prometheus workload:

```bash
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

Port-forward:

```bash
kubectl port-forward \
  -n monitoring \
  svc/prometheus-server 9090:80
```

Verify that the thumbnail-service target is available in Prometheus.

### Grafana

Check Grafana:

```bash
kubectl get pods -n monitoring
```

Port-forward:

```bash
kubectl port-forward \
  -n monitoring \
  svc/grafana 3000:80
```

Verify that Prometheus is configured as the data source and that
application metrics are being collected.

### Jaeger

Check Jaeger:

```bash
kubectl get pods -n thumbnail-pipeline
kubectl get svc jaeger -n thumbnail-pipeline
```

Port-forward the UI:

```bash
kubectl port-forward \
  -n thumbnail-pipeline \
  svc/jaeger 16686:16686
```

If traces are missing, verify:

* Jaeger Pod is running
* application tracing is enabled
* OTLP endpoint is configured correctly
* NetworkPolicy allows TCP `4317`
* application logs contain no exporter errors

## Helm Troubleshooting

Validate the chart:

```bash
helm lint ./helm/thumbnail-pipeline
```

Render the chart:

```bash
helm template thumbnail-pipeline \
  ./helm/thumbnail-pipeline \
  -n thumbnail-pipeline
```

Check the release:

```bash
helm list -n thumbnail-pipeline
```

Check release history:

```bash
helm history thumbnail-pipeline \
  -n thumbnail-pipeline
```

For Helm-managed configuration problems, compare the rendered
configuration with the expected Kubernetes resources before applying
changes.

## Final Recovery Verification

After fixing a problem, verify the complete workload rather than
checking only the component that failed.

```bash
kubectl get pods -n thumbnail-pipeline
kubectl get svc -n thumbnail-pipeline
kubectl get pvc -n thumbnail-pipeline
kubectl get nodes
kubectl get applications -n argocd
```

Verify application health:

```bash
kubectl port-forward \
  -n thumbnail-pipeline \
  svc/thumbnail-service 8000:8000
```

Then:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected:

```json
{"status":"ok"}
```

```json
{"status":"ready"}
```

For the final GitOps state, the Argo CD Application should report:

```text
Synced
Healthy
```

## Quick Reference

| Problem                    | First checks                             |
| -------------------------- | ---------------------------------------- |
| Pod not running            | `get pods`, `describe pod`, Events       |
| CrashLoopBackOff           | logs, `--previous`, container state      |
| CreateContainerConfigError | Secrets, ConfigMaps, `describe pod`      |
| ImagePullBackOff           | image/tag, Events, Minikube image        |
| Readiness failure          | probe configuration, `/ready`, Events    |
| Liveness failure           | probe configuration, container restarts  |
| Service failure            | Service, endpoints, Pods, NetworkPolicy  |
| MinIO failure              | Pod, Secret, Service, PVC                |
| PVC problem                | PVC status, `describe pvc`, Pod mount    |
| Network failure            | Service, DNS, NetworkPolicy              |
| Argo CD OutOfSync          | Application, desired/live state, Git     |
| Pod Pending                | node status, taints, Events              |
| Resource issue             | requests/limits, Events, container state |
| Missing metrics            | `/metrics/`, Prometheus target, logs     |
| Missing traces             | Jaeger, OTLP endpoint, NetworkPolicy     |

## Scope

This guide reflects troubleshooting procedures used during the local
Minikube implementation and Phase 11 failure-engineering exercises.

The environment is a single-node development/demo cluster and does not
represent a production multi-node troubleshooting or incident-response
runbook.
