# Unified CI/CD Pipeline

This repository contains a comprehensive, unified CI/CD pipeline that consolidates multiple workflows into a single, maintainable, and secure deployment process.

## Overview

The unified pipeline replaces multiple individual workflows with a single, intelligent workflow that:
- Supports multiple environments (development, integration, staging, production)
- Implements comprehensive security scanning
- Provides automated rollback capabilities
- Uses OIDC for secure cloud authentication
- Optimizes caching strategies
- Supports multiple deployment strategies

## Architecture

### Workflow Structure

```
.github/workflows/
├── unified-cicd.yml          # Main unified workflow
├── config/                   # Configuration files
│   ├── security-config.yml   # Security scanning configuration
│   ├── deployment-config.yml # Deployment strategies and environments
│   └── oidc-config.yml      # OIDC authentication configuration
└── README.md                # This file
```

### Key Components

1. **Unified Workflow** ([`unified-cicd.yml`](unified-cicd.yml))
   - Single entry point for all CI/CD operations
   - Environment-aware job execution
   - Comprehensive security scanning
   - Multi-strategy deployment support

2. **Security Configuration** ([`config/security-config.yml`](config/security-config.yml))
   - Vulnerability scanning (Trivy, Snyk)
   - Static Application Security Testing (SAST)
   - Dependency scanning
   - Container security
   - Secret scanning
   - Compliance enforcement

3. **Deployment Configuration** ([`config/deployment-config.yml`](config/deployment-config.yml))
   - Environment-specific settings
   - Deployment strategies (rolling, blue-green, canary)
   - Health check configurations
   - Rollback mechanisms
   - Monitoring and alerting

4. **OIDC Configuration** ([`config/oidc-config.yml`](config/oidc-config.yml))
   - Multi-cloud authentication (AWS, Azure, GCP)
   - Secure token-based authentication
   - Role-based access control
   - Compliance and governance

## Features

### 🚀 Multi-Environment Support
- **Development**: Auto-deploy with minimal approvals
- **Integration**: Automated testing with basic approvals
- **Staging**: Production-like environment with enhanced approvals
- **Production**: Secure deployment with multiple approvals

### 🔒 Comprehensive Security
- **Vulnerability Scanning**: Trivy, Snyk integration
- **SAST**: Semgrep, CodeQL analysis
- **Dependency Scanning**: npm-audit, pip-audit, safety
- **Container Security**: Base image validation, vulnerability scanning
- **Secret Scanning**: Gitleaks, TruffleHog
- **Compliance**: SOX, PCI-DSS, HIPAA, SOC2 support

### 🔄 Deployment Strategies
- **Rolling**: Gradual rollout with minimal downtime
- **Blue-Green**: Instant switch with rollback capability
- **Canary**: Progressive rollout with monitoring
- **Emergency**: Fast deployment for critical fixes

### 🔐 Secure Authentication
- **OIDC Integration**: Token-based authentication
- **Multi-Cloud Support**: AWS, Azure, GCP
- **Role-Based Access**: Fine-grained permissions
- **Session Management**: Secure token handling

### 📊 Monitoring & Observability
- **Health Checks**: Comprehensive health monitoring
- **Metrics Collection**: Performance and error tracking
- **Alerting**: Multi-channel notifications
- **Audit Logging**: Complete audit trail

## Usage

### Triggering the Pipeline

The pipeline automatically triggers on:
- Push to main branches
- Pull requests
- Manual workflow dispatch
- Scheduled runs

### Manual Deployment

To manually trigger a deployment:

```yaml
# Development deployment
gh workflow run unified-cicd.yml -f environment=development -f deployment_strategy=rolling

# Production deployment
gh workflow run unified-cicd.yml -f environment=production -f deployment_strategy=canary
```

### Environment Variables

Required secrets:
```bash
# Cloud Provider Credentials
AWS_ACCOUNT_ID
AWS_EXTERNAL_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
GCP_PROJECT_ID

# Service Account Credentials
AZURE_CLIENT_ID_DEV
AZURE_CLIENT_ID_INT
AZURE_CLIENT_ID_STAGING
AZURE_CLIENT_ID_PROD
GCP_SERVICE_ACCOUNT_DEV
GCP_SERVICE_ACCOUNT_INT
GCP_SERVICE_ACCOUNT_STAGING
GCP_SERVICE_ACCOUNT_PROD

# Notification Settings
SLACK_WEBHOOK_URL
PAGERDUTY_SERVICE_KEY

# Security Tools
SNYK_TOKEN
Trivy_USERNAME
Trivy_PASSWORD
```

## Configuration

### Customizing Security Scanning

Edit [`config/security-config.yml`](config/security-config.yml):

```yaml
vulnerability_scanning:
  severity_threshold: "HIGH"
  fail_on_severity: "CRITICAL"
  
sast:
  tools:
    semgrep:
      configs:
        - "p/security-audit"
        - "p/secrets"
        - "p/custom-rules"  # Add your custom rules
```

### Configuring Deployment Strategies

Edit [`config/deployment-config.yml`](config/deployment-config.yml):

```yaml
deployment_strategies:
  canary:
    stages:
      - weight: 10
        duration: 300s
        success_threshold: 95
      - weight: 50
        duration: 600s
        success_threshold: 98
```

### Setting Up OIDC

Edit [`config/oidc-config.yml`](config/oidc-config.yml):

```yaml
providers:
  aws:
    trust_conditions:
      - key: "sub"
        values:
          - "repo:your-org/your-repo:ref:refs/heads/main"
```

## Security Best Practices

### 1. Principle of Least Privilege
- Use minimal required permissions for each environment
- Implement role-based access control
- Regular access reviews

### 2. Secret Management
- Never hardcode secrets in workflows
- Use GitHub Secrets for sensitive data
- Implement secret rotation policies

### 3. Network Security
- Use private networks where possible
- Implement network policies
- Enable encryption in transit

### 4. Compliance
- Regular security audits
- Compliance scanning
- Audit trail maintenance

## Troubleshooting

### Common Issues

1. **OIDC Authentication Failures**
   - Check provider configuration
   - Verify trust relationships
   - Validate token claims

2. **Deployment Failures**
   - Review deployment logs
   - Check health check configurations
   - Verify resource availability

3. **Security Scan Failures**
   - Check tool configurations
   - Review severity thresholds
   - Validate exception handling

### Debug Mode

Enable debug mode by setting:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## Migration from Individual Workflows

### Step 1: Audit Existing Workflows
```bash
# List all existing workflows
ls .github/workflows/*.yml

# Identify unique functionality
grep -r "jobs:" .github/workflows/
```

### Step 2: Map Functionality to Unified Workflow

| Existing Workflow | Unified Workflow Job |
|-------------------|---------------------|
| `build.yml` | `build` |
| `test.yml` | `test` |
| `security-scan.yml` | `security-scan` |
| `deploy-dev.yml` | `deploy-development` |
| `deploy-prod.yml` | `deploy-production` |

### Step 3: Migrate Configuration
1. Extract environment-specific settings
2. Move to appropriate config files
3. Update workflow references
4. Test migration

### Step 4: Validate Migration
1. Run pipeline in development environment
2. Compare outputs with original workflows
3. Verify security scanning results
4. Test deployment strategies

## Performance Optimization

### Caching Strategy
- **Dependency Caching**: npm, pip, Docker layers
- **Build Caching**: Compiled artifacts
- **Security Tool Caching**: Vulnerability databases
- **Deployment Caching**: Container images

### Parallel Execution
- **Matrix Strategy**: Multi-platform builds
- **Job Parallelization**: Independent jobs run concurrently
- **Step Optimization**: Minimize sequential dependencies

### Resource Management
- **Appropriate Runners**: Size-based selection
- **Timeout Configuration**: Prevent hanging jobs
- **Resource Limits**: Memory and CPU constraints

## Monitoring and Alerting

### Metrics Tracked
- **Build Duration**: Pipeline execution time
- **Success Rate**: Deployment success percentage
- **Security Issues**: Vulnerability counts
- **Resource Usage**: CPU, memory, storage

### Alert Channels
- **Slack**: Real-time notifications
- **Email**: Detailed reports
- **PagerDuty**: Critical alerts
- **GitHub Issues**: Automated issue creation

## Compliance and Governance

### Supported Standards
- **SOX**: Financial reporting compliance
- **PCI-DSS**: Payment card industry standards
- **HIPAA**: Healthcare data protection
- **SOC2**: Service organization controls

### Audit Trail
- **Complete Logs**: All pipeline executions
- **Change Tracking**: Configuration modifications
- **Access Records**: User and service access
- **Compliance Reports**: Automated generation

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Testing
```bash
# Run workflow locally (using act)
act -j security-scan

# Validate YAML syntax
yamllint .github/workflows/

# Test configuration files
python scripts/validate_config.py
```

### Code Standards
- Follow YAML best practices
- Use meaningful job names
- Add comprehensive comments
- Maintain backward compatibility

## Support

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides)
- [OIDC Configuration](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers)

### Community
- [GitHub Community](https://github.community/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/github-actions)

### Issues
Report issues using GitHub Issues with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial unified pipeline implementation
- Multi-environment support
- Comprehensive security scanning
- OIDC authentication
- Automated rollback mechanisms

### Roadmap
- [ ] Advanced deployment strategies
- [ ] Machine learning-based optimization
- [ ] Enhanced monitoring capabilities
- [ ] Multi-region deployment support
- [ ] Advanced compliance reporting