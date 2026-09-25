{{/*
Application name
*/}}
{{- define "thumbnail-pipeline.applicationName" -}}
thumbnail-service
{{- end }}

{{/*
MinIO name
*/}}
{{- define "thumbnail-pipeline.minioName" -}}
minio
{{- end }}

{{/*
Common Helm labels
*/}}
{{- define "thumbnail-pipeline.labels" -}}
helm.sh/chart: {{ include "thumbnail-pipeline.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Chart label
*/}}
{{- define "thumbnail-pipeline.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Application selector labels

Keep this aligned with the known-good Phase 4 Deployment/Service.
*/}}
{{- define "thumbnail-pipeline.applicationSelectorLabels" -}}
app: thumbnail-service
{{- end }}

{{/*
MinIO selector labels

Keep this aligned with the known-good Phase 4 Deployment/Service.
*/}}
{{- define "thumbnail-pipeline.minioSelectorLabels" -}}
app: minio
{{- end }}