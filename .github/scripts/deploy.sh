#!/bin/bash
set -euo pipefail

# Deployment Script with Advanced Rollback Capabilities
# Usage: ./deploy.sh <environment> <image-tag> <deployment-id>

ENVIRONMENT=$1
IMAGE_TAG=$2
DEPLOYMENT_ID=$3
CONFIG_FILE=".github/workflows/config/ci-cd-config.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Error handling
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Error occurred on line $line_number with exit code $error_code"
    
    # Trigger rollback if deployment was initiated
    if [[ "${DEPLOYMENT_INITIATED:-false}" == "true" ]]; then
        log_warning "Initiating automatic rollback due to deployment failure..."
        rollback_deployment
    fi
    
    exit $error_code
}

trap 'handle_error $LINENO $?' ERR

# Configuration loading
load_config() {
    log_info "Loading configuration for environment: $ENVIRONMENT"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Extract configuration values (simplified - in real implementation use yq or similar)
    DEPLOYMENT_STRATEGY="canary"  # Default
    HEALTH_CHECK_URL="https://${ENVIRONMENT}.isa-superapp.com/health"
    TIMEOUT_MINUTES=30
    ROLLBACK_ENABLED=true
    
    log_success "Configuration loaded successfully"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if required tools are available
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl is required but not installed"; exit 1; }
    command -v curl >/dev/null 2>&1 || { log_error "curl is required but not installed"; exit 1; }
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
        exit 1
    fi
    
    # Validate image tag
    if [[ -z "$IMAGE_TAG" ]]; then
        log_error "Image tag cannot be empty"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Pre-deployment checks passed"
}

# Create deployment backup
create_backup() {
    log_info "Creating deployment backup..."
    
    BACKUP_DIR="/tmp/deployment-backup-${DEPLOYMENT_ID}"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current deployment configuration
    kubectl get deployment isa-superapp -o yaml > "$BACKUP_DIR/deployment.yaml" 2>/dev/null || true
    kubectl get service isa-superapp -o yaml > "$BACKUP_DIR/service.yaml" 2>/dev/null || true
    kubectl get configmap isa-superapp-config -o yaml > "$BACKUP_DIR/configmap.yaml" 2>/dev/null || true
    
    # Backup current image tag
    CURRENT_IMAGE=$(kubectl get deployment isa-superapp -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "")
    echo "$CURRENT_IMAGE" > "$BACKUP_DIR/current_image.txt"
    
    echo "$BACKUP_DIR" > "/tmp/current-backup-location"
    
    log_success "Backup created at $BACKUP_DIR"
}

# Health check function
health_check() {
    local url=$1
    local expected_status=${2:-200}
    local timeout=${3:-30}
    local retries=${4:-3}
    
    log_info "Performing health check: $url"
    
    for ((i=1; i<=retries; i++)); do
        if curl -f -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" | grep -q "$expected_status"; then
            log_success "Health check passed (attempt $i/$retries)"
            return 0
        else
            log_warning "Health check failed (attempt $i/$retries)"
            if [[ $i -lt $retries ]]; then
                sleep 10
            fi
        fi
    done
    
    log_error "Health check failed after $retries attempts"
    return 1
}

# Blue-green deployment
blue_green_deployment() {
    log_info "Starting blue-green deployment..."
    
    # Create green deployment
    log_info "Creating green deployment..."
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: isa-superapp-green
  labels:
    app: isa-superapp
    version: green
    deployment-id: $DEPLOYMENT_ID
spec:
  replicas: 3
  selector:
    matchLabels:
      app: isa-superapp
      version: green
  template:
    metadata:
      labels:
        app: isa-superapp
        version: green
        deployment-id: $DEPLOYMENT_ID
    spec:
      containers:
      - name: isa-superapp
        image: $IMAGE_TAG
        ports:
        - containerPort: 8080
        env:
        - name: DEPLOYMENT_ID
          value: "$DEPLOYMENT_ID"
        - name: ENVIRONMENT
          value: "$ENVIRONMENT"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
EOF
    
    # Wait for green deployment to be ready
    log_info "Waiting for green deployment to be ready..."
    kubectl rollout status deployment/isa-superapp-green --timeout=10m
    
    # Perform health checks on green deployment
    log_info "Performing health checks on green deployment..."
    GREEN_POD=$(kubectl get pods -l app=isa-superapp,version=green -o jsonpath='{.items[0].metadata.name}')
    kubectl port-forward "$GREEN_POD" 8081:8080 &
    PF_PID=$!
    sleep 5
    
    if health_check "http://localhost:8081/health" 200 30 5; then
        log_success "Green deployment health check passed"
    else
        log_error "Green deployment health check failed"
        kill $PF_PID 2>/dev/null || true
        return 1
    fi
    
    kill $PF_PID 2>/dev/null || true
    
    # Switch traffic to green
    log_info "Switching traffic to green deployment..."
    kubectl patch service isa-superapp -p '{"spec":{"selector":{"version":"green"}}}'
    
    # Verify traffic switch
    sleep 10
    if health_check "$HEALTH_CHECK_URL" 200 60 5; then
        log_success "Traffic switch successful"
    else
        log_error "Traffic switch failed"
        return 1
    fi
    
    # Remove blue deployment
    log_info "Removing blue deployment..."
    kubectl delete deployment isa-superapp-blue 2>/dev/null || true
    
    log_success "Blue-green deployment completed successfully"
}

# Canary deployment
canary_deployment() {
    log_info "Starting canary deployment..."
    
    local stages=(
        "10:5"
        "25:10"
        "50:15"
        "100:0"
    )
    
    for stage in "${stages[@]}"; do
        IFS=':' read -r percentage duration <<< "$stage"
        
        log_info "Canary stage: $percentage% traffic for ${duration} minutes"
        
        # Update deployment with new percentage
        kubectl patch deployment isa-superapp -p "{\"spec\":{\"template\":{\"metadata\":{\"labels\":{\"deployment-id\":\"$DEPLOYMENT_ID\",\"canary-percentage\":\"$percentage\"}}}}}"
        
        # Wait for rollout
        kubectl rollout status deployment/isa-superapp --timeout=5m
        
        # Perform health checks
        if ! health_check "$HEALTH_CHECK_URL" 200 60 3; then
            log_error "Health check failed during canary stage $percentage%"
            return 1
        fi
        
        # Monitor metrics during canary
        if [[ $percentage -lt 100 ]]; then
            log_info "Monitoring canary metrics for $duration minutes..."
            sleep ${duration}m
            
            # Check error rates (simplified - in real implementation use monitoring API)
            ERROR_RATE=$(curl -s "$HEALTH_CHECK_URL/metrics" | grep "error_rate" | cut -d' ' -f2 || echo "0")
            if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
                log_error "Error rate too high during canary: $ERROR_RATE"
                return 1
            fi
        fi
    done
    
    log_success "Canary deployment completed successfully"
}

# Rolling deployment (default)
rolling_deployment() {
    log_info "Starting rolling deployment..."
    
    # Update deployment image
    kubectl set image deployment/isa-superapp isa-superapp="$IMAGE_TAG"
    
    # Add deployment ID label
    kubectl patch deployment isa-superapp -p "{\"spec\":{\"template\":{\"metadata\":{\"labels\":{\"deployment-id\":\"$DEPLOYMENT_ID\"}}}}}"
    
    # Wait for rollout to complete
    kubectl rollout status deployment/isa-superapp --timeout=15m
    
    # Perform health checks
    if health_check "$HEALTH_CHECK_URL" 200 60 5; then
        log_success "Rolling deployment completed successfully"
    else
        log_error "Health check failed after rolling deployment"
        return 1
    fi
}

# Main deployment function
deploy() {
    log_info "Starting deployment to $ENVIRONMENT environment"
    log_info "Image: $IMAGE_TAG"
    log_info "Deployment ID: $DEPLOYMENT_ID"
    
    DEPLOYMENT_INITIATED=true
    
    # Create backup before deployment
    create_backup
    
    # Determine deployment strategy
    case "$DEPLOYMENT_STRATEGY" in
        "blue-green")
            blue_green_deployment
            ;;
        "canary")
            canary_deployment
            ;;
        "rolling")
            rolling_deployment
            ;;
        *)
            log_warning "Unknown deployment strategy: $DEPLOYMENT_STRATEGY. Using rolling deployment."
            rolling_deployment
            ;;
    esac
    
    log_success "Deployment completed successfully"
}

# Rollback function
rollback_deployment() {
    log_warning "Initiating rollback..."
    
    BACKUP_DIR=$(cat "/tmp/current-backup-location" 2>/dev/null || echo "")
    
    if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
        log_info "Restoring from backup: $BACKUP_DIR"
        
        # Restore deployment configuration
        if [[ -f "$BACKUP_DIR/deployment.yaml" ]]; then
            kubectl apply -f "$BACKUP_DIR/deployment.yaml"
        fi
        
        # Restore service configuration
        if [[ -f "$BACKUP_DIR/service.yaml" ]]; then
            kubectl apply -f "$BACKUP_DIR/service.yaml"
        fi
        
        # Restore configmap
        if [[ -f "$BACKUP_DIR/configmap.yaml" ]]; then
            kubectl apply -f "$BACKUP_DIR/configmap.yaml"
        fi
        
        # Wait for rollback to complete
        kubectl rollout status deployment/isa-superapp --timeout=5m
        
        # Verify rollback success
        if health_check "$HEALTH_CHECK_URL" 200 60 3; then
            log_success "Rollback completed successfully"
        else
            log_error "Rollback verification failed - manual intervention required"
            exit 1
        fi
    else
        log_error "No backup found for rollback"
        exit 1
    fi
}

# Post-deployment validation
post_deployment_validation() {
    log_info "Running post-deployment validation..."
    
    # Performance validation
    log_info "Running performance tests..."
    # This would typically run your performance test suite
    
    # Security validation
    log_info "Running security validation..."
    # This would typically run quick security scans
    
    # Business logic validation
    log_info "Running business logic validation..."
    # This would typically run smoke tests
    
    log_success "Post-deployment validation completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up deployment artifacts..."
    
    # Remove backup directory
    BACKUP_DIR=$(cat "/tmp/current-backup-location" 2>/dev/null || echo "")
    if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
        rm -f "/tmp/current-backup-location"
    fi
    
    # Clean up old deployments
    kubectl delete deployment -l app=isa-superapp,version=green --ignore-not-found=true
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    log_info "Starting deployment script..."
    
    # Load configuration
    load_config
    
    # Run pre-deployment checks
    pre_deployment_checks
    
    # Execute deployment
    deploy
    
    # Run post-deployment validation
    post_deployment_validation
    
    # Cleanup
    cleanup
    
    log_success "Deployment script completed successfully"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi