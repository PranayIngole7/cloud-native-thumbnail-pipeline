# Observability

The Cloud-Native Thumbnail Pipeline includes application and infrastructure observability using metrics, logs, and distributed tracing.

The implementation is designed to make application health, request activity, and request execution flow visible during local Kubernetes operation.

## Observability Stack

| Component        | Purpose                                                         |
| ---------------- | --------------------------------------------------------------- |
| Prometheus       | Collects and queries application and Kubernetes metrics         |
| Grafana          | Visualizes application metrics through dashboards               |
| OpenTelemetry    | Instruments the FastAPI application and exports traces          |
| Jaeger           | Stores and visualizes distributed traces                        |
| Application logs | Provide request and runtime information through Kubernetes logs |

## Metrics

The FastAPI application exposes Prometheus-compatible metrics through:

```text
/metrics/
```

Application metrics include a custom request counter:

```text
thumbnail_requests_total
```

Prometheus is configured to scrape the application through the Kubernetes Service:

```text
thumbnail-service.thumbnail-pipeline.svc.cluster.local:8000
```

The Prometheus deployment is intentionally lightweight for the local Minikube environment. Optional components such as Alertmanager, Pushgateway, node exporter, and kube-state-metrics are disabled in this project.

## Grafana

Grafana is deployed in the `monitoring` namespace and uses Prometheus as its data source.

The project dashboard currently provides:

* Total thumbnail requests
* Thumbnail request rate
* Thumbnail service availability
* Requests during the last five minutes

Grafana and Prometheus use Kubernetes service DNS for communication inside the cluster.

## Logging

Application logs are available through Kubernetes:

```bash
kubectl logs -n thumbnail-pipeline deployment/thumbnail-service
```

The application logs important request activity, including thumbnail requests, upload processing, and HTTP responses.

Kubernetes health and readiness probes also generate observable application traffic for:

```text
/health
/ready
```

## Distributed Tracing

The FastAPI application uses OpenTelemetry instrumentation and exports traces to Jaeger using OTLP.

The application exports telemetry to:

```text
http://jaeger:4317
```

Jaeger provides the trace UI through port `16686`.

The application includes custom spans for important stages of the thumbnail pipeline:

```text
image.validation
minio.put_original
minio.get_original
thumbnail.generation
minio.put_thumbnail
```

FastAPI HTTP requests are also automatically instrumented.

A real end-to-end `POST /thumbnails` request was verified in Jaeger with an HTTP `200 OK` response and an 11-span trace, demonstrating that tracing works across the actual thumbnail-processing workflow.

## Verification

The observability stack has been verified by:

1. Confirming the application `/metrics/` endpoint exposes Prometheus metrics.
2. Confirming the Prometheus `thumbnail-service` target is `UP`.
3. Verifying `thumbnail_requests_total` is collected by Prometheus.
4. Verifying the Grafana application dashboard displays live metrics.
5. Verifying Kubernetes application logs for health, readiness, metrics, and thumbnail requests.
6. Sending a real image to `POST /thumbnails`.
7. Confirming the resulting request and custom processing spans in Jaeger.

## Local Access

For local Minikube verification, the services can be accessed with Kubernetes port forwarding:

```bash
kubectl port-forward -n thumbnail-pipeline svc/thumbnail-service 8000:8000
kubectl port-forward -n thumbnail-pipeline svc/jaeger 16686:16686
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
kubectl port-forward -n monitoring svc/grafana 3000:80
```

Typical local interfaces:

```text
Thumbnail Service: http://localhost:8000
Prometheus:        http://localhost:9090
Grafana:           http://localhost:3000
Jaeger:            http://localhost:16686
```

## Resource-Constrained Design

The monitoring stack is configured for the project's local Minikube environment on a resource-constrained development machine.

Prometheus and Grafana use modest CPU and memory limits, and persistence is disabled for these local deployments.

This configuration is intended for development, learning, verification, and demonstration rather than production high-availability monitoring.
