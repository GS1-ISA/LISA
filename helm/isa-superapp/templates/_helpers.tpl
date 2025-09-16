{{/*
Expand the name of the chart.
*/}}
{{- define "isa-superapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "isa-superapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "isa-superapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "isa-superapp.labels" -}}
helm.sh/chart: {{ include "isa-superapp.chart" . }}
{{ include "isa-superapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "isa-superapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "isa-superapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "isa-superapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "isa-superapp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
PostgreSQL fullname
*/}}
{{- define "isa-superapp.postgresql.fullname" -}}
{{- printf "%s-postgresql" (include "isa-superapp.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Redis fullname
*/}}
{{- define "isa-superapp.redis.fullname" -}}
{{- printf "%s-redis" (include "isa-superapp.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Neo4j fullname
*/}}
{{- define "isa-superapp.neo4j.fullname" -}}
{{- printf "%s-neo4j" (include "isa-superapp.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Prometheus fullname
*/}}
{{- define "isa-superapp.prometheus.fullname" -}}
{{- printf "%s-prometheus" (include "isa-superapp.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Grafana fullname
*/}}
{{- define "isa-superapp.grafana.fullname" -}}
{{- printf "%s-grafana" (include "isa-superapp.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}