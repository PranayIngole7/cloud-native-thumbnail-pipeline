# Observability

The Cloud-Native Thumbnail Pipeline includes application observability
through metrics, logs, and distributed tracing.

The implementation makes application health, request activity, and
request execution flow visible during local Kubernetes operation.

## Observability Stack

| Component        | Purpose                                                         |
| ---------------- | --------------------------------------------------------------- |
| Prometheus       | Collects and queries application metrics                        |
| Grafana          | Visualizes application metrics through dashboards               |
| OpenTelemetry    | Instruments the FastAPI application and exports traces          |
| Jaeger           | Stores and visualizes distributed traces                        |
| Application logs | Provide request and runtime information through Kubernetes logs |

## Metrics

The FastAPI application exposes Prometheus-compatible metrics through:

```text id="f0c7sj"
/metrics/
```

Application metrics include the custom request counter:

```text id="9x4vkp"
thumbnail_requests_total
```

Prometheus is configured to scrape the application through the
Kubernetes Service:

```text id="5j7q3m"
thumbnail-service.thumbnail-pipeline.svc.cluster.local:8000
```

The Prometheus deployment is intentionally lightweight for the local
Minikube environment.

Optional Prometheus components such as Alertmanager, Pushgateway,
node exporter, and kube-state-metrics are not enabled as part of this
project's monitoring configuration.

## Grafana

Grafana is deployed in the `monitoring` namespace and uses Prometheus
as its data source.

The project dashboard provides visibility into:

* total thumbnail requests
* thumbnail request rate
* thumbnail service availability
* recent requests

Grafana and Prometheus communicate through Kubernetes Service DNS.

## Logging

Application logs are available through Kubernetes:

```bash id="7d3j9v"
kubectl logs -n thumbnail-pipeline deployment/thumbnail-service
```

The application logs request and runtime activity, including thumbnail
processing and HTTP responses.

Kubernetes health and readiness probes also generate observable
application requests:

```text id="r8f5wn"
/health
/ready
```

These requests can therefore appear in the application logs during
normal operation and verification.

## Distributed Tracing

The FastAPI application uses OpenTelemetry instrumentation and exports
traces to Jaeger using OTLP.

The application exports telemetry to:

```text id="x2m6qa"
http://jaeger:4317
```

Jaeger's local UI is exposed through port `16686`.

FastAPI HTTP requests are automatically instrumented, and the
application also includes custom spans for important thumbnail
processing stages:

```text id="p3k8zt"
image.validation
minio.put_original
minio.get_original
thumbnail.generation
minio.put_thumbnail
```

A real end-to-end `POST /thumbnails` request was verified in Jaeger
with an HTTP `200 OK` response and an 11-span trace.

This demonstrated tracing across the actual thumbnail-processing
workflow rather than only verifying that the tracing components were
running.

## Verification

The observability stack was verified by:

1. Confirming that `/metrics/` exposes Prometheus-compatible metrics.
2. Confirming that the `thumbnail-service` Prometheus target is `UP`.
3. Verifying that `thumbnail_requests_total` is collected.
4. Verifying that the Grafana dashboard displays application metrics.
5. Inspecting Kubernetes application logs for health, readiness,
   metrics, and thumbnail requests.
6. Sending a real image to `POST /thumbnails`.
7. Confirming the resulting HTTP request and custom processing spans in
   Jaeger.

## Local Access

For local Minikube verification, Kubernetes port forwarding can be used:

```bash id="u7k2pv"
kubectl port-forward -n thumbnail-pipeline svc/thumbnail-service 8000:8000

kubectl port-forward -n thumbnail-pipeline svc/jaeger 16686:16686

kubectl port-forward -n monitoring svc/prometheus-server 9090:80

kubectl port-forward -n monitoring svc/grafana 3000:80
```

Typical local interfaces are:

```text id="w1r4kc"
Thumbnail Service: http://localhost:8000
Prometheus:        http://localhost:9090
Grafana:           http://localhost:3000
Jaeger:            http://localhost:16686
```

## Resource-Constrained Design

The observability stack is configured for the project's local Minikube
environment and resource-constrained development machine.

Prometheus and Grafana use modest resource allocations, and persistence
is disabled for these local monitoring deployments.

The configuration is intended for development, learning, verification,
and demonstration rather than production high-availability monitoring.
