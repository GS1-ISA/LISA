# ISA_D Infrastructure

This directory contains infrastructure-as-code for provisioning, configuring, and monitoring the ISA_D platform.

## 📁 Structure Overview

```
infra/
├── feature_flags/        # Feature flag infrastructure
├── grafana/             # Monitoring dashboards
├── monitoring/          # Monitoring configuration
├── otel/               # OpenTelemetry setup
├── rag/                # RAG system infrastructure
└── [other infra components]
```

## 🏗️ Infrastructure Components

### Monitoring Stack

| Component | Purpose | Technology |
|-----------|---------|------------|
| Prometheus | Metrics collection | Prometheus |
| Grafana | Visualization | Grafana |
| Alertmanager | Alerting | Alertmanager |
| Loki | Log aggregation | Loki |
| Promtail | Log shipping | Promtail |

### Observability

| Component | Purpose | Technology |
|-----------|---------|------------|
| OpenTelemetry | Tracing | OTEL Collector |
| Jaeger | Distributed tracing | Jaeger |
| Metrics | Performance monitoring | Custom exporters |

### Feature Flags

| Component | Purpose | Technology |
|-----------|---------|------------|
| Flag Management | Dynamic features | LaunchDarkly/Custom |
| Configuration | Runtime config | ConfigMaps/Secrets |
| Rollout | Gradual deployment | Kubernetes |

## 🚀 Quick Start

### Prerequisites

- Terraform 1.0+
- Ansible 2.9+
- AWS CLI (for AWS deployments)
- kubectl (for Kubernetes)

### Infrastructure Setup

1. **Initialize Terraform**:
   ```bash
   cd infra/
   terraform init
   ```

2. **Plan deployment**:
   ```bash
   terraform plan -var-file=staging.tfvars
   ```

3. **Apply infrastructure**:
   ```bash
   terraform apply -var-file=staging.tfvars
   ```

4. **Configure with Ansible**:
   ```bash
   ansible-playbook -i inventory.ini playbooks/setup.yml
   ```

## ⚙️ Configuration

### Terraform Variables

```hcl
# terraform.tfvars
environment = "staging"
region = "us-east-1"
instance_type = "t3.medium"
cluster_name = "isa-cluster"
domain_name = "isa.example.com"

# Monitoring
enable_monitoring = true
grafana_admin_password = "secure-password"

# Feature flags
feature_flags_enabled = true
flag_service_provider = "launchdarkly"
```

### Ansible Inventory

```ini
# inventory.ini
[isa_servers]
server1 ansible_host=10.0.1.10
server2 ansible_host=10.0.1.11

[kubernetes_master]
master ansible_host=10.0.1.100

[kubernetes_workers]
worker1 ansible_host=10.0.1.101
worker2 ansible_host=10.0.1.102

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/isa-key.pem
```

## 📊 Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'isa-app'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Grafana Dashboards

```json
// grafana/dashboards/isa-overview.json
{
  "dashboard": {
    "title": "ISA_D Overview",
    "tags": ["isa", "overview"],
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

```yaml
# monitoring/alert_rules.yml
groups:
  - name: isa_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"

      - alert: PodCrashLooping
        expr: kube_pod_container_status_restarts_total > 5
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Pod crash looping"
          description: "Pod {{ $labels.pod }} is crash looping"
```

## 🔧 Operations

### Monitoring Commands

```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Query metrics
curl "http://prometheus:9090/api/v1/query?query=up"

# Check Grafana status
curl http://grafana:3000/api/health

# View logs in Loki
curl "http://loki:3100/loki/api/v1/query?query={job=\"isa-app\"}"
```

### Feature Flag Management

```bash
# Enable feature
curl -X POST http://flags:8080/flags/research_agent/enable

# Check flag status
curl http://flags:8080/flags/research_agent

# Update flag rules
curl -X PUT http://flags:8080/flags/compliance_engine \
  -d '{"rules": {"percentage": 50}}'
```

### Infrastructure Updates

```bash
# Update Terraform
terraform plan
terraform apply

# Update Ansible
ansible-playbook playbooks/update.yml

# Rolling update
kubectl rollout restart deployment/isa-superapp
```

## 🔒 Security

### Infrastructure Security

- **Network Policies**: Pod-to-pod communication control
- **RBAC**: Role-based access control
- **Secrets Management**: Encrypted secrets storage
- **Vulnerability Scanning**: Container image scanning

### Monitoring Security

```yaml
# Network policy for monitoring
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: monitoring-policy
spec:
  podSelector:
    matchLabels:
      app: prometheus
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# HPA for application
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: isa-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: isa-superapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Infrastructure Scaling

```hcl
# Terraform auto-scaling
resource "aws_autoscaling_group" "isa_workers" {
  min_size         = 2
  max_size         = 10
  desired_capacity = 3

  launch_template {
    id      = aws_launch_template.isa_worker.id
    version = "$Latest"
  }
}
```

## 🔄 CI/CD Integration

### Infrastructure Testing

```yaml
# .github/workflows/infra-test.yml
name: Infrastructure Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Terraform Format
        run: terraform fmt -check

      - name: Terraform Validate
        run: terraform validate

      - name: Ansible Lint
        run: ansible-lint playbooks/
```

### Automated Deployment

```yaml
# .github/workflows/deploy-infra.yml
name: Deploy Infrastructure
on:
  push:
    branches: [main]
    paths: [infra/**]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Deploy with Terraform
        run: |
          cd infra
          terraform init
          terraform apply -auto-approve
```

## 🧪 Testing

### Infrastructure Tests

```bash
# Test Terraform
terraform plan -detailed-exitcode

# Test Ansible
ansible-playbook --check playbooks/setup.yml

# Lint infrastructure code
tflint
ansible-lint
```

### Integration Tests

```bash
# Test monitoring stack
curl -f http://prometheus:9090/-/healthy
curl -f http://grafana:3000/api/health

# Test feature flags
curl -f http://flags:8080/health
```

## 📚 Related Documentation

- [Helm Deployment](../helm/README.md)
- [Kubernetes Setup](../k8s/README.md)
- [Monitoring Guide](../docs/monitoring/)
- [Security Policy](../SECURITY.md)

## 🤝 Contributing

### Infrastructure Development

1. Follow infrastructure-as-code principles
2. Use version control for all changes
3. Test changes in staging environment
4. Document all modifications
5. Follow security best practices

### Best Practices

- **Immutable Infrastructure**: Treat infrastructure as immutable
- **Version Control**: Keep all infra code in Git
- **Testing**: Test infrastructure changes
- **Documentation**: Document all components
- **Security**: Apply security best practices
- **Monitoring**: Monitor infrastructure health

This infrastructure setup provides a robust, scalable, and secure foundation for the ISA_D platform.