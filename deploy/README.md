# ISA SuperApp Deployment Guide

This guide provides comprehensive instructions for deploying the ISA SuperApp to AWS EKS using Kubernetes and Helm.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Environment Setup](#environment-setup)
- [Deployment Process](#deployment-process)
- [Monitoring and Observability](#monitoring-and-observability)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Prerequisites

### Required Tools

- **kubectl** (>= 1.24): Kubernetes CLI
- **helm** (>= 3.10): Kubernetes package manager
- **awscli** (>= 2.0): AWS CLI
- **docker** (>= 20.0): Container runtime
- **git**: Version control

### AWS Resources Required

- **EKS Cluster**: Kubernetes control plane
- **ECR Repository**: Container image registry
- **RDS PostgreSQL**: Managed database (optional, can use in-cluster)
- **ElastiCache Redis**: Managed cache (optional, can use in-cluster)
- **ALB Ingress Controller**: For load balancing
- **AWS Secrets Manager**: For secrets management
- **IAM Roles**: For service accounts and CI/CD

### Network Requirements

- **VPC**: With public and private subnets
- **Security Groups**: Properly configured for EKS
- **NAT Gateway**: For private subnet internet access
- **Route 53**: For DNS management

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   AWS ALB       │    │   AWS WAF       │
│   Load Balancer │────│   Web Firewall  │
└─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │   Frontend      │
│   Controller    │────│   (Next.js)     │
└─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│   ISA SuperApp  │    │   PostgreSQL    │
│   (FastAPI)     │────│   Database      │
└─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Redis Cache   │    │   Neo4j Graph   │
│                 │    │   Database      │
└─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   Grafana       │
│   Monitoring    │────│   Dashboards    │
└─────────────────┘    └─────────────────┘
```

## Environment Setup

### 1. AWS Infrastructure Setup

Create the required AWS infrastructure using Terraform or CloudFormation:

```bash
# Example Terraform commands
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 2. Kubernetes Cluster Setup

Configure kubectl to connect to your EKS cluster:

```bash
aws eks update-kubeconfig --region us-east-1 --name isa-production-cluster
kubectl get nodes
```

### 3. Helm Setup

Add required Helm repositories:

```bash
# Add Bitnami repository for PostgreSQL and Redis
helm repo add bitnami https://charts.bitnami.com/bitnami

# Add Prometheus community repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Add Grafana repository
helm repo add grafana https://grafana.github.io/helm-charts

# Add Neo4j repository
helm repo add neo4j https://neo4j.github.io/helm-charts

# Update repositories
helm repo update
```

### 4. Secrets Management

Set up AWS Secrets Manager secrets:

```bash
# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name isa-superapp/production/database \
  --secret-string '{"username":"isa_user","password":"your-secure-password"}'

aws secretsmanager create-secret \
  --name isa-superapp/production/redis \
  --secret-string '{"password":"your-redis-password"}'
```

## Deployment Process

### Automated Deployment (Recommended)

Use the provided deployment script:

```bash
# Deploy to staging
./deploy/deploy.sh deploy staging v1.2.3

# Deploy to production
./deploy/deploy.sh deploy production v1.2.3

# Check deployment status
./deploy/deploy.sh status production
```

### Manual Deployment

Deploy using Helm directly:

```bash
# Deploy to staging
helm upgrade --install isa-superapp ./helm/isa-superapp \
  --namespace isa-superapp-staging \
  --create-namespace \
  --values deploy/staging-values.yaml \
  --set isaSuperapp.image.tag=v1.2.3 \
  --set frontend.image.tag=v1.2.3 \
  --wait

# Deploy to production
helm upgrade --install isa-superapp ./helm/isa-superapp \
  --namespace isa-superapp \
  --create-namespace \
  --values deploy/production-values.yaml \
  --set isaSuperapp.image.tag=v1.2.3 \
  --set frontend.image.tag=v1.2.3 \
  --wait
```

### CI/CD Deployment

The GitHub Actions pipeline will automatically deploy on:

- **Staging**: Push to `develop` branch
- **Production**: Push to `main` branch or manual trigger

## Monitoring and Observability

### Accessing Grafana

```bash
# Port forward Grafana
kubectl port-forward svc/grafana 3000:80 -n isa-monitoring

# Access at http://localhost:3000
# Default credentials: admin/admin (change immediately)
```

### Prometheus Metrics

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus-server 9090:80 -n isa-monitoring

# Access at http://localhost:9090
```

### Application Metrics

The application exposes metrics at:
- **ISA SuperApp**: `http://api.isa-superapp.com/metrics`
- **Frontend**: `http://app.isa-superapp.com/api/metrics`

### Health Checks

```bash
# Check application health
curl https://api.isa-superapp.com/health

# Check database connectivity
curl https://api.isa-superapp.com/health/database

# Check cache connectivity
curl https://api.isa-superapp.com/health/cache
```

## Security Considerations

### Network Security

- **Network Policies**: Enforce traffic rules between pods
- **Security Groups**: Restrict traffic at the EC2 level
- **WAF**: Protect against common web attacks
- **SSL/TLS**: End-to-end encryption

### Authentication & Authorization

- **RBAC**: Role-based access control for Kubernetes
- **IAM**: AWS identity and access management
- **Secrets Management**: AWS Secrets Manager integration
- **Service Accounts**: Kubernetes service account tokens

### Security Scanning

The CI/CD pipeline includes:
- **Bandit**: Python security scanning
- **Safety**: Python dependency vulnerability scanning
- **Trivy**: Container vulnerability scanning
- **CodeQL**: Static application security testing (SAST)
- **Semgrep**: Semantic code analysis

### Compliance

- **Pod Security Standards**: Enforced via admission controllers
- **Image Security**: Regular vulnerability scanning
- **Audit Logging**: Comprehensive audit trails
- **Data Encryption**: At rest and in transit

## Troubleshooting

### Common Issues

#### 1. Pod Startup Failures

```bash
# Check pod events
kubectl describe pod <pod-name> -n isa-superapp

# Check pod logs
kubectl logs <pod-name> -n isa-superapp --previous

# Check resource usage
kubectl top pods -n isa-superapp
```

#### 2. Database Connection Issues

```bash
# Check database pod status
kubectl get pods -n isa-database

# Check database logs
kubectl logs -f deployment/isa-postgresql -n isa-database

# Test database connectivity
kubectl exec -it deployment/isa-superapp -n isa-superapp -- python -c "
import psycopg2
conn = psycopg2.connect('host=isa-postgresql user=isa_user password=*** dbname=isa_superapp')
print('Database connection successful')
"
```

#### 3. Ingress Issues

```bash
# Check ingress status
kubectl get ingress -n isa-superapp

# Check ALB status
kubectl get targetgroupbindings -n isa-superapp

# Check ingress controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

#### 4. Autoscaling Issues

```bash
# Check HPA status
kubectl get hpa -n isa-superapp

# Check metrics server
kubectl get apiservice v1beta1.metrics.k8s.io

# Check pod resource usage
kubectl top pods -n isa-superapp
```

### Debugging Commands

```bash
# Get all resources in namespace
kubectl get all -n isa-superapp

# Check events
kubectl get events -n isa-superapp --sort-by=.metadata.creationTimestamp

# Check resource usage
kubectl top nodes
kubectl top pods -n isa-superapp

# Check network policies
kubectl get networkpolicies -n isa-superapp

# Check secrets
kubectl get secrets -n isa-superapp
```

## Rollback Procedures

### Automated Rollback

```bash
# Rollback to previous release
./deploy/deploy.sh rollback production 1

# Rollback staging
./deploy/deploy.sh rollback staging 1
```

### Manual Rollback

```bash
# Check available revisions
helm history isa-superapp -n isa-superapp

# Rollback to specific revision
helm rollback isa-superapp 1 -n isa-superapp

# Force rollback (skip hooks)
helm rollback isa-superapp 1 -n isa-superapp --force
```

### Emergency Rollback

In case of critical issues:

1. **Immediate rollback**:
   ```bash
   helm rollback isa-superapp 1 -n isa-superapp --wait --timeout=300s
   ```

2. **Scale down problematic deployment**:
   ```bash
   kubectl scale deployment isa-superapp --replicas=0 -n isa-superapp
   ```

3. **Switch to backup deployment** (if available):
   ```bash
   kubectl scale deployment isa-superapp-backup --replicas=5 -n isa-superapp
   ```

## Performance Optimization

### Resource Optimization

- **HPA Configuration**: Adjust based on load patterns
- **Pod Resource Limits**: Set appropriate CPU/memory limits
- **Node Sizing**: Choose appropriate EC2 instance types
- **Storage Optimization**: Use appropriate storage classes

### Monitoring Optimization

- **Metrics Collection**: Configure appropriate scrape intervals
- **Log Aggregation**: Implement efficient log shipping
- **Alert Thresholds**: Tune based on normal operation patterns
- **Dashboard Customization**: Create relevant dashboards

## Backup and Recovery

### Database Backups

```bash
# Manual PostgreSQL backup
kubectl exec -it deployment/isa-postgresql -n isa-database -- pg_dump -U isa_user isa_superapp > backup.sql

# Automated backups using AWS Backup or similar
```

### Application Backups

- **Configuration Backups**: Helm releases and values
- **Persistent Volume Backups**: EBS snapshots
- **Secret Backups**: AWS Secrets Manager versioning

### Disaster Recovery

1. **Cluster Failure**: Multi-AZ deployment with cross-region replication
2. **Data Loss**: Point-in-time recovery from backups
3. **Application Failure**: Blue-green deployment strategy
4. **Network Failure**: Multi-region deployment with failover

## Support and Maintenance

### Regular Maintenance Tasks

- **Security Updates**: Regular dependency updates
- **Performance Monitoring**: Continuous performance tracking
- **Log Rotation**: Implement log rotation policies
- **Backup Verification**: Regular backup testing

### Support Contacts

- **DevOps Team**: devops@isa-superapp.com
- **Security Team**: security@isa-superapp.com
- **Development Team**: dev@isa-superapp.com

### Documentation Updates

Keep this documentation updated with:
- New deployment procedures
- Security updates
- Performance optimizations
- Troubleshooting guides

---

For additional support or questions, please contact the DevOps team.