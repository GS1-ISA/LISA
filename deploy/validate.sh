#!/bin/bash

# ISA SuperApp Deployment Validation Script
# This script validates the deployment setup and configuration

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validation results
VALIDATION_PASSED=0
VALIDATION_FAILED=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((VALIDATION_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((VALIDATION_FAILED++))
}

# Validate file existence
validate_files() {
    log_info "Validating file structure..."

    local files=(
        "helm/isa-superapp/Chart.yaml"
        "helm/isa-superapp/values.yaml"
        "helm/isa-superapp/templates/_helpers.tpl"
        "helm/isa-superapp/templates/deployment.yaml"
        "helm/isa-superapp/templates/service.yaml"
        "helm/isa-superapp/templates/hpa.yaml"
        "helm/isa-superapp/templates/ingress.yaml"
        "k8s/namespace.yaml"
        "k8s/rbac.yaml"
        "k8s/configmap.yaml"
        "k8s/secrets.yaml"
        "k8s/postgresql-deployment.yaml"
        "k8s/redis-deployment.yaml"
        "k8s/neo4j-deployment.yaml"
        "k8s/deployment.yaml"
        "k8s/frontend-deployment.yaml"
        "k8s/ingress.yaml"
        "k8s/monitoring-deployment.yaml"
        "k8s/hpa.yaml"
        "k8s/network-policy.yaml"
        ".github/workflows/production-cicd.yml"
        ".github/workflows/reusable-security-scan.yml"
        ".github/dependency-review-config.yml"
        "deploy/production-values.yaml"
        "deploy/staging-values.yaml"
        "deploy/deploy.sh"
        "deploy/README.md"
    )

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            log_success "✓ $file exists"
        else
            log_error "✗ $file missing"
        fi
    done
}

# Validate YAML syntax
validate_yaml() {
    log_info "Validating YAML syntax..."

    local yaml_files=(
        "helm/isa-superapp/Chart.yaml"
        "helm/isa-superapp/values.yaml"
        "deploy/production-values.yaml"
        "deploy/staging-values.yaml"
        "k8s/namespace.yaml"
        "k8s/rbac.yaml"
        "k8s/configmap.yaml"
        "k8s/secrets.yaml"
    )

    for file in "${yaml_files[@]}"; do
        if [ -f "$file" ]; then
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                log_success "✓ $file has valid YAML syntax"
            else
                log_error "✗ $file has invalid YAML syntax"
            fi
        fi
    done
}

# Validate Helm chart
validate_helm() {
    log_info "Validating Helm chart..."

    if command -v helm &> /dev/null; then
        cd "$PROJECT_ROOT/helm/isa-superapp"
        if helm template . --dry-run >/dev/null 2>&1; then
            log_success "✓ Helm chart template validation passed"
        else
            log_error "✗ Helm chart template validation failed"
        fi
        cd "$PROJECT_ROOT"
    else
        log_warning "Helm not installed, skipping chart validation"
    fi
}

# Validate GitHub Actions workflows
validate_workflows() {
    log_info "Validating GitHub Actions workflows..."

    local workflow_files=(
        ".github/workflows/production-cicd.yml"
        ".github/workflows/reusable-security-scan.yml"
    )

    for file in "${workflow_files[@]}"; do
        if [ -f "$file" ]; then
            # Basic YAML validation for workflows
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                log_success "✓ $file has valid YAML syntax"
            else
                log_error "✗ $file has invalid YAML syntax"
            fi
        fi
    done
}

# Validate deployment script
validate_scripts() {
    log_info "Validating deployment scripts..."

    if [ -x "deploy/deploy.sh" ]; then
        log_success "✓ deploy/deploy.sh is executable"
    else
        log_error "✗ deploy/deploy.sh is not executable"
    fi

    if [ -x "deploy/validate.sh" ]; then
        log_success "✓ deploy/validate.sh is executable"
    else
        log_error "✗ deploy/validate.sh is not executable"
    fi
}

# Validate security configurations
validate_security() {
    log_info "Validating security configurations..."

    # Check for security headers in ingress
    if grep -q "X-Frame-Options" k8s/ingress.yaml; then
        log_success "✓ Security headers configured in ingress"
    else
        log_error "✗ Security headers missing in ingress"
    fi

    # Check for network policies
    if [ -f "k8s/network-policy.yaml" ]; then
        log_success "✓ Network policies configured"
    else
        log_error "✗ Network policies missing"
    fi

    # Check for RBAC
    if [ -f "k8s/rbac.yaml" ]; then
        log_success "✓ RBAC configuration present"
    else
        log_error "✗ RBAC configuration missing"
    fi
}

# Validate monitoring setup
validate_monitoring() {
    log_info "Validating monitoring setup..."

    if grep -q "prometheus.io/scrape" k8s/deployment.yaml; then
        log_success "✓ Prometheus scraping configured"
    else
        log_error "✗ Prometheus scraping not configured"
    fi

    if [ -f "k8s/monitoring-deployment.yaml" ]; then
        log_success "✓ Monitoring deployment configured"
    else
        log_error "✗ Monitoring deployment missing"
    fi
}

# Validate autoscaling
validate_autoscaling() {
    log_info "Validating autoscaling configuration..."

    if [ -f "k8s/hpa.yaml" ]; then
        log_success "✓ Horizontal Pod Autoscaler configured"
    else
        log_error "✗ Horizontal Pod Autoscaler missing"
    fi

    if grep -q "autoscaling" helm/isa-superapp/values.yaml; then
        log_success "✓ Autoscaling enabled in Helm values"
    else
        log_error "✗ Autoscaling not enabled in Helm values"
    fi
}

# Generate validation report
generate_report() {
    log_info "Generating validation report..."

    echo ""
    echo "========================================"
    echo "ISA SuperApp Deployment Validation Report"
    echo "========================================"
    echo "Timestamp: $(date)"
    echo "Total validations: $((VALIDATION_PASSED + VALIDATION_FAILED))"
    echo "Passed: $VALIDATION_PASSED"
    echo "Failed: $VALIDATION_FAILED"
    echo ""

    if [ $VALIDATION_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All validations passed!${NC}"
        echo "The deployment setup is ready for production."
    else
        echo -e "${RED}✗ $VALIDATION_FAILED validation(s) failed.${NC}"
        echo "Please address the failed validations before proceeding."
        exit 1
    fi

    echo ""
    echo "Next steps:"
    echo "1. Set up AWS infrastructure (EKS, ECR, etc.)"
    echo "2. Configure AWS Secrets Manager"
    echo "3. Update image repository URLs in values files"
    echo "4. Run: ./deploy/deploy.sh deploy staging"
    echo "5. Test the staging deployment"
    echo "6. Run: ./deploy/deploy.sh deploy production"
}

# Main validation function
main() {
    log_info "Starting ISA SuperApp deployment validation..."

    validate_files
    echo ""
    validate_yaml
    echo ""
    validate_helm
    echo ""
    validate_workflows
    echo ""
    validate_scripts
    echo ""
    validate_security
    echo ""
    validate_monitoring
    echo ""
    validate_autoscaling
    echo ""

    generate_report
}

# Run main validation
main "$@"