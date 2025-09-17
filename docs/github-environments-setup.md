# GitHub Environments Setup Guide

This document outlines the required GitHub environment configurations for the unified CI/CD pipeline.

## Required Environments

### 1. Staging Environment
- **Name**: `staging`
- **Purpose**: Pre-production testing environment
- **Protection Rules**:
  - Required reviewers: 1 (optional for develop branch)
  - Deployment branches: `develop`
  - Environment secrets:
    - `AWS_ROLE_ARN`: IAM role for OIDC authentication
    - `STAGING_DATABASE_URL`: Database connection string
    - `STAGING_API_KEY`: API key for staging services

### 2. Production Environment
- **Name**: `production`
- **Purpose**: Live production environment
- **Protection Rules**:
  - Required reviewers: 2 (minimum)
  - Deployment branches: `main`
  - Wait timer: 30 minutes (optional)
  - Environment secrets:
    - `AWS_ROLE_ARN`: IAM role for OIDC authentication
    - `PRODUCTION_DATABASE_URL`: Database connection string
    - `PRODUCTION_API_KEY`: API key for production services
    - `SLACK_WEBHOOK_URL`: For deployment notifications

## Environment Configuration Steps

### Step 1: Create Environments in GitHub

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Environments**
3. Click **New environment**
4. Create environments with the following names:
   - `staging`
   - `production`

### Step 2: Configure Environment Protection Rules

#### For Staging Environment:
1. **Deployment protection rules**:
   - ✅ Required reviewers: 1 (set to team lead or senior developer)
   - ✅ Deployment branches: `develop`
   - ❌ Wait timer: Not required

2. **Environment secrets**:
   - Add `AWS_ROLE_ARN` with your IAM role ARN
   - Add other staging-specific secrets

#### For Production Environment:
1. **Deployment protection rules**:
   - ✅ Required reviewers: 2 (set to senior team members)
   - ✅ Deployment branches: `main`
   - ✅ Wait timer: 30 minutes (recommended)

2. **Environment secrets**:
   - Add `AWS_ROLE_ARN` with your IAM role ARN
   - Add other production-specific secrets

### Step 3: Configure OIDC Authentication

1. **Create IAM OIDC Provider** (AWS):
   ```bash
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --thumbprint a031c46782e6b6c2c2bb7b8b0b8b0b8b0b8b0b8b0 \
     --client-id-list sts.amazonaws.com
   ```

2. **Create IAM Role with Trust Policy**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::YOUR_ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
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

3. **Add IAM Role ARN to Environment Secrets**:
   - Add the role ARN as `AWS_ROLE_ARN` in both environments

### Step 4: Configure Branch Protection Rules

1. **For `main` branch**:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging
   - ✅ Restrict pushes that create files larger than 100MB

2. **For `develop` branch**:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

### Step 5: Configure Required Status Checks

Add these status checks to your branch protection rules:

#### For `main` branch:
- `unit-tests`
- `integration-tests`
- `e2e-tests`
- `build`
- `docker-build`
- `deploy-staging`

#### For `develop` branch:
- `unit-tests`
- `integration-tests`
- `build`

## Environment Variables

### Global Environment Variables (Repository Secrets):
- `GITHUB_TOKEN`: Automatically provided
- `REGISTRY`: Container registry URL
- `IMAGE_NAME`: Container image name

### Environment-Specific Variables:
- **Staging**: `AWS_ROLE_ARN`, `STAGING_*` secrets
- **Production**: `AWS_ROLE_ARN`, `PRODUCTION_*` secrets

## Monitoring and Alerts

### Deployment Notifications:
- Configure Slack webhook for deployment notifications
- Set up email alerts for failed deployments
- Monitor deployment duration and success rates

### Environment Health Checks:
- Implement health check endpoints
- Set up monitoring dashboards
- Configure alerting for environment issues

## Troubleshooting

### Common Issues:

1. **Environment not found**:
   - Ensure environment names match exactly (`staging`, `production`)
   - Check environment creation in repository settings

2. **OIDC authentication failures**:
   - Verify IAM role trust policy
   - Check OIDC provider configuration
   - Ensure role ARN is correct in environment secrets

3. **Deployment approval issues**:
   - Verify required reviewers are set correctly
   - Check user permissions for environment access
   - Ensure branch protection rules are configured

4. **Secret access issues**:
   - Verify secrets are added to correct environment
   - Check secret names match workflow references
   - Ensure secrets are properly encrypted

## Security Best Practices

1. **Use OIDC authentication** instead of long-lived credentials
2. **Implement least privilege** for IAM roles
3. **Use environment protection rules** for production deployments
4. **Require multiple approvals** for production changes
5. **Audit deployment access** regularly
6. **Rotate secrets** on a regular schedule
7. **Monitor deployment activity** for anomalies

## Next Steps

After setting up environments:
1. Test the deployment pipeline in staging
2. Verify rollback mechanisms work correctly
3. Set up monitoring and alerting
4. Train team on deployment procedures
5. Document incident response procedures