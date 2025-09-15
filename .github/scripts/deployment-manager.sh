#!/bin/bash
set -euo pipefail

# Comprehensive Deployment Management Script
# Usage: ./deployment-manager.sh <action> <environment> <service> [version]

ACTION=$1
ENVIRONMENT=$2
SERVICE=$3
VERSION=${4:-$(git rev-parse --short HEAD)}
CONFIG_FILE=".github/workflows/config/ci-cd-config.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

log_deploy() {
    echo -e "${PURPLE}[DEPLOY]${NC} $1"
}

# Error handling
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Error occurred on line $line_number with exit code $error_code"
    exit $error_code
}

trap 'handle_error $LINENO $?' ERR

# Deployment configuration
DEPLOYMENT_DIR="/tmp/deployments"
DEPLOYMENT_LOG="$DEPLOYMENT_DIR/deployment.log"
DEPLOYMENT_STATE_FILE="$DEPLOYMENT_DIR/deployment-state.json"
ROLLBACK_HISTORY_FILE="$DEPLOYMENT_DIR/rollback-history.json"
MAX_ROLLBACK_HISTORY=10

# Initialize deployment directory
init_deployment() {
    mkdir -p "$DEPLOYMENT_DIR"
    
    # Initialize state file if it doesn't exist
    if [[ ! -f "$DEPLOYMENT_STATE_FILE" ]]; then
        echo '{}' > "$DEPLOYMENT_STATE_FILE"
    fi
    
    # Initialize rollback history file if it doesn't exist
    if [[ ! -f "$ROLLBACK_HISTORY_FILE" ]]; then
        echo '[]' > "$ROLLBACK_HISTORY_FILE"
    fi
}

# Get environment configuration
get_env_config() {
    local environment=$1
    local service=$2
    
    # This would typically read from a configuration file
    # For now, return default configurations
    case "$environment" in
        "development")
            echo '{"region": "us-east-1", "cluster": "dev-cluster", "namespace": "development", "replicas": 1, "resources": {"cpu": "100m", "memory": "128Mi"}}'
            ;;
        "staging")
            echo '{"region": "us-east-1", "cluster": "staging-cluster", "namespace": "staging", "replicas": 2, "resources": {"cpu": "200m", "memory": "256Mi"}}'
            ;;
        "production")
            echo '{"region": "us-east-1", "cluster": "prod-cluster", "namespace": "production", "replicas": 3, "resources": {"cpu": "500m", "memory": "512Mi"}}'
            ;;
        *)
            log_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
}

# Validate deployment prerequisites
validate_prerequisites() {
    local environment=$1
    local service=$2
    local version=$3
    
    log_info "Validating deployment prerequisites..."
    
    # Check if required tools are available
    local required_tools=("kubectl" "docker" "helm" "jq")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check if service configuration exists
    if [[ ! -f "k8s/$service/values-$environment.yaml" ]]; then
        log_error "Service configuration not found: k8s/$service/values-$environment.yaml"
        exit 1
    fi
    
    # Check if Docker image exists
    local image_tag="ghcr.io/${GITHUB_REPOSITORY}/${service}:${version}"
    if ! docker manifest inspect "$image_tag" >/dev/null 2>&1; then
        log_error "Docker image not found: $image_tag"
        exit 1
    fi
    
    # Check environment protection rules
    if ! check_environment_protection "$environment" "$service" "$version"; then
        log_error "Environment protection check failed"
        exit 1
    fi
    
    log_success "All prerequisites validated"
}

# Check environment protection rules
check_environment_protection() {
    local environment=$1
    local service=$2
    local version=$3
    
    log_info "Checking environment protection rules..."
    
    # Production environment requires additional checks
    if [[ "$environment" == "production" ]]; then
        # Check if deployment is during allowed hours (9 AM - 5 PM UTC, Monday-Friday)
        local current_hour=$(date -u +%H)
        local current_day=$(date -u +%u)
        
        if [[ $current_hour -lt 9 || $current_hour -gt 17 || $current_day -gt 5 ]]; then
            log_error "Production deployments are only allowed during business hours (9 AM - 5 PM UTC, Monday-Friday)"
            return 1
        fi
        
        # Check if version has been deployed to staging first
        if ! check_staging_deployment "$service" "$version"; then
            log_error "Version must be deployed to staging before production"
            return 1
        fi
        
        # Check if required approvals are in place
        if ! check_required_approvals "$environment" "$service"; then
            log_error "Required approvals not found for production deployment"
            return 1
        fi
    fi
    
    # Check if there are any active incidents
    if check_active_incidents "$environment" "$service"; then
        log_error "Cannot deploy during active incident"
        return 1
    fi
    
    log_success "Environment protection checks passed"
    return 0
}

# Check if version has been deployed to staging
check_staging_deployment() {
    local service=$1
    local version=$2
    
    log_info "Checking staging deployment for $service:$version"
    
    # Check deployment state
    local staging_state=$(jq -r ".staging.$service.current_version // \"\"" "$DEPLOYMENT_STATE_FILE")
    
    if [[ "$staging_state" == "$version" ]]; then
        log_success "Version found in staging: $version"
        return 0
    else
        log_warning "Version not found in staging. Current staging version: $staging_state"
        return 1
    fi
}

# Check required approvals
check_required_approvals() {
    local environment=$1
    local service=$2
    
    log_info "Checking required approvals for $environment/$service"
    
    # This would typically check against an approval system
    # For now, simulate approval check
    local approval_file="$DEPLOYMENT_DIR/approvals/${environment}_${service}.json"
    
    if [[ -f "$approval_file" ]]; then
        local approval_status=$(jq -r '.status' "$approval_file")
        local approval_timestamp=$(jq -r '.timestamp' "$approval_file")
        local approval_age_hours=$(( ($(date +%s) - $(date -d "$approval_timestamp" +%s)) / 3600 ))
        
        # Approvals expire after 24 hours
        if [[ "$approval_status" == "approved" && $approval_age_hours -lt 24 ]]; then
            log_success "Valid approval found"
            return 0
        fi
    fi
    
    log_warning "No valid approval found"
    return 1
}

# Check for active incidents
check_active_incidents() {
    local environment=$1
    local service=$2
    
    log_info "Checking for active incidents..."
    
    # This would typically check against an incident management system
    # For now, simulate incident check
    local incident_file="$DEPLOYMENT_DIR/incidents/${environment}_${service}.json"
    
    if [[ -f "$incident_file" ]]; then
        local incident_status=$(jq -r '.status' "$incident_file")
        if [[ "$incident_status" == "active" ]]; then
            log_warning "Active incident detected"
            return 0
        fi
    fi
    
    return 1
}

# Perform health check
perform_health_check() {
    local environment=$1
    local service=$2
    local timeout=${3:-300}
    
    log_info "Performing health check for $service in $environment..."
    
    local env_config=$(get_env_config "$environment" "$service")
    local namespace=$(echo "$env_config" | jq -r '.namespace')
    local start_time=$(date +%s)
    
    while [[ $(($(date +%s) - start_time)) -lt $timeout ]]; do
        # Check pod status
        local ready_pods=$(kubectl get pods -n "$namespace" -l "app=$service" -o json | \
                          jq '[.items[] | select(.status.phase == "Running" and ([.status.conditions[] | select(.type == "Ready" and .status == "True")] | length > 0))] | length')
        
        local total_pods=$(kubectl get pods -n "$namespace" -l "app=$service" -o json | jq '.items | length')
        
        if [[ $ready_pods -eq $total_pods && $total_pods -gt 0 ]]; then
            log_success "Health check passed: $ready_pods/$total_pods pods ready"
            return 0
        fi
        
        log_info "Waiting for pods to be ready: $ready_pods/$total_pods"
        sleep 10
    done
    
    log_error "Health check timed out after $timeout seconds"
    return 1
}

# Deploy service
deploy_service() {
    local environment=$1
    local service=$2
    local version=$3
    
    log_deploy "Starting deployment of $service:$version to $environment"
    
    # Get environment configuration
    local env_config=$(get_env_config "$environment" "$service")
    local namespace=$(echo "$env_config" | jq -r '.namespace')
    local replicas=$(echo "$env_config" | jq -r '.replicas')
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Update Helm values
    local values_file="k8s/$service/values-$environment.yaml"
    local temp_values_file=$(mktemp)
    
    # Merge base values with environment-specific values
    if [[ -f "k8s/$service/values.yaml" ]]; then
        yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
            "k8s/$service/values.yaml" "$values_file" > "$temp_values_file"
    else
        cp "$values_file" "$temp_values_file"
    fi
    
    # Update image tag
    yq eval ".image.tag = \"$version\"" -i "$temp_values_file"
    
    # Update replica count
    yq eval ".replicaCount = $replicas" -i "$temp_values_file"
    
    # Deploy using Helm
    local release_name="${service}-${environment}"
    local chart_path="k8s/$service"
    
    log_info "Deploying with Helm: $release_name"
    
    if helm upgrade --install "$release_name" "$chart_path" \
        --namespace "$namespace" \
        --values "$temp_values_file" \
        --set "image.tag=$version" \
        --wait --timeout=10m; then
        
        log_success "Helm deployment completed successfully"
        
        # Clean up temporary values file
        rm -f "$temp_values_file"
        
        return 0
    else
        log_error "Helm deployment failed"
        rm -f "$temp_values_file"
        return 1
    fi
}

# Update deployment state
update_deployment_state() {
    local environment=$1
    local service=$2
    local version=$3
    local status=$4
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    log_info "Updating deployment state: $environment/$service:$version ($status)"
    
    # Update current state
    jq --arg env "$environment" \
       --arg service "$service" \
       --arg version "$version" \
       --arg status "$status" \
       --arg timestamp "$timestamp" \
       '.[$env][$service] = {
         "current_version": $version,
         "status": $status,
         "last_updated": $timestamp,
         "deployment_count": ((.[$env][$service].deployment_count // 0) + 1)
       }' "$DEPLOYMENT_STATE_FILE" > "$DEPLOYMENT_STATE_FILE.tmp" && mv "$DEPLOYMENT_STATE_FILE.tmp" "$DEPLOYMENT_STATE_FILE"
    
    # Add to rollback history if deployment was successful
    if [[ "$status" == "deployed" ]]; then
        add_to_rollback_history "$environment" "$service" "$version"
    fi
}

# Add to rollback history
add_to_rollback_history() {
    local environment=$1
    local service=$2
    local version=$3
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    log_info "Adding to rollback history: $environment/$service:$version"
    
    # Add new entry to history
    jq --arg env "$environment" \
       --arg service "$service" \
       --arg version "$version" \
       --arg timestamp "$timestamp" \
       '. += [{
         "environment": $env,
         "service": $service,
         "version": $version,
         "timestamp": $timestamp
       }] | sort_by(.timestamp) | reverse | .[0:'$MAX_ROLLBACK_HISTORY']' "$ROLLBACK_HISTORY_FILE" > "$ROLLBACK_HISTORY_FILE.tmp" && mv "$ROLLBACK_HISTORY_FILE.tmp" "$ROLLBACK_HISTORY_FILE"
}

# Get previous version for rollback
get_previous_version() {
    local environment=$1
    local service=$2
    
    log_info "Getting previous version for rollback: $environment/$service"
    
    # Get the most recent successful deployment from history
    local previous_version=$(jq -r '[.[] | select(.environment == "'$environment'" and .service == "'$service'")] | .[1].version // ""' "$ROLLBACK_HISTORY_FILE")
    
    if [[ -n "$previous_version" ]]; then
        log_success "Previous version found: $previous_version"
        echo "$previous_version"
        return 0
    else
        log_error "No previous version found for rollback"
        return 1
    fi
}

# Rollback deployment
rollback_deployment() {
    local environment=$1
    local service=$2
    
    log_deploy "Starting rollback for $service in $environment"
    
    # Get previous version
    local previous_version
    if ! previous_version=$(get_previous_version "$environment" "$service"); then
        log_error "Cannot rollback: no previous version found"
        return 1
    fi
    
    # Get current version for logging
    local current_version=$(jq -r ".${environment}.${service}.current_version // \"\"" "$DEPLOYMENT_STATE_FILE")
    
    log_info "Rolling back from $current_version to $previous_version"
    
    # Deploy previous version
    if deploy_service "$environment" "$service" "$previous_version"; then
        # Perform health check
        if perform_health_check "$environment" "$service"; then
            log_success "Rollback completed successfully"
            update_deployment_state "$environment" "$service" "$previous_version" "rolled_back"
            return 0
        else
            log_error "Health check failed after rollback"
            return 1
        fi
    else
        log_error "Rollback deployment failed"
        return 1
    fi
}

# Generate deployment report
generate_deployment_report() {
    local environment=$1
    local service=$2
    local version=$3
    local status=$4
    
    log_info "Generating deployment report..."
    
    local report_file="$DEPLOYMENT_DIR/reports/${environment}_${service}_${version}_$(date +%Y%m%d_%H%M%S).json"
    mkdir -p "$(dirname "$report_file")"
    
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local commit_info=$(git log -1 --pretty=format:'{"sha": "%H", "message": "%s", "author": "%an", "date": "%ai"}' 2>/dev/null || echo '{}')
    
    cat > "$report_file" <<EOF
{
  "deployment_id": "$(uuidgen 2>/dev/null || echo "$(date +%s)")",
  "timestamp": "$timestamp",
  "repository": "${GITHUB_REPOSITORY:-unknown}",
  "environment": "$environment",
  "service": "$service",
  "version": "$version",
  "status": "$status",
  "commit": $commit_info,
  "deployment_duration": "$(calculate_deployment_duration)",
  "health_check_result": "$(get_health_check_result)",
  "rollback_available": $(check_rollback_available "$environment" "$service"),
  "metadata": {
    "triggered_by": "${GITHUB_ACTOR:-unknown}",
    "workflow_run_id": "${GITHUB_RUN_ID:-unknown}",
    "deployment_strategy": "rolling_update"
  }
}
EOF
    
    log_success "Deployment report generated: $report_file"
}

# Calculate deployment duration
calculate_deployment_duration() {
    # This would track actual deployment time
    # For now, return placeholder
    echo "5m30s"
}

# Get health check result
get_health_check_result() {
    # This would return actual health check result
    # For now, return placeholder
    echo "passed"
}

# Check if rollback is available
check_rollback_available() {
    local environment=$1
    local service=$2
    
    local previous_version
    if previous_version=$(get_previous_version "$environment" "$service" 2>/dev/null); then
        echo "true"
    else
        echo "false"
    fi
}

# Main deployment process
deploy() {
    local environment=$1
    local service=$2
    local version=$3
    
    log_deploy "Starting deployment process for $service:$version to $environment"
    
    # Validate prerequisites
    validate_prerequisites "$environment" "$service" "$version"
    
    # Update deployment state to "deploying"
    update_deployment_state "$environment" "$service" "$version" "deploying"
    
    # Perform deployment
    if deploy_service "$environment" "$service" "$version"; then
        # Perform health check
        if perform_health_check "$environment" "$service"; then
            log_success "Deployment completed successfully"
            update_deployment_state "$environment" "$service" "$version" "deployed"
            generate_deployment_report "$environment" "$service" "$version" "success"
            return 0
        else
            log_error "Health check failed, initiating rollback"
            rollback_deployment "$environment" "$service"
            generate_deployment_report "$environment" "$service" "$version" "failed_health_check"
            return 1
        fi
    else
        log_error "Deployment failed"
        update_deployment_state "$environment" "$service" "$version" "failed"
        generate_deployment_report "$environment" "$service" "$version" "failed_deployment"
        return 1
    fi
}

# Show deployment status
show_status() {
    local environment=${1:-""}
    local service=${2:-""}
    
    log_info "Deployment Status:"
    echo "==================="
    
    if [[ -n "$environment" && -n "$service" ]]; then
        # Show specific service status
        local status=$(jq -r ".${environment}.${service} // {}" "$DEPLOYMENT_STATE_FILE")
        if [[ "$status" != "{}" ]]; then
            echo "Environment: $environment"
            echo "Service: $service"
            echo "Current Version: $(echo "$status" | jq -r '.current_version // "unknown"')"
            echo "Status: $(echo "$status" | jq -r '.status // "unknown"')"
            echo "Last Updated: $(echo "$status" | jq -r '.last_updated // "unknown"')"
            echo "Deployment Count: $(echo "$status" | jq -r '.deployment_count // 0')"
        else
            log_warning "No deployment information found for $environment/$service"
        fi
    elif [[ -n "$environment" ]]; then
        # Show all services in environment
        local env_state=$(jq -r ".${environment} // {}" "$DEPLOYMENT_STATE_FILE")
        if [[ "$env_state" != "{}" ]]; then
            echo "Environment: $environment"
            echo ""
            echo "Service | Version | Status | Last Updated"
            echo "=================================="
            echo "$env_state" | jq -r 'to_entries[] | "\(.key) | \(.value.current_version) | \(.value.status) | \(.value.last_updated)"' | column -t -s '|'
        else
            log_warning "No deployment information found for environment: $environment"
        fi
    else
        # Show all environments
        echo "All Environments:"
        echo ""
        jq -r 'to_entries[] | "\(.key): \(.value | length) services"' "$DEPLOYMENT_STATE_FILE"
    fi
}

# Show rollback history
show_rollback_history() {
    local environment=${1:-""}
    local service=${2:-""}
    
    log_info "Rollback History:"
    echo "=================="
    
    local filter=""
    if [[ -n "$environment" ]]; then
        filter=" | select(.environment == \"$environment\")"
        if [[ -n "$service" ]]; then
            filter="$filter | select(.service == \"$service\")"
        fi
    fi
    
    if [[ -n "$filter" ]]; then
        jq -r ".[] $filter | \"\\(.environment)/\\(.service): \\(.version) (\\(.timestamp))\"" "$ROLLBACK_HISTORY_FILE" | head -10
    else
        jq -r '.[] | "\(.environment)/\(.service): \(.version) (\(.timestamp))"' "$ROLLBACK_HISTORY_FILE" | head -20
    fi
}

# Main execution
main() {
    log_info "Starting deployment manager: $ACTION"
    
    # Initialize deployment
    init_deployment
    
    case "$ACTION" in
        "deploy")
            deploy "$ENVIRONMENT" "$SERVICE" "$VERSION"
            ;;
            
        "rollback")
            rollback_deployment "$ENVIRONMENT" "$SERVICE"
            ;;
            
        "status")
            show_status "$ENVIRONMENT" "$SERVICE"
            ;;
            
        "history")
            show_rollback_history "$ENVIRONMENT" "$SERVICE"
            ;;
            
        "validate")
            validate_prerequisites "$ENVIRONMENT" "$SERVICE" "$VERSION"
            ;;
            
        *)
            log_error "Unknown action: $ACTION"
            echo "Usage: $0 <deploy|rollback|status|history|validate> <environment> <service> [version]"
            exit 1
            ;;
    esac
    
    log_success "Deployment manager completed successfully"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi