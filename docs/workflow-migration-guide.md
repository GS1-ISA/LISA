# Workflow Migration Guide

## Overview

This guide provides step-by-step instructions for migrating from the existing fragmented CI/CD workflows to the new unified pipeline architecture. The migration is designed to be gradual and risk-minimized, allowing teams to validate each step before proceeding.

## Pre-Migration Assessment

### 1. Inventory Existing Workflows

First, catalog all existing workflows and their characteristics:

```bash
# List all workflow files
find .github/workflows -name "*.yml" -o -name "*.yaml" | sort

# Analyze workflow complexity
for workflow in .github/workflows/*.yml; do
    echo "=== $workflow ==="
    grep -c "jobs:" "$workflow"
    grep -c "steps:" "$workflow"
    grep -c "uses:" "$workflow"
done
```

### 2. Identify Critical Dependencies

Document all external dependencies:

- **Container Registries**: Docker Hub, ECR, GCR, ACR
- **Package Registries**: npm, PyPI, Maven, NuGet
- **Deployment Targets**: Kubernetes clusters, cloud providers, on-premises
- **Monitoring Systems**: Prometheus, Grafana, DataDog, New Relic
- **Notification Channels**: Slack, email, PagerDuty, Teams

### 3. Security Audit

Review current security practices:

```bash
# Check for hardcoded secrets
grep -r "password\|secret\|token\|key" .github/workflows/ || true

# Check for insecure practices
grep -r "http://\|--insecure\|skip-verify" .github/workflows/ || true
```

## Migration Phases

### Phase 1: Foundation Setup (Week 1-2)

#### Step 1.1: Repository Preparation

1. **Create unified workflow structure**:
```bash
mkdir -p .github/workflows/config
mkdir -p .github/workflows/actions
mkdir -p .github/workflows/scripts
mkdir -p docs/workflows
```

2. **Set up configuration files**:
```bash
# Copy template configurations
cp templates/deployment-config.yml .github/workflows/config/
cp templates/security-config.yml .github/workflows/config/
cp templates/oidc-config.yml .github/workflows/config/
cp templates/environment-config.yml .github/workflows/config/
cp templates/caching-config.yml .github/workflows/config/
cp templates/monitoring-config.yml .github/workflows/config/
```

3. **Initialize GitHub environments**:
```bash
# Create environments via GitHub API or UI
# Required environments: development, integration, staging, production
```

#### Step 1.2: OIDC Configuration

1. **Configure OIDC providers**:
   - Set up AWS OIDC provider
   - Configure Azure AD OIDC
   - Set up Google Cloud OIDC
   - Configure custom OIDC providers

2. **Create OIDC configuration file**:
```yaml
# .github/workflows/config/oidc-config.yml
oidc:
  providers:
    aws:
      role_arn: "arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/github-actions-role"
      audience: "sts.amazonaws.com"
      subject_claim: "repo:${{ github.repository }}:ref:${{ github.ref }}"
      
    azure:
      client_id: "${{ vars.AZURE_CLIENT_ID }}"
      tenant_id: "${{ vars.AZURE_TENANT_ID }}"
      subscription_id: "${{ vars.AZURE_SUBSCRIPTION_ID }}"
      
    google:
      workload_identity_provider: "${{ vars.GCP_WORKLOAD_IDENTITY_PROVIDER }}"
      service_account: "${{ vars.GCP_SERVICE_ACCOUNT }}"
```

#### Step 1.3: Security Baseline

1. **Set up security scanning tools**:
```bash
# Install security tools
npm install -g snyk
pip install safety bandit
curl -sfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh
```

2. **Configure security policies**:
```yaml
# .github/workflows/config/security-config.yml
security:
  scanning:
    sast:
      enabled: true
      tools: ["sonarqube", "codeql", "semgrep"]
      severity_threshold: "high"
      
    dependency:
      enabled: true
      tools: ["snyk", "safety", "npm-audit"]
      fail_on_severity: "high"
      
    container:
      enabled: true
      tools: ["trivy", "grype", "clair"]
      severity_threshold: "critical"
```

### Phase 2: Workflow Development (Week 3-4)

#### Step 2.1: Create Reusable Actions

1. **Security scanning action**:
```yaml
# .github/workflows/actions/security-scan/action.yml
name: 'Security Scan'
description: 'Comprehensive security scanning'
inputs:
  scan_type:
    description: 'Type of security scan'
    required: true
  severity_threshold:
    description: 'Minimum severity to fail on'
    required: false
    default: 'high'
outputs:
  vulnerabilities_found:
    description: 'Number of vulnerabilities found'
    value: ${{ steps.scan.outputs.vuln_count }}
runs:
  using: 'composite'
  steps:
    - name: Run security scan
      id: scan
      shell: bash
      run: |
        # Security scanning logic here
        echo "vuln_count=0" >> $GITHUB_OUTPUT
```

2. **Deployment action**:
```yaml
# .github/workflows/actions/deploy/action.yml
name: 'Deploy Application'
description: 'Deploy application with strategy'
inputs:
  environment:
    description: 'Target environment'
    required: true
  strategy:
    description: 'Deployment strategy'
    required: false
    default: 'rolling'
  timeout_minutes:
    description: 'Deployment timeout'
    required: false
    default: '30'
outputs:
  deployment_id:
    description: 'Deployment ID'
    value: ${{ steps.deploy.outputs.deployment_id }}
runs:
  using: 'composite'
  steps:
    - name: Deploy application
      id: deploy
      shell: bash
      run: |
        # Deployment logic here
        echo "deployment_id=12345" >> $GITHUB_OUTPUT
```

3. **Rollback action**:
```yaml
# .github/workflows/actions/rollback/action.yml
name: 'Rollback Deployment'
description: 'Rollback to previous version'
inputs:
  environment:
    description: 'Target environment'
    required: true
  deployment_id:
    description: 'Deployment ID to rollback'
    required: true
  reason:
    description: 'Rollback reason'
    required: false
outputs:
  rollback_id:
    description: 'Rollback ID'
    value: ${{ steps.rollback.outputs.rollback_id }}
runs:
  using: 'composite'
  steps:
    - name: Rollback deployment
      id: rollback
      shell: bash
      run: |
        # Rollback logic here
        echo "rollback_id=67890" >> $GITHUB_OUTPUT
```

#### Step 2.2: Create Unified Workflow

1. **Main workflow file**:
```yaml
# .github/workflows/unified-cicd-pipeline.yml
name: Unified CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - integration
          - staging
          - production
      deployment_strategy:
        description: 'Deployment strategy'
        required: false
        type: choice
        options:
          - rolling
          - blue-green
          - canary
          - emergency
        default: 'rolling'

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Code quality and security scanning
  code-quality:
    name: Code Quality & Security
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      actions: read
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run security scans
        uses: ./.github/workflows/actions/security-scan
        with:
          scan_type: 'full'
          severity_threshold: 'high'
      
      - name: Upload security results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: security-results.sarif

  # Build and test
  build-and-test:
    name: Build & Test
    runs-on: ubuntu-latest
    needs: code-quality
    strategy:
      matrix:
        language: [python, javascript]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup language environment
        uses: actions/setup-${{ matrix.language }}@v4
        with:
          ${{ matrix.language }}-version: ${{ matrix.language == 'python' && env.PYTHON_VERSION || env.NODE_VERSION }}
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.npm
            ~/.cache/yarn
          key: ${{ runner.os }}-${{ matrix.language }}-${{ hashFiles('**/requirements.txt', '**/package-lock.json') }}
      
      - name: Install dependencies
        run: |
          if [ "${{ matrix.language }}" == "python" ]; then
            pip install -r requirements.txt
          else
            npm ci
          fi
      
      - name: Run tests
        run: |
          if [ "${{ matrix.language }}" == "python" ]; then
            pytest --cov=./ --cov-report=xml
          else
            npm test -- --coverage
          fi
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: ${{ matrix.language }}

  # Build and push container image
  build-image:
    name: Build Container Image
    runs-on: ubuntu-latest
    needs: build-and-test
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Security validation
  security-validation:
    name: Security Validation
    runs-on: ubuntu-latest
    needs: build-image
    permissions:
      contents: read
      security-events: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Container security scan
        uses: ./.github/workflows/actions/security-scan
        with:
          scan_type: 'container'
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
      
      - name: Infrastructure security scan
        uses: ./.github/workflows/actions/security-scan
        with:
          scan_type: 'infrastructure'
          infrastructure_path: './infrastructure'

  # Deploy to environment
  deploy:
    name: Deploy to ${{ github.event.inputs.environment || 'development' }}
    runs-on: ubuntu-latest
    needs: security-validation
    environment:
      name: ${{ github.event.inputs.environment || 'development' }}
      url: ${{ steps.deploy.outputs.environment_url }}
    permissions:
      contents: read
      packages: read
      id-token: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure OIDC credentials
        uses: aws-actions/configure-aws-credentials@v4
        if: github.event.inputs.environment == 'production'
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          role-session-name: github-actions-deployment
          aws-region: ${{ vars.AWS_REGION }}
      
      - name: Deploy application
        id: deploy
        uses: ./.github/workflows/actions/deploy
        with:
          environment: ${{ github.event.inputs.environment || 'development' }}
          strategy: ${{ github.event.inputs.deployment_strategy || 'rolling' }}
          timeout_minutes: 30
      
      - name: Run smoke tests
        run: |
          # Smoke test logic here
          echo "Running smoke tests..."
      
      - name: Notify deployment status
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            Deployment to ${{ github.event.inputs.environment || 'development' }} ${{ job.status }}
            Strategy: ${{ github.event.inputs.deployment_strategy || 'rolling' }}
            Commit: ${{ github.sha }}

  # Post-deployment monitoring
  monitor:
    name: Post-deployment Monitoring
    runs-on: ubuntu-latest
    needs: deploy
    if: always()
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup monitoring
        run: |
          # Setup monitoring tools
          echo "Setting up monitoring..."
      
      - name: Collect metrics
        run: |
          # Collect deployment metrics
          echo "Collecting metrics..."
      
      - name: Check deployment health
        run: |
          # Health check logic
          echo "Checking deployment health..."
```

### Phase 3: Testing & Validation (Week 5-6)

#### Step 3.1: Unit Testing

1. **Test reusable actions**:
```bash
# Create test directory
mkdir -p .github/workflows/actions/tests

# Create test workflow
cat > .github/workflows/test-actions.yml << 'EOF'
name: Test Reusable Actions

on:
  pull_request:
    paths:
      - '.github/workflows/actions/**'

jobs:
  test-security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/workflows/actions/security-scan
        with:
          scan_type: 'test'
          
  test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/workflows/actions/deploy
        with:
          environment: 'test'
          strategy: 'rolling'
EOF
```

2. **Validate configurations**:
```python
# scripts/validate_configs.py
#!/usr/bin/env python3
import yaml
import json
import sys
from pathlib import Path

def validate_yaml_file(file_path):
    """Validate YAML file syntax and schema"""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return True, "Valid YAML"
    except yaml.YAMLError as e:
        return False, str(e)

def validate_workflow_config():
    """Validate workflow configuration files"""
    config_dir = Path('.github/workflows/config')
    errors = []
    
    for config_file in config_dir.glob('*.yml'):
        valid, message = validate_yaml_file(config_file)
        if not valid:
            errors.append(f"{config_file}: {message}")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    valid, errors = validate_workflow_config()
    if not valid:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("All configurations are valid")
```

#### Step 3.2: Integration Testing

1. **Test workflow in isolation**:
```bash
# Create test branch
git checkout -b test-unified-workflow

# Push test commit
git commit --allow-empty -m "Test unified workflow"
git push origin test-unified-workflow

# Monitor workflow execution
gh run list --workflow=unified-cicd-pipeline.yml
```

2. **Validate deployment strategies**:
```bash
# Test different deployment strategies
for strategy in rolling blue-green canary; do
    echo "Testing $strategy deployment..."
    gh workflow run unified-cicd-pipeline.yml \
        --ref test-unified-workflow \
        --field environment=development \
        --field deployment_strategy=$strategy
done
```

#### Step 3.3: Performance Testing

1. **Measure workflow performance**:
```python
# scripts/measure_workflow_performance.py
#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

def get_workflow_runs(repo, workflow_id):
    """Get workflow run statistics"""
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    runs = response.json()['workflow_runs']
    
    stats = []
    for run in runs[:10]:  # Last 10 runs
        stats.append({
            'id': run['id'],
            'status': run['status'],
            'conclusion': run['conclusion'],
            'created_at': run['created_at'],
            'updated_at': run['updated_at'],
            'run_duration': calculate_duration(run['created_at'], run['updated_at'])
        })
    
    return stats

def calculate_duration(start_time, end_time):
    """Calculate duration between two timestamps"""
    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    return (end - start).total_seconds() / 60  # minutes

if __name__ == "__main__":
    repo = "your-org/your-repo"
    workflow_id = "unified-cicd-pipeline.yml"
    
    stats = get_workflow_runs(repo, workflow_id)
    
    print("Workflow Performance Statistics:")
    for stat in stats:
        print(f"Run {stat['id']}: {stat['status']} - {stat['run_duration']:.2f} minutes")
```

### Phase 4: Gradual Rollout (Week 7-8)

#### Step 4.1: Environment Migration

1. **Start with development environment**:
```bash
# Enable unified workflow for development
# Update branch protection rules
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Code Quality & Security", "Build & Test", "Security Validation"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
```

2. **Monitor development deployments**:
```bash
# Set up monitoring alerts
# Create alert for deployment failures
cat > .github/workflows/config/alert-rules.yml << 'EOF'
alerts:
  - name: "development-deployment-failure"
    condition: "deployment_status == 'failed' AND environment == 'development'"
    severity: "warning"
    channels: ["slack", "email"]
EOF
```

#### Step 4.2: Integration Environment

1. **Migrate integration environment**:
```bash
# Update integration environment configuration
# Add integration-specific settings
cat >> .github/workflows/config/environment-config.yml << 'EOF'

integration:
  deployment:
    strategy: "blue-green"
    health_check_url: "https://integration.example.com/health"
    timeout_minutes: 45
    
  monitoring:
    enabled: true
    alert_threshold_multiplier: 1.2
    
  security:
    scanning:
      enabled: true
      severity_threshold: "medium"
EOF
```

2. **Validate integration performance**:
```bash
# Run integration tests
gh workflow run unified-cicd-pipeline.yml \
  --ref main \
  --field environment=integration \
  --field deployment_strategy=blue-green
```

#### Step 4.3: Staging Environment

1. **Prepare staging environment**:
```bash
# Configure staging with production-like settings
cat >> .github/workflows/config/environment-config.yml << 'EOF'

staging:
  deployment:
    strategy: "canary"
    canary_percentage: 10
    health_check_url: "https://staging.example.com/health"
    timeout_minutes: 60
    
  monitoring:
    enabled: true
    alert_threshold_multiplier: 1.0
    
  security:
    scanning:
      enabled: true
      severity_threshold: "low"
      
  approvals:
    required: true
    approvers: ["staging-approvers"]
EOF
```

2. **Conduct staging validation**:
```bash
# Perform comprehensive testing
# Include performance tests
# Include security tests
# Include user acceptance tests
```

#### Step 4.4: Production Environment

1. **Final production setup**:
```bash
# Configure production with strict settings
cat >> .github/workflows/config/environment-config.yml << 'EOF'

production:
  deployment:
    strategy: "canary"
    canary_percentage: 5
    health_check_url: "https://app.example.com/health"
    timeout_minutes: 90
    
  monitoring:
    enabled: true
    alert_threshold_multiplier: 0.8
    
  security:
    scanning:
      enabled: true
      severity_threshold: "low"
      
  approvals:
    required: true
    approvers: ["production-approvers", "security-team"]
    
  rollback:
    automatic: true
    conditions:
      - "error_rate > 0.01"
      - "response_time > 2000ms"
      - "availability < 99.9%"
EOF
```

2. **Production go-live**:
```bash
# Schedule production migration
# Coordinate with stakeholders
# Prepare rollback plan
# Execute final deployment
```

### Phase 5: Optimization & Cleanup (Week 9-10)

#### Step 5.1: Performance Optimization

1. **Analyze workflow performance**:
```python
# scripts/optimize_workflow.py
#!/usr/bin/env python3
import yaml
import json
from pathlib import Path

def analyze_workflow_performance():
    """Analyze workflow performance and suggest optimizations"""
    # Collect performance metrics
    # Identify bottlenecks
    # Suggest optimizations
    pass

def optimize_caching_strategy():
    """Optimize caching configuration"""
    # Analyze cache hit rates
    # Optimize cache keys
    # Implement cache warming
    pass
```

2. **Implement optimizations**:
```bash
# Update caching configuration
# Optimize build steps
# Parallelize independent tasks
# Implement conditional execution
```

#### Step 5.2: Documentation Update

1. **Update team documentation**:
```bash
# Create team-specific guides
# Update runbooks
# Document troubleshooting steps
# Create FAQ
```

2. **Training sessions**:
```bash
# Conduct team training
# Create video tutorials
# Set up office hours
# Create support channels
```

#### Step 5.3: Legacy Cleanup

1. **Remove old workflows**:
```bash
# Archive old workflow files
mkdir -p .github/workflows/archive
git mv .github/workflows/old-*.yml .github/workflows/archive/

# Update references
# Remove old configurations
# Clean up secrets
```

2. **Update integrations**:
```bash
# Update external integrations
# Migrate webhooks
# Update monitoring tools
# Update documentation
```

## Post-Migration Validation

### 1. Success Metrics

Monitor these key metrics:

- **Deployment Frequency**: Number of deployments per day/week
- **Lead Time**: Time from commit to production
- **MTTR**: Mean time to recovery
- **Change Failure Rate**: Percentage of deployments causing failures
- **Security Scan Coverage**: Percentage of code covered by security scans
- **Performance**: Build and deployment duration

### 2. Continuous Improvement

Establish processes for:

- **Regular Reviews**: Monthly workflow performance reviews
- **Feedback Collection**: Gather team feedback
- **Issue Tracking**: Track and resolve migration issues
- **Optimization**: Continuous workflow optimization

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   ```bash
   # Check OIDC configuration
   # Verify role permissions
   # Check token expiration
   ```

2. **Deployment Timeouts**:
   ```bash
   # Increase timeout values
   # Optimize deployment steps
   # Check network connectivity
   ```

3. **Cache Issues**:
   ```bash
   # Clear cache
   # Update cache keys
   # Check cache permissions
   ```

4. **Security Scan Failures**:
   ```bash
   # Update security tools
   # Check tool configurations
   # Review severity thresholds
   ```

### Support Channels

- **Internal Slack**: #cicd-support
- **Email**: devops-team@company.com
- **Office Hours**: Tuesdays and Thursdays, 2-3 PM
- **Documentation**: Internal wiki

## Conclusion

This migration guide provides a structured approach to transitioning from fragmented CI/CD workflows to a unified pipeline. The gradual migration approach minimizes risk while ensuring continuous delivery capabilities throughout the transition period.

Regular monitoring and continuous improvement processes ensure the unified workflow remains optimized and aligned with team needs.