#!/bin/bash

# Unified Deployment Script
# This script handles deployment to different environments with various strategies

set -euo pipefail

# Default values
ENVIRONMENT="development"
IMAGE_TAG="latest"
DEPLOYMENT_STRATEGY="rolling"
DEPLOYMENT_ID=""
CONFIG_FILE="config/deployment-config.yaml"
DRY_RUN="false"
VERBOSE="false"
COMPOSE_FILE="docker-compose.yml"

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

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Unified deployment script for Docker-based applications

OPTIONS:
    -e, --environment ENV       Target environment (development, staging, production)
    -t, --image-tag TAG         Docker image tag to deploy
    -s, --strategy STRATEGY     Deployment strategy (rolling, blue-green, canary, recreate)
    -d, --deployment-id ID      Unique deployment identifier
    -c, --config-file FILE      Configuration file path
    -f, --compose-file FILE     Docker Compose file path
    --dry-run                   Perform a dry run without actual deployment
    --verbose                   Enable verbose output
    -h, --help                  Show this help message

EXAMPLES:
    $0 --environment staging --image-tag v1.2.3 --strategy rolling
    $0 -e production -t latest -s blue-green --dry-run
    $0 --environment development --verbose
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -s|--strategy)
                DEPLOYMENT_STRATEGY="$2"
                shift 2
                ;;
            -d|--deployment-id)
                DEPLOYMENT_ID="$2"
                shift 2
                ;;
            -c|--config-file)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -f|--compose-file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    log_info "Validating inputs..."
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be one of: development, staging, production"
        exit 1
    fi
    
    # Validate deployment strategy
    if [[ ! "$DEPLOYMENT_STRATEGY" =~ ^(rolling|blue-green|canary|recreate)$ ]]; then
        log_error "Invalid deployment strategy: $DEPLOYMENT_STRATEGY. Must be one of: rolling, blue-green, canary, recreate"
        exit 1
    fi
    
    # Validate config file exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Validate compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    # Generate deployment ID if not provided
    if [[ -z "$DEPLOYMENT_ID" ]]; then
        DEPLOYMENT_ID="$(date +%Y%m%d-%H%M%S)-${ENVIRONMENT}-${RANDOM}"
        log_info "Generated deployment ID: $DEPLOYMENT_ID"
    fi
    
    log_success "Input validation completed"
}

# Load configuration from YAML file
load_configuration() {
    log_info "Loading configuration from $CONFIG_FILE..."
    
    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        log_error "yq is required but not installed. Please install yq first."
        exit 1
    fi
    
    # Load environment-specific configuration
    local env_config
    env_config=$(yq eval ".environments.${ENVIRONMENT}" "$CONFIG_FILE")
    
    if [[ "$env_config" == "null" ]]; then
        log_error "Configuration for environment '$ENVIRONMENT' not found in $CONFIG_FILE"
        exit 1
    fi
    
    # Extract configuration values
    REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.resources.replicas" "$CONFIG_FILE")
    CPU=$(yq eval ".environments.${ENVIRONMENT}.resources.cpu" "$CONFIG_FILE")
    MEMORY=$(yq eval ".environments.${ENVIRONMENT}.resources.memory" "$CONFIG_FILE")
    STORAGE=$(yq eval ".environments.${ENVIRONMENT}.resources.storage" "$CONFIG_FILE")
    
    MIN_REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.scaling.min_replicas" "$CONFIG_FILE")
    MAX_REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.scaling.max_replicas" "$CONFIG_FILE")
    TARGET_CPU_UTILIZATION=$(yq eval ".environments.${ENVIRONMENT}.scaling.target_cpu_utilization" "$CONFIG_FILE")
    TARGET_MEMORY_UTILIZATION=$(yq eval ".environments.${ENVIRONMENT}.scaling.target_memory_utilization" "$CONFIG_FILE")
    
    HEALTH_CHECK_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.health_checks.enabled" "$CONFIG_FILE")
    HEALTH_CHECK_PATH=$(yq eval ".environments.${ENVIRONMENT}.health_checks.path" "$CONFIG_FILE")
    HEALTH_CHECK_INTERVAL=$(yq eval ".environments.${ENVIRONMENT}.health_checks.interval" "$CONFIG_FILE")
    HEALTH_CHECK_TIMEOUT=$(yq eval ".environments.${ENVIRONMENT}.health_checks.timeout" "$CONFIG_FILE")
    HEALTH_CHECK_RETRIES=$(yq eval ".environments.${ENVIRONMENT}.health_checks.retries" "$CONFIG_FILE")
    HEALTH_CHECK_START_PERIOD=$(yq eval ".environments.${ENVIRONMENT}.health_checks.start_period" "$CONFIG_FILE")
    
    ENV_VARS=$(yq eval ".environments.${ENVIRONMENT}.env[]" "$CONFIG_FILE" | tr '\n' ' ')
    
    log_success "Configuration loaded successfully"
}

# Create environment-specific Docker Compose override
create_compose_override() {
    log_info "Creating Docker Compose override for $ENVIRONMENT..."
    
    cat > docker-compose.override.yml << EOF
# Auto-generated override for $ENVIRONMENT environment
# Deployment ID: $DEPLOYMENT_ID
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

services:
  app:
    image: ghcr.io/${GITHUB_REPOSITORY}:$IMAGE_TAG
    deploy:
      replicas: $REPLICAS
      resources:
        limits:
          cpus: '$CPU'
          memory: ${MEMORY}M
        reservations:
          cpus: '$CPU'
          memory: ${MEMORY}M
    environment:
      - ENVIRONMENT=$ENVIRONMENT
      - DEPLOYMENT_ID=$DEPLOYMENT_ID
      - LOG_LEVEL=$([ "$ENVIRONMENT" = "production" ] && echo "info" || echo "debug")
      $([ "$HEALTH_CHECK_ENABLED" = "true" ] && echo "- HEALTH_CHECK_PATH=$HEALTH_CHECK_PATH")
      $([ "$HEALTH_CHECK_ENABLED" = "true" ] && echo "- HEALTH_CHECK_INTERVAL=$HEALTH_CHECK_INTERVAL")
      $([ "$HEALTH_CHECK_ENABLED" = "true" ] && echo "- HEALTH_CHECK_TIMEOUT=$HEALTH_CHECK_TIMEOUT")
      $([ "$HEALTH_CHECK_ENABLED" = "true" ] && echo "- HEALTH_CHECK_RETRIES=$HEALTH_CHECK_RETRIES")
      $([ "$HEALTH_CHECK_ENABLED" = "true" ] && echo "- HEALTH_CHECK_START_PERIOD=$HEALTH_CHECK_START_PERIOD")
EOF

    # Add environment variables from config
    for env_var in $ENV_VARS; do
        echo "      - $env_var" >> docker-compose.override.yml
    done

    # Add health check configuration if enabled
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        cat >> docker-compose.override.yml << EOF
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080$HEALTH_CHECK_PATH"]
      interval: ${HEALTH_CHECK_INTERVAL}s
      timeout: ${HEALTH_CHECK_TIMEOUT}s
      retries: $HEALTH_CHECK_RETRIES
      start_period: ${HEALTH_CHECK_START_PERIOD}s
EOF
    fi

    log_success "Docker Compose override created"
}

# Rolling deployment strategy
deploy_rolling() {
    log_info "Executing rolling deployment strategy..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would execute: docker-compose up -d --no-deps --scale app=$REPLICAS app"
        return 0
    fi
    
    # Pull the new image
    log_info "Pulling new image: ghcr.io/${GITHUB_REPOSITORY}:$IMAGE_TAG"
    docker-compose pull app
    
    # Scale up new containers one by one
    for i in $(seq 1 $REPLICAS); do
        log_info "Deploying replica $i/$REPLICAS"
        docker-compose up -d --no-deps --scale app=$i app
        
        # Wait for health check if enabled
        if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
            wait_for_health_check
        else
            sleep 10  # Basic wait without health check
        fi
    done
    
    # Remove old containers
    docker-compose up -d --remove-orphans
    
    log_success "Rolling deployment completed"
}

# Blue-green deployment strategy
deploy_blue_green() {
    log_info "Executing blue-green deployment strategy..."
    
    local blue_service="app-blue"
    local green_service="app-green"
    local active_service inactive_service
    
    # Determine which service is currently active
    if docker-compose ps | grep -q "$blue_service"; then
        active_service="$blue_service"
        inactive_service="$green_service"
    else
        active_service="$green_service"
        inactive_service="$blue_service"
    fi
    
    log_info "Current active service: $active_service"
    log_info "Deploying to inactive service: $inactive_service"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would deploy to $inactive_service and switch traffic"
        return 0
    fi
    
    # Deploy to inactive service
    log_info "Deploying to $inactive_service"
    IMAGE_TAG=$IMAGE_TAG docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --no-deps --scale $inactive_service=$REPLICAS $inactive_service
    
    # Wait for health check if enabled
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check $inactive_service
    else
        sleep 30  # Wait longer for blue-green deployment
    fi
    
    # Switch traffic by updating the load balancer configuration
    log_info "Switching traffic from $active_service to $inactive_service"
    
    # Update nginx configuration (assuming nginx is used as load balancer)
    update_load_balancer_config $inactive_service
    
    # Wait a bit for the switch to take effect
    sleep 5
    
    # Stop the old service
    log_info "Stopping old service: $active_service"
    docker-compose stop $active_service
    docker-compose rm -f $active_service
    
    log_success "Blue-green deployment completed"
}

# Canary deployment strategy
deploy_canary() {
    log_info "Executing canary deployment strategy..."
    
    local canary_replicas=1
    local stable_replicas=$((REPLICAS - canary_replicas))
    
    if [[ $stable_replicas -lt 1 ]]; then
        stable_replicas=1
        canary_replicas=$((REPLICAS - 1))
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would deploy $canary_replicas canary replicas and $stable_replicas stable replicas"
        return 0
    fi
    
    # Deploy canary version
    log_info "Deploying canary version with $canary_replicas replicas"
    CANARY_VERSION=true IMAGE_TAG=$IMAGE_TAG docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --no-deps --scale app-canary=$canary_replicas app-canary
    
    # Wait for canary health check
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check app-canary
    else
        sleep 20
    fi
    
    # Monitor canary metrics (this would typically involve checking metrics/logs)
    log_info "Monitoring canary deployment for stability..."
    monitor_canary_health $canary_replicas
    
    # If canary is healthy, proceed with full deployment
    if [[ $? -eq 0 ]]; then
        log_info "Canary deployment is healthy, proceeding with full deployment"
        deploy_rolling
    else
        log_error "Canary deployment failed health checks, rolling back"
        rollback_canary
        exit 1
    fi
    
    log_success "Canary deployment completed"
}

# Recreate deployment strategy
deploy_recreate() {
    log_info "Executing recreate deployment strategy..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would stop all containers and recreate them"
        return 0
    fi
    
    # Stop all running containers
    log_info "Stopping all running containers"
    docker-compose down
    
    # Start with new configuration
    log_info "Starting containers with new configuration"
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    
    # Wait for health check if enabled
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check
    else
        sleep 15
    fi
    
    log_success "Recreate deployment completed"
}

# Wait for health check
wait_for_health_check() {
    local service="${1:-app}"
    local max_attempts=$HEALTH_CHECK_RETRIES
    local attempt=1
    
    log_info "Waiting for health check on service: $service"
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps $service | grep -q "healthy"; then
            log_success "Health check passed for $service"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, waiting..."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done
    
    log_error "Health check failed for $service after $max_attempts attempts"
    return 1
}

# Update load balancer configuration
update_load_balancer_config() {
    local new_service="$1"
    
    log_info "Updating load balancer configuration to point to $new_service"
    
    # This is a placeholder - implement based on your load balancer
    # For nginx, you might update the upstream configuration
    if [[ -f "nginx.conf" ]]; then
        sed -i "s/app-blue\|app-green/$new_service/g" nginx.conf
        docker-compose exec nginx nginx -s reload
    fi
}

# Monitor canary health
monitor_canary_health() {
    local canary_replicas="$1"
    local monitoring_duration=300  # 5 minutes
    local check_interval=30
    
    log_info "Monitoring canary health for $monitoring_duration seconds..."
    
    local end_time=$(($(date +%s) + monitoring_duration))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check if canary containers are running
        local running_canaries
        running_canaries=$(docker-compose ps app-canary | grep -c "Up" || true)
        
        if [[ $running_canaries -ne $canary_replicas ]]; then
            log_error "Canary containers are not running properly"
            return 1
        fi
        
        # Check health status if enabled
        if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
            if ! docker-compose ps app-canary | grep -q "healthy"; then
                log_error "Canary containers are not healthy"
                return 1
            fi
        fi
        
        # Add more sophisticated monitoring here (error rates, response times, etc.)
        
        log_info "Canary health check passed, continuing monitoring..."
        sleep $check_interval
    done
    
    log_success "Canary monitoring completed successfully"
    return 0
}

# Rollback canary deployment
rollback_canary() {
    log_info "Rolling back canary deployment..."
    
    # Stop canary containers
    docker-compose stop app-canary
    docker-compose rm -f app-canary
    
    log_success "Canary rollback completed"
}

# Main deployment function
main() {
    log_info "Starting unified deployment script"
    log_info "Environment: $ENVIRONMENT"
    log_info "Image Tag: $IMAGE_TAG"
    log_info "Strategy: $DEPLOYMENT_STRATEGY"
    log_info "Deployment ID: $DEPLOYMENT_ID"
    log_info "Dry Run: $DRY_RUN"
    
    # Execute deployment based on strategy
    case $DEPLOYMENT_STRATEGY in
        rolling)
            deploy_rolling
            ;;
        blue-green)
            deploy_blue_green
            ;;
        canary)
            deploy_canary
            ;;
        recreate)
            deploy_recreate
            ;;
        *)
            log_error "Unknown deployment strategy: $DEPLOYMENT_STRATEGY"
            exit 1
            ;;
    esac
    
    # Cleanup
    if [[ -f "docker-compose.override.yml" ]]; then
        rm -f "docker-compose.override.yml"
    fi
    
    log_success "Deployment completed successfully"
}

# Error handling
trap 'log_error "Deployment failed on line $LINENO"; exit 1' ERR

# Script execution
parse_arguments "$@"
validate_inputs
load_configuration
create_compose_override
main

exit 0