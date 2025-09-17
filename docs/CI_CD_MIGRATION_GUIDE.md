# CI/CD Migration Guide: From Legacy to Unified Pipeline

## Overview

This guide provides a step-by-step approach to migrate from existing GitHub Actions workflows to the new unified CI/CD pipeline architecture. The migration is designed to be gradual, low-risk, and reversible.

## Migration Strategy

### Phase 1: Assessment and Preparation (Week 1-2)

#### 1.1 Inventory Existing Workflows

First, catalog all existing workflows and their purposes:

```bash
# List all workflows in the repository
gh api repos/:owner/:repo/actions/workflows | jq '.workflows[] | {name: .name, path: .path, state: .state}'

# Get detailed information about each workflow
for workflow in $(gh api repos/:owner/:repo/actions/workflows | jq -r '.workflows[].id'); do
  echo "Workflow ID: $workflow"
  gh api repos/:owner/:repo/actions/workflows/$workflow | jq '{name: .name, path: .path, created_at: .created_at}'
done
```

#### 1.2 Analyze Workflow Dependencies

Document the relationships between workflows:

```bash
# Extract workflow calls and dependencies
find .github/workflows -name "*.yml" -o -name "*.yaml" | while read file; do
  echo "=== $file ==="
  grep -E "uses:|needs:" "$file" | head -20
done
```

#### 1.3 Identify Critical Workflows

Categorize workflows by importance:

| Priority | Description | Examples |
|----------|-------------|----------|
| **Critical** | Production deployment, security scanning | `deploy-prod.yml`, `security-scan.yml` |
| **High** | Staging deployment, testing | `deploy-staging.yml`, `run-tests.yml` |
| **Medium** | Code quality, linting | `lint.yml`, `code-quality.yml` |
| **Low** | Documentation, notifications | `update-docs.yml`, `notify-slack.yml` |

#### 1.4 Create Migration Timeline

```yaml
# migration-timeline.yml
phases:
  phase-1:
    duration: "2 weeks"
    tasks:
      - "Inventory existing workflows"
      - "Set up new workflow infrastructure"
      - "Create test environment"
  
  phase-2:
    duration: "2 weeks"
    tasks:
      - "Migrate low-priority workflows"
      - "Test new workflow components"
      - "Validate functionality"
  
  phase-3:
    duration: "2 weeks"
      - "Migrate high-priority workflows"
      - "Implement security features"
      - "Performance testing"
  
  phase-4:
    duration: "1 week"
    tasks:
      - "Migrate critical workflows"
      - "Production validation"
      - "Remove legacy workflows"
```

### Phase 2: Infrastructure Setup (Week 1-2)

#### 2.1 Set Up OIDC Authentication

Configure AWS OIDC for secure authentication:

```bash
# Create OIDC provider (one-time setup)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint a031c46782e6e6c662c2c87c76da9aa62ccabd8e \
  --client-id-list sts.amazonaws.com

# Create IAM role for GitHub Actions
cat > github-actions-role.json << EOF
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
EOF

aws iam create-role --role-name GitHubActionsRole --assume-role-policy-document file://github-actions-role.json
```

#### 2.2 Configure Repository Secrets

Add required secrets to your repository:

```bash
# Using GitHub CLI
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::YOUR_ACCOUNT:role/GitHubActionsRole"
gh secret set SNYK_TOKEN --body "your-snyk-token"
gh secret set SONAR_TOKEN --body "your-sonar-token"
gh secret set SLACK_WEBHOOK_URL --body "your-slack-webhook"
gh secret set TEST_DATABASE_URL --body "postgresql://testuser:testpass@localhost:5432/testdb"
gh secret set TEST_API_KEY --body "your-test-api-key"
```

#### 2.3 Set Up Environment Protection Rules

Configure GitHub environments:

```bash
# Create environments
gh api repos/:owner/:repo/environments \
  --method POST \
  --field name=staging \
  --field wait_timer=30

gh api repos/:owner/:repo/environments \
  --method POST \
  --field name=production \
  --field wait_timer=60

# Add protection rules
gh api repos/:owner/:repo/environments/staging/protection_rules \
  --method POST \
  --field type=required_reviewers \
  --field reviewers[].type=User \
  --field reviewers[].id=YOUR_USER_ID

gh api repos/:owner/:repo/environments/production/protection_rules \
  --method POST \
  --field type=required_reviewers \
  --field reviewers[].type=User \
  --field reviewers[].id=YOUR_USER_ID
```

### Phase 3: Component Migration (Week 3-4)

#### 3.1 Migrate Code Quality Workflows

Start with the [`code-quality.yml`](.github/workflows/code-quality.yml) workflow:

```yaml
# Test the new workflow
name: Test Code Quality Migration
on:
  push:
    branches: [feature/test-migration]

jobs:
  test-new-workflow:
    uses: ./.github/workflows/code-quality.yml
    with:
      environment: development
      enable-sast: true
      enable-dependency-check: true
      enable-secret-scanning: true
      upload-results: true
    secrets:
      SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

#### 3.2 Migrate Build and Test Workflows

Test the [`build-and-test.yml`](.github/workflows/build-and-test.yml) workflow:

```yaml
# Test build and test migration
name: Test Build Migration
on:
  pull_request:
    branches: [develop]

jobs:
  test-build:
    uses: ./.github/workflows/build-and-test.yml
    with:
      environment: development
      cache-key: ${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
      run-unit-tests: true
      run-integration-tests: false
      run-e2e-tests: false
    secrets:
      TEST_DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
      TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
```

#### 3.3 Validate Migration Results

Compare results between old and new workflows:

```bash
# Get workflow run history
gh api repos/:owner/:repo/actions/runs \
  --paginate \
  --jq '.workflow_runs[] | select(.name == "Test Code Quality Migration") | {id: .id, status: .status, conclusion: .conclusion, created_at: .created_at}'

# Compare with legacy workflow results
gh api repos/:owner/:repo/actions/runs \
  --paginate \
  --jq '.workflow_runs[] | select(.name == "Legacy Code Quality") | {id: .id, status: .status, conclusion: .conclusion, created_at: .created_at}'
```

### Phase 4: Production Migration (Week 5-6)

#### 4.1 Create Migration Script

```bash
#!/bin/bash
# migrate-to-unified.sh

set -euo pipefail

echo "🚀 Starting CI/CD migration to unified pipeline..."

# Backup existing workflows
echo "📋 Backing up existing workflows..."
mkdir -p workflow-backups
cp -r .github/workflows/* workflow-backups/
git add workflow-backups/
git commit -m "Backup existing workflows before migration"

# Enable new unified workflow
echo "🔧 Enabling unified workflow..."
git checkout -b feature/unified-cicd-migration

# Update workflow triggers
echo "🔄 Updating workflow triggers..."
# This would be customized based on your specific needs

# Test the migration
echo "🧪 Testing unified workflow..."
gh workflow run unified-cicd.yml --ref feature/unified-cicd-migration

echo "✅ Migration preparation complete!"
echo "Next steps:"
echo "1. Test the unified workflow thoroughly"
echo "2. Update branch protection rules"
echo "3. Update documentation"
echo "4. Remove legacy workflows"
```

#### 4.2 Gradual Cutover Strategy

Implement a feature flag approach:

```yaml
# In your application code or deployment config
features:
  use_unified_cicd: 
    development: true
    staging: true
    production: false  # Enable after validation
```

#### 4.3 Monitor Migration Progress

```bash
# Create monitoring dashboard
cat > migration-dashboard.json << EOF
{
  "title": "CI/CD Migration Dashboard",
  "widgets": [
    {
      "type": "metric",
      "title": "Workflow Success Rate",
      "query": "SELECT success_rate FROM workflow_runs WHERE workflow_name = 'unified-cicd'"
    },
    {
      "type": "metric", 
      "title": "Build Duration Comparison",
      "query": "SELECT avg(duration) FROM workflow_runs GROUP BY workflow_name"
    }
  ]
}
EOF
```

### Phase 5: Cleanup and Optimization (Week 7)

#### 5.1 Remove Legacy Workflows

```bash
# Archive old workflows
mkdir -p archived-workflows
git mv .github/workflows/legacy-*.yml archived-workflows/
git commit -m "Archive legacy CI/CD workflows"

# Remove completely after validation period
# git rm archived-workflows/
```

#### 5.2 Update Documentation

```bash
# Update README with new workflow information
cat >> README.md << EOF

## CI/CD Pipeline

This repository uses a unified CI/CD pipeline architecture. See [CI/CD Architecture](docs/CI_CD_ARCHITECTURE.md) for details.

### Quick Start

\`\`\`bash
# Trigger a build
git push origin main

# Manual deployment
gh workflow run unified-cicd.yml --ref main -f deployment-target=staging
\`\`\`
EOF
```

#### 5.3 Performance Optimization

```bash
# Analyze workflow performance
gh api repos/:owner/:repo/actions/runs \
  --paginate \
  --jq '.workflow_runs[] | select(.name == "unified-cicd") | {
    id: .id, 
    duration: (.updated_at - .created_at), 
    status: .status, 
    conclusion: .conclusion
  }' > workflow-performance.json

# Identify bottlenecks
python3 << EOF
import json
import datetime

with open('workflow-performance.json') as f:
    data = json.load(f)

# Analyze duration trends
durations = [item['duration'] for item in data if item['duration']]
avg_duration = sum(durations) / len(durations)
print(f"Average workflow duration: {avg_duration}")
EOF
```

## Rollback Plan

### Immediate Rollback (Emergency)

```bash
#!/bin/bash
# emergency-rollback.sh

echo "🚨 Emergency rollback initiated..."

# Disable unified workflow
git checkout main
git revert HEAD --no-edit

# Restore legacy workflows
cp -r workflow-backups/* .github/workflows/
git add .github/workflows/
git commit -m "Emergency rollback to legacy workflows"

# Force push to override
git push origin main --force

echo "✅ Emergency rollback complete!"
```

### Gradual Rollback (Planned)

```bash
#!/bin/bash
# planned-rollback.sh

echo "🔄 Planned rollback to legacy workflows..."

# Create rollback branch
git checkout -b rollback/legacy-cicd

# Restore specific workflows
git checkout workflow-backups -- legacy-deploy.yml legacy-test.yml

# Update to use legacy workflows
# (Modify configuration files as needed)

# Test rollback
gh workflow run legacy-deploy.yml --ref rollback/legacy-cicd

echo "✅ Planned rollback prepared!"
echo "Review and merge rollback/legacy-cicd branch when ready"
```

## Validation Checklist

### Pre-Migration
- [ ] All existing workflows documented
- [ ] OIDC authentication configured
- [ ] Repository secrets set up
- [ ] Environment protection rules enabled
- [ ] Backup of existing workflows created

### During Migration
- [ ] New workflows tested in development
- [ ] Security scanning validated
- [ ] Deployment processes verified
- [ ] Performance metrics compared
- [ ] Team training completed

### Post-Migration
- [ ] Legacy workflows removed
- [ ] Documentation updated
- [ ] Monitoring dashboards configured
- [ ] Incident response procedures updated
- [ ] Performance optimization completed

## Common Issues and Solutions

### Issue: Workflow Not Triggering
**Solution**: Check branch protection rules and workflow syntax
```bash
# Validate workflow syntax
gh api repos/:owner/:repo/actions/workflows/unified-cicd.yml \
  --jq '.path' \
  --method GET
```

### Issue: Permission Denied
**Solution**: Verify OIDC role configuration
```bash
# Test OIDC authentication
aws sts assume-role-with-web-identity \
  --role-arn $AWS_ROLE_ARN \
  --role-session-name test-session \
  --web-identity-token $GITHUB_TOKEN
```

### Issue: Test Failures
**Solution**: Compare test environments
```bash
# Check test configuration differences
diff legacy-test-config.yml unified-test-config.yml
```

## Support and Escalation

### Primary Contacts
- **Migration Lead**: [Team Lead Email]
- **DevOps Team**: [DevOps Email]
- **Security Team**: [Security Email]

### Escalation Path
1. **Level 1**: Team Lead (Business hours)
2. **Level 2**: DevOps Manager (24/7)
3. **Level 3**: Engineering Director (Critical issues)

### Emergency Procedures
- **Pipeline Failure**: Use emergency rollback script
- **Security Incident**: Contact security team immediately
- **Production Outage**: Follow incident response procedures

## Success Metrics

### Performance Metrics
- **Build Duration**: Target < 15 minutes for full pipeline
- **Success Rate**: Target > 95% success rate
- **Time to Deploy**: Target < 30 minutes to production

### Quality Metrics
- **Security Issues**: Zero high/critical vulnerabilities
- **Test Coverage**: Maintain or improve current coverage
- **Deployment Failures**: < 2% failure rate

### Team Metrics
- **Developer Satisfaction**: Survey after migration
- **Time Savings**: Measure reduction in workflow maintenance
- **Incident Reduction**: Track pre/post migration incidents

---

This migration guide provides a comprehensive approach to transitioning from legacy CI/CD workflows to the unified pipeline architecture. Follow the phases sequentially and validate each step before proceeding to the next.