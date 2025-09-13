# ISA SuperApp Kubernetes Deployment

This directory contains the complete Kubernetes deployment configuration for the ISA SuperApp, following cloud-native best practices and security standards.

## Architecture Overview

The deployment includes:
- **Namespace isolation** for multi-tenant environments
- **RBAC** with least-privilege access controls
- **Network policies** for micro-segmentation
- **Horizontal Pod Autoscaling** (HPA) for dynamic scaling
- **Vertical Pod Autoscaling** (VPA) for resource optimization
- **Pod Disruption Budgets** (PDB) for high availability
- **Service monitoring** with Prometheus integration
- **Kustomization** for environment-specific configurations

## Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured with cluster access
- Kustomize (v4.0+)
- Metrics Server installed (for HPA)
- VPA admission controller (for VPA)
- Prometheus Operator (for ServiceMonitor)

## Quick Start

```bash
# Deploy to production namespace
kubectl apply -k k8s/

# Deploy to specific environment
kubectl apply -k k8s/overlays/staging
kubectl apply -k k8s/overlays/development
```

## Configuration

### Environment Variables

The application uses ConfigMaps and Secrets for configuration:

- **ConfigMap**: Non-sensitive configuration (log levels, feature flags)
- **Secrets**: Sensitive data (database credentials, API keys)

### Resource Requirements

Default resource allocations:
- **CPU**: 200m requests, 1 core limits
- **Memory**: 256Mi requests, 1Gi limits
- **Replicas**: 3 minimum, 10 maximum

### Scaling Configuration

**HPA Triggers:**
- CPU utilization > 70%
- Memory utilization > 80%
- HTTP requests per second > 100

**VPA Configuration:**
- Min: 100m CPU, 128Mi memory
- Max: 2 CPU, 2Gi memory

## Security Features

### RBAC
- Service accounts with minimal permissions
- Role-based access control for different components
- Separate roles for monitoring, deployment, and runtime

### Network Policies
- Ingress: Only from ingress controller and monitoring
- Egress: DNS, HTTPS, database, and cache access only
- Inter-pod communication restricted to same application

### Pod Security
- Non-root containers
- Read-only root filesystem
- Dropped capabilities
- Security contexts configured

## Monitoring

### Metrics Collection
- Prometheus ServiceMonitor configured
- Application metrics exposed on `/metrics`
- Standard Kubernetes metrics included

### Health Checks
- Liveness probe: `/health`
- Readiness probe: `/ready`
- Startup probe: `/startup`

## Deployment Strategies

### Blue-Green Deployment
```bash
# Deploy to green environment
kubectl apply -k k8s/overlays/green

# Switch traffic
kubectl patch service isa-superapp -p '{"spec":{"selector":{"version":"green"}}}'
```

### Canary Deployment
```bash
# Deploy canary version
kubectl apply -k k8s/overlays/canary

# Monitor metrics and gradually increase traffic
kubectl patch ingress isa-superapp -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"20"}}}'
```

## Rollback Procedures

### Immediate Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/isa-superapp

# Check rollout status
kubectl rollout status deployment/isa-superapp
```

### Versioned Rollback
```bash
# List revision history
kubectl rollout history deployment/isa-superapp

# Rollback to specific revision
kubectl rollout undo deployment/isa-superapp --to-revision=3
```

## Troubleshooting

### Common Issues

1. **Pod not starting**
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=isa-superapp
   kubectl logs -l app.kubernetes.io/name=isa-superapp --previous
   ```

2. **HPA not scaling**
   ```bash
   kubectl describe hpa isa-superapp
   kubectl top pods -l app.kubernetes.io/name=isa-superapp
   ```

3. **Network connectivity issues**
   ```bash
   kubectl get networkpolicy -n isa-superapp
   kubectl describe networkpolicy isa-superapp
   ```

### Debug Commands
```bash
# Check deployment status
kubectl get all -n isa-superapp

# View logs
kubectl logs -f deployment/isa-superapp

# Execute into pod
kubectl exec -it deployment/isa-superapp -- /bin/sh

# Port forward for testing
kubectl port-forward service/isa-superapp 8080:8080
```

## Maintenance

### Updates
```bash
# Update image tag
kubectl set image deployment/isa-superapp isa-superapp=ghcr.io/isa-superapp/isa-superapp:v2.0.0

# Update configuration
kubectl apply -k k8s/
```

### Cleanup
```bash
# Remove all resources
kubectl delete -k k8s/

# Remove namespace (if needed)
kubectl delete namespace isa-superapp
```

## Best Practices

1. **Always use Kustomize** for environment-specific configurations
2. **Test in staging** before production deployment
3. **Monitor metrics** during and after deployment
4. **Use PDBs** to maintain availability during updates
5. **Implement proper health checks** for reliable deployments
6. **Use secrets management** for sensitive data
7. **Regular security audits** of RBAC and network policies

## Support

For issues or questions:
- Check application logs: `kubectl logs -l app.kubernetes.io/name=isa-superapp`
- Review events: `kubectl get events -n isa-superapp --sort-by='.lastTimestamp'`
- Contact the DevOps team for infrastructure issues