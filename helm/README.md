# ISA_D Helm Charts

This directory contains Helm charts for deploying the ISA_D platform on Kubernetes.

## 📁 Structure Overview

```
helm/
└── isa-superapp/           # Main application chart
    ├── Chart.yaml         # Chart metadata
    ├── values.yaml       # Default configuration values
    ├── templates/        # Kubernetes manifests
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingress.yaml
    │   ├── hpa.yaml
    │   └── _helpers.tpl
    └── charts/           # Sub-charts (if any)
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (v1.19+)
- Helm 3.x
- kubectl configured for your cluster

### Installation

1. **Add repository** (if using a Helm repo):
   ```bash
   helm repo add isa https://charts.isa-d.com
   helm repo update
   ```

2. **Install the chart**:
   ```bash
   # Install with default values
   helm install isa-superapp ./helm/isa-superapp

   # Install with custom values
   helm install isa-superapp ./helm/isa-superapp -f my-values.yaml

   # Install in specific namespace
   helm install isa-superapp ./helm/isa-superapp -n isa-system
   ```

3. **Verify installation**:
   ```bash
   kubectl get pods -n isa-system
   kubectl get services -n isa-system
   ```

## ⚙️ Configuration

### Default Values

The `values.yaml` file contains all configurable parameters:

```yaml
# values.yaml
# Application configuration
image:
  repository: isa/superapp
  tag: "latest"
  pullPolicy: IfNotPresent

# Service configuration
service:
  type: ClusterIP
  port: 80
  targetPort: 8001

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: isa.example.com
      paths:
        - path: /
          pathType: Prefix

# Resource limits
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

# Environment variables
env:
  - name: DEBUG
    value: "false"
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: isa-secrets
        key: database-url

# Secrets
secrets:
  enabled: true
  name: isa-secrets
  data:
    openrouter-api-key: ""
    openai-api-key: ""
    anthropic-api-key: ""
```

### Customizing Values

Create a custom values file:

```yaml
# my-values.yaml
image:
  tag: "v1.2.3"

ingress:
  hosts:
    - host: isa.mycompany.com

env:
  - name: LOG_LEVEL
    value: "DEBUG"

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
```

Apply with:
```bash
helm upgrade isa-superapp ./helm/isa-superapp -f my-values.yaml
```

## 📋 Chart Components

### Main Components

| Component | Purpose | Template |
|-----------|---------|----------|
| Deployment | Application pods | `templates/deployment.yaml` |
| Service | Internal networking | `templates/service.yaml` |
| Ingress | External access | `templates/ingress.yaml` |
| HPA | Auto-scaling | `templates/hpa.yaml` |
| ConfigMap | Configuration data | `templates/configmap.yaml` |
| Secret | Sensitive data | `templates/secret.yaml` |

### Templates

#### Deployment Template

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "isa-superapp.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "isa-superapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "isa-superapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: isa-superapp
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          env:
            {{- toYaml .Values.env | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

#### Service Template

```yaml
# templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "isa-superapp.fullname" . }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "isa-superapp.selectorLabels" . | nindent 4 }}
```

## 🔧 Operations

### Upgrading

```bash
# Upgrade to new version
helm upgrade isa-superapp ./helm/isa-superapp

# Upgrade with new values
helm upgrade isa-superapp ./helm/isa-superapp -f new-values.yaml

# Rollback if needed
helm rollback isa-superapp 1
```

### Monitoring

```bash
# Check release status
helm status isa-superapp

# List releases
helm list -n isa-system

# Get release values
helm get values isa-superapp

# Get release manifest
helm get manifest isa-superapp
```

### Troubleshooting

```bash
# Check pod status
kubectl get pods -n isa-system

# Check pod logs
kubectl logs -n isa-system deployment/isa-superapp

# Describe deployment
kubectl describe deployment isa-superapp -n isa-system

# Check events
kubectl get events -n isa-system --sort-by=.metadata.creationTimestamp
```

## 🔒 Security

### Secrets Management

Use Kubernetes secrets for sensitive data:

```yaml
# Create secret
kubectl create secret generic isa-secrets \
  --from-literal=openrouter-api-key="your-key" \
  --from-literal=database-url="postgresql://..."

# Reference in values
env:
  - name: OPENROUTER_API_KEY
    valueFrom:
      secretKeyRef:
        name: isa-secrets
        key: openrouter-api-key
```

### Network Policies

Enable network policies for security:

```yaml
# values.yaml
networkPolicy:
  enabled: true
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
```

### RBAC

Configure RBAC for service accounts:

```yaml
# values.yaml
serviceAccount:
  create: true
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/isa-role

rbac:
  create: true
  rules:
    - apiGroups: [""]
      resources: ["pods", "services"]
      verbs: ["get", "list", "watch"]
```

## 📊 Scaling

### Horizontal Pod Autoscaler

Configure HPA for automatic scaling:

```yaml
# values.yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment isa-superapp --replicas=5 -n isa-system

# Update via Helm
helm upgrade isa-superapp ./helm/isa-superapp --set replicaCount=5
```

## 🔄 CI/CD Integration

### GitHub Actions

Example workflow for automated deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v2
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}

      - name: Deploy with Helm
        run: |
          helm upgrade --install isa-superapp ./helm/isa-superapp \
            --namespace isa-system \
            --create-namespace \
            --set image.tag=${{ github.sha }}
```

### ArgoCD

For GitOps deployments:

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: isa-superapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/isa-d
    path: helm/isa-superapp
    targetRevision: HEAD
  destination:
    server: https://kubernetes.default.svc
    namespace: isa-system
```

## 🧪 Testing

### Helm Testing

```bash
# Lint chart
helm lint ./helm/isa-superapp

# Template dry-run
helm template isa-superapp ./helm/isa-superapp

# Install dry-run
helm install isa-superapp ./helm/isa-superapp --dry-run
```

### Integration Testing

```bash
# Test with test framework
helm test isa-superapp
```

## 📚 Related Documentation

- [Kubernetes Deployment Guide](../k8s/README.md)
- [Infrastructure Setup](../infra/README.md)
- [CI/CD Architecture](../docs/CI_CD_ARCHITECTURE.md)
- [Project Structure](../docs/project-structure.md)

## 🤝 Contributing

### Chart Development

1. Update `Chart.yaml` version
2. Modify templates as needed
3. Update `values.yaml` with new parameters
4. Test changes locally
5. Submit pull request

### Best Practices

- Use Helm best practices
- Include comprehensive documentation
- Test thoroughly before deployment
- Follow security guidelines
- Maintain backward compatibility

This Helm chart provides a production-ready deployment solution for the ISA_D platform on Kubernetes.