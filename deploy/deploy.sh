#!/bin/bash

# ISA SuperApp Deployment Script
# This script handles deployment to different environments

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELM_CHART_PATH="$PROJECT_ROOT/helm/isa-superapp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install it first."
        exit 1
    fi

    # Check if aws cli is installed
    if ! command -v aws &> /dev/null; then
        log_error "aws CLI is not installed. Please install it first."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Setup AWS credentials and kubectl context
setup_aws() {
    local environment=$1
    local region=${2:-us-east-1}

    log_info "Setting up AWS credentials for $environment environment..."

    # Configure AWS credentials (assuming IAM roles or profiles are set up)
    export AWS_REGION=$region

    # Update kubectl context
    local cluster_name="isa-${environment}-cluster"
    aws eks update-kubeconfig --region $region --name $cluster_name

    log_success "AWS setup completed for $environment"
}

# Validate deployment
validate_deployment() {
    local environment=$1
    local namespace=${2:-"isa-superapp"}

    log_info "Validating deployment in $environment..."

    # Wait for deployments to be ready
    kubectl wait --for=condition=available --timeout=600s deployment/isa-superapp -n $namespace
    kubectl wait --for=condition=available --timeout=600s deployment/isa-frontend -n $namespace

    # Check pod status
    local unhealthy_pods=$(kubectl get pods -n $namespace --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{.items[*].metadata.name}')
    if [ ! -z "$unhealthy_pods" ]; then
        log_error "Found unhealthy pods: $unhealthy_pods"
        kubectl get pods -n $namespace
        exit 1
    fi

    log_success "Deployment validation passed"
}

# Deploy to environment
deploy() {
    local environment=$1
    local image_tag=${2:-latest}
    local values_file="$SCRIPT_DIR/${environment}-values.yaml"

    if [ ! -f "$values_file" ]; then
        log_error "Values file not found: $values_file"
        exit 1
    fi

    log_info "Deploying to $environment environment with image tag: $image_tag"

    # Setup AWS for the environment
    setup_aws $environment

    # Determine namespace
    local namespace="isa-superapp"
    if [ "$environment" = "staging" ]; then
        namespace="isa-superapp-staging"
    fi

    # Deploy using Helm
    helm upgrade --install isa-superapp $HELM_CHART_PATH \
        --namespace $namespace \
        --create-namespace \
        --values $values_file \
        --set isaSuperapp.image.tag=$image_tag \
        --set frontend.image.tag=$image_tag \
        --wait \
        --timeout=900s

    log_success "Deployment to $environment completed"

    # Validate deployment
    validate_deployment $environment $namespace
}

# Rollback deployment
rollback() {
    local environment=$1
    local revision=${2:-1}

    log_info "Rolling back $environment environment to revision $revision"

    setup_aws $environment

    local namespace="isa-superapp"
    if [ "$environment" = "staging" ]; then
        namespace="isa-superapp-staging"
    fi

    helm rollback isa-superapp $revision --namespace $namespace

    log_success "Rollback completed"
}

# Get deployment status
status() {
    local environment=$1

    setup_aws $environment

    local namespace="isa-superapp"
    if [ "$environment" = "staging" ]; then
        namespace="isa-superapp-staging"
    fi

    log_info "Deployment status for $environment:"

    echo "=== Helm Release Status ==="
    helm status isa-superapp --namespace $namespace

    echo ""
    echo "=== Pod Status ==="
    kubectl get pods -n $namespace

    echo ""
    echo "=== Service Status ==="
    kubectl get services -n $namespace

    echo ""
    echo "=== Ingress Status ==="
    kubectl get ingress -n $namespace
}

# Main script logic
main() {
    local command=$1
    local environment=$2
    local image_tag=$3

    case $command in
        deploy)
            if [ -z "$environment" ]; then
                log_error "Environment is required for deploy command"
                echo "Usage: $0 deploy <environment> [image-tag]"
                exit 1
            fi
            check_prerequisites
            deploy $environment $image_tag
            ;;
        rollback)
            if [ -z "$environment" ]; then
                log_error "Environment is required for rollback command"
                echo "Usage: $0 rollback <environment> [revision]"
                exit 1
            fi
            rollback $environment $image_tag
            ;;
        status)
            if [ -z "$environment" ]; then
                log_error "Environment is required for status command"
                echo "Usage: $0 status <environment>"
                exit 1
            fi
            status $environment
            ;;
        *)
            echo "ISA SuperApp Deployment Script"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  deploy <environment> [image-tag]    Deploy to specified environment"
            echo "  rollback <environment> [revision]   Rollback deployment"
            echo "  status <environment>                Show deployment status"
            echo ""
            echo "Environments:"
            echo "  staging                              Staging environment"
            echo "  production                           Production environment"
            echo ""
            echo "Examples:"
            echo "  $0 deploy staging v1.2.3"
            echo "  $0 deploy production"
            echo "  $0 rollback production 1"
            echo "  $0 status staging"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"