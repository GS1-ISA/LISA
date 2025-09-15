# Unified CI/CD Workflow Configuration

This document describes all the configuration options, environment variables, and secrets required for the unified CI/CD workflow.

## Required Secrets

Configure these secrets in your GitHub repository settings under **Settings > Secrets and variables > Actions**:

### AWS Configuration (Required for Deployment)
```yaml
AWS_ROLE_ARN: "arn:aws:iam::ACCOUNT:role/github-actions-production-role"
AWS_STAGING_ROLE_ARN: "arn:aws:iam::ACCOUNT:role/github-actions-staging-role"
AWS_REGION: "us-east-1"
```

### Container Registry (Required for Image Publishing)
```yaml
GITHUB_TOKEN: # Automatically provided by GitHub Actions
```

### Optional but Recommended
```yaml
SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
CODECOV_TOKEN: "your-codecov-token"
BACKUP_BUCKET: "your-backup-bucket-name"
METRICS_ENDPOINT: "https://your-metrics-endpoint.com/api/metrics"
```

## Environment Variables

These are set in the workflow file and can be customized:

```yaml
env:
  PYTHON_VERSION: '3.11'          # Default Python version
  CACHE_VERSION: 'v1'             # Cache version for cache busting
  REGISTRY: ghcr.io               # Container registry
  IMAGE_NAME: ${{ github.repository }}  # Image name format
```

## Workflow Permissions

The workflow requires these permissions:

```yaml
permissions:
  contents: read          # Read repository contents
  id-token: write         # For OIDC authentication
  packages: write         # For publishing container images
  security-events: write  # For uploading security scan results
  pull-requests: write    # For PR comments and status updates
```

## Environment Protection Rules

Configure these environments in **Settings > Environments**:

### Security Review Environment
- **Name**: `security-review`
- **Purpose**: Security scanning and compliance checks
- **Protection**: None required (runs on every workflow)

### Staging Environment
- **Name**: `staging`
- **Purpose**: Staging deployments
- **Protection**: 
  - Required reviewers: 1 (optional)
  - Deployment branches: `develop`

### Production Environment
- **Name**: `production`
- **Purpose**: Production deployments
- **Protection**:
  - Required reviewers: 2 (recommended)
  - Deployment branches: `main`
  - Wait timer: 10 minutes (recommended)

## OIDC Configuration

To enable OIDC authentication with AWS:

### 1. Create IAM Identity Provider
```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint a031c46782e6b6bed6b2d3b6593b778ab3d3b14a \
  --client-id-list sts.amazonaws.com
```

### 2. Create IAM Role with Trust Policy
Create a file `github-actions-trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
        }
      }
    }
  ]
}
```

### 3. Create the Role
```bash
aws iam create-role \
  --role-name github-actions-production-role \
  --assume-role-policy-document file://github-actions-trust-policy.json

aws iam create-role \
  --role-name github-actions-staging-role \
  --assume-role-policy-document file://github-actions-trust-policy.json
```

### 4. Attach Required Policies
```bash
# For production role
aws iam attach-role-policy \
  --role-name github-actions-production-role \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# For staging role
aws iam attach-role-policy \
  --role-name github-actions-staging-role \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

## Customization Options

### Python Versions
Modify the matrix strategy in the `code-quality` and `test-suite` jobs:
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

### Security Scanning Tools
Add or remove security tools in the `security-checks` job:
```yaml
- name: Install security tools
  run: |
    pip install bandit safety pip-audit detect-secrets semgrep
```

### Deployment Strategies
Customize deployment commands in the `deploy-staging` and `deploy-production` jobs:
```bash
# Example for Kubernetes
kubectl apply -f k8s/${{ needs.initialize.outputs.environment }}/
kubectl rollout status deployment/isa-superapp -n ${{ needs.initialize.outputs.environment }}

# Example for AWS ECS
aws ecs update-service \
  --cluster ${{ needs.initialize.outputs.environment }} \
  --service isa-superapp \
  --force-new-deployment
```

### Notification Channels
Customize notifications in the `post-deployment` job:
```yaml
# Slack notification
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#deployments'
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}

# Email notification
- name: Send Email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
```

## Monitoring and Debugging

### Enable Debug Logging
Add this to your workflow or set as repository variable:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### View Security Reports
Security scan results are available in:
- **GitHub Security tab**: SARIF uploads from Bandit and Trivy
- **Workflow artifacts**: Download from the workflow run page
- **Code scanning alerts**: Automatic creation for found vulnerabilities

### Deployment Metrics
The workflow sends deployment metrics that include:
- Timestamp
- Repository name
- Environment (staging/production)
- Commit SHA
- Branch name
- Deployment status
- Rollback status
- Container image tag

## Troubleshooting Common Issues

### 1. OIDC Authentication Failures
**Symptom**: `AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity`
**Solution**: 
- Verify the IAM role trust policy includes the correct repository
- Check the OIDC provider thumbprint is correct
- Ensure the role ARN is correctly set in secrets

### 2. Container Image Push Failures
**Symptom**: `denied: requested access to the resource is denied`
**Solution**:
- Verify `packages: write` permission is set
- Check the repository has GitHub Packages enabled
- Ensure the image name format is correct

### 3. Security Scan Failures
**Symptom**: Security scans fail or don't upload results
**Solution**:
- Check the `security-events: write` permission
- Verify SARIF file format is correct
- Ensure CodeQL is enabled for the repository

### 4. Deployment Timeouts
**Symptom**: Deployment jobs timeout after 6 hours
**Solution**:
- Add timeout-minutes to deployment jobs
- Optimize deployment scripts
- Consider using deployment slots or blue-green deployments

## Best Practices

1. **Use OIDC for AWS authentication** instead of long-lived credentials
2. **Set up required reviewers** for production deployments
3. **Enable deployment protection rules** for staging and production
4. **Monitor security scan results** regularly
5. **Test rollback procedures** before production use
6. **Keep deployment scripts** in version control
7. **Use semantic versioning** for releases
8. **Document infrastructure changes** in pull requests

## Support

For issues or questions:
1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the [troubleshooting section](#troubleshooting-common-issues)
3. Create an issue in this repository
4. Contact your DevOps team