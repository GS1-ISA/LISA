# GitHub Workflows Consolidation Migration Guide

## Overview

This guide explains how to migrate from the existing separate CI and CI/CD workflows to the new unified pipeline. The consolidation eliminates duplication, standardizes security scanning, and provides a more maintainable and efficient workflow.

## What Changed

### Before (Current State)
- **`.github/workflows/ci.yml`**: Basic CI pipeline with linting, testing, Trivy scanning, and Docker building
- **`.github/workflows/ci-cd.yml`**: Comprehensive CI/CD pipeline with multiple security tools, deployment, OIDC, rollback mechanisms

### After (New Unified Pipeline)
- **`.github/workflows/unified-ci-cd.yml`**: Single workflow that handles both CI and CI/CD scenarios with conditional logic

## Key Improvements

1. **Eliminated Duplication**: Single workflow handles all scenarios
2. **Standardized Security**: Uses comprehensive security scanning from CI/CD workflow
3. **Conditional Deployment**: Automatically determines when to deploy based on branch/event
4. **Optimized Caching**: Consistent caching strategy across all jobs
5. **Enhanced Monitoring**: Better deployment tracking and notifications

## Migration Steps

### Step 1: Review and Test the New Workflow

1. **Create a feature branch** for testing:
   ```bash
   git checkout -b test-unified-workflow
   ```

2. **Add the new workflow** to your repository (already done if you're reading this)

3. **Test in a non-production environment** by pushing to the feature branch

### Step 2: Update Required Secrets

Ensure these secrets are configured in your GitHub repository settings:

#### Required Secrets
```yaml
# AWS Configuration
AWS_ROLE_ARN: "arn:aws:iam::ACCOUNT:role/github-actions-role"
AWS_STAGING_ROLE_ARN: "arn:aws:iam::ACCOUNT:role/github-actions-staging-role"
AWS_REGION: "us-east-1"

# Optional but Recommended
SLACK_WEBHOOK_URL: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
CODECOV_TOKEN: "your-codecov-token"
BACKUP_BUCKET: "your-backup-bucket-name"
METRICS_ENDPOINT: "https://your-metrics-endpoint.com/api/metrics"
```

### Step 3: Update Branch Protection Rules

Update your branch protection rules to require the new workflow checks:

1. Go to **Settings > Branches** in your GitHub repository
2. Edit protection rules for `main` and `develop` branches
3. Update required status checks to use the new unified workflow names:
   - `Security & Compliance`
   - `Code Quality (3.10)`
   - `Code Quality (3.11)`
   - `Code Quality (3.12)`
   - `Test Suite (3.10, unit)`
   - `Test Suite (3.11, unit)`
   - `Test Suite (3.12, unit)`
   - `Build & Package`

### Step 4: Update Deployment Configuration

Update your deployment scripts to work with the new workflow:

#### For Kubernetes Deployments
```yaml
# Update your deployment manifests to use the new image tags
# The unified workflow uses: ghcr.io/${{ github.repository }}:${{ github.sha }}
# For releases: ghcr.io/${{ github.repository }}:${{ github.event.release.tag_name }}
```

#### For Docker Compose
```yaml
# Update docker-compose files to use the new image naming convention
services:
  app:
    image: ghcr.io/your-org/your-repo:${GITHUB_SHA}
```

### Step 5: Test the Migration

1. **Create a test pull request** to verify CI functionality
2. **Deploy to staging** by pushing to the `develop` branch
3. **Deploy to production** by creating a release or pushing to `main`

### Step 6: Monitor and Validate

Monitor the first few runs to ensure:
- All security scans are running correctly
- Deployments are working as expected
- Rollback mechanisms function properly
- Notifications are being sent

### Step 7: Clean Up Old Workflows

Once you've confirmed the new workflow is working correctly:

1. **Disable the old workflows** in GitHub Actions settings
2. **Delete the old workflow files**:
   ```bash
   git rm .github/workflows/ci.yml
   git rm .github/workflows/ci-cd.yml
   git commit -m "Remove old workflows after migration to unified pipeline"
   ```

## Workflow Behavior Matrix

| Event | Branch | Environment | Deployment | Notes |
|-------|--------|-------------|------------|-------|
| Push | `main` | production | ✅ | Full CI/CD with production deployment |
| Push | `develop` | staging | ✅ | Full CI/CD with staging deployment |
| Push | feature/* | none | ❌ | CI only, no deployment |
| Pull Request | any | none | ❌ | CI only, no deployment |
| Release | any | production | ✅ | Production deployment with release tag |
| Manual | any | user choice | ✅ | User selects environment |

## Troubleshooting

### Common Issues

#### 1. Missing Secrets
**Error**: `Error: Credentials could not be loaded`
**Solution**: Ensure all required AWS OIDC secrets are configured

#### 2. Branch Protection Failures
**Error**: `Required status check "ci" was not set by the expected GitHub App`
**Solution**: Update branch protection rules to use new workflow names

#### 3. Deployment Failures
**Error**: `Deployment failed with exit code 1`
**Solution**: Check deployment scripts are compatible with new image naming

#### 4. Cache Issues
**Error**: `Cache not found`
**Solution**: The first run will rebuild caches, subsequent runs should be faster

### Getting Help

If you encounter issues during migration:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the workflow logs for specific error messages
3. Ensure all secrets are properly configured
4. Verify your deployment scripts work with the new image naming convention

## Rollback Plan

If you need to rollback to the old workflows:

1. **Restore the old workflow files** from git history
2. **Re-enable the old workflows** in GitHub Actions settings
3. **Disable the new unified workflow**
4. **Update branch protection rules** back to the old workflow names

## Benefits of the New Workflow

- **Reduced Maintenance**: Single workflow to maintain
- **Consistent Security**: Standardized security scanning across all scenarios
- **Better Performance**: Optimized caching and job dependencies
- **Enhanced Monitoring**: Comprehensive deployment tracking
- **Improved Reliability**: Built-in rollback mechanisms
- **Simplified Configuration**: One set of secrets and configurations

## Next Steps

After successful migration, consider:

1. **Customizing deployment scripts** for your specific infrastructure
2. **Adding additional security scans** as needed
3. **Integrating with your monitoring systems**
4. **Setting up automated rollback triggers**
5. **Adding performance benchmarks** to the pipeline

For questions or issues, please create an issue in the repository or contact the development team.