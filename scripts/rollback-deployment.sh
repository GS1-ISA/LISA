#!/bin/bash
# Comprehensive Rollback Mechanism Script

set -euo pipefail

# Source helper functions
source "$(dirname "$0")/unified-cicd-helpers.sh"

# Configuration
ROLLBACK_HISTORY_DIR="rollback-history"
MAX_ROLLBACK_HISTORY=10
HEALTH_CHECK_TIMEOUT=300
HEALTH_CHECK_INTERVAL=10

# Initialize rollback history
init_rollback_history() {
    mkdir -p "$ROLLBACK_HISTORY_DIR"
    log_info "Initialized rollback history directory: $ROLLBACK_HISTORY_DIR"
}

# Create deployment snapshot
create_deployment_snapshot() {
    local deployment_name=$1
    local environment=$2
    local version=$3
    local snapshot_file="$ROLLBACK_HISTORY_DIR/${deployment_name}-${environment}-${version}-$(date +%Y%m%d-%H%M%S).json"
    
    log_info "Creating deployment snapshot for: $deployment_name ($environment) v$version"
    
    # Collect deployment information
    local snapshot_data=$(cat <<EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "deployment_name": "$deployment_name",
    "environment": "$environment",
    "version": "$version",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
    "docker_images": [],
    "kubernetes_manifests": [],
    "database_migrations": [],
    "configuration": {},
    "rollback_commands": []
}
EOF
)
    
    # Add Docker images information
    if command -v docker >/dev/null 2>&1; then
        local docker_images=$(docker ps --format "{{.Image}}" | sort -u | jq -R . | jq -s .)
        snapshot_data=$(echo "$snapshot_data" | jq --argjson images "$docker_images" '.docker_images = $images')
    fi
    
    # Add Kubernetes manifests if available
    if [[ -d "k8s" ]]; then
        local k8s_manifests=$(find k8s -name "*.yaml" -o -name "*.yml" 2>/dev/null | jq -R . | jq -s .)
        snapshot_data=$(echo "$snapshot_data" | jq --argjson manifests "$k8s_manifests" '.kubernetes_manifests = $manifests')
    fi
    
    # Save snapshot
    echo "$snapshot_data" > "$snapshot_file"
    
    # Maintain history limit
    maintain_rollback_history "$deployment_name" "$environment"
    
    log_success "Deployment snapshot created: $snapshot_file"
    echo "$snapshot_file"
}

# Maintain rollback history limit
maintain_rollback_history() {
    local deployment_name=$1
    local environment=$2
    
    local history_files=$(find "$ROLLBACK_HISTORY_DIR" -name "${deployment_name}-${environment}-*.json" | sort -r)
    local file_count=$(echo "$history_files" | wc -l)
    
    if [[ $file_count -gt $MAX_ROLLBACK_HISTORY ]]; then
        local files_to_remove=$((file_count - MAX_ROLLBACK_HISTORY))
        log_info "Removing $files_to_remove old rollback snapshots"
        
        echo "$history_files" | tail -n "$files_to_remove" | while read -r file; do
            rm -f "$file"
            log_info "Removed old snapshot: $file"
        done
    fi
}

# Kubernetes deployment rollback
rollback_kubernetes() {
    local deployment_name=$1
    local namespace=$2
    local target_revision=${3:-""}
    
    log_info "Rolling back Kubernetes deployment: $deployment_name in namespace: $namespace"
    
    # Get current revision
    local current_revision=$(kubectl rollout history deployment/"$deployment_name" -n "$namespace" | tail -2 | head -1 | awk '{print $1}')
    
    if [[ -n "$target_revision" ]]; then
        # Rollback to specific revision
        log_info "Rolling back to revision: $target_revision"
        kubectl rollout undo deployment/"$deployment_name" -n "$namespace" --to-revision="$target_revision"
    else
        # Rollback to previous revision
        log_info "Rolling back to previous revision"
        kubectl rollout undo deployment/"$deployment_name" -n "$namespace"
    fi
    
    # Wait for rollout to complete
    log_info "Waiting for rollout to complete"
    kubectl rollout status deployment/"$deployment_name" -n "$namespace" --timeout="${HEALTH_CHECK_TIMEOUT}s"
    
    # Verify rollback
    local new_revision=$(kubectl rollout history deployment/"$deployment_name" -n "$namespace" | tail -2 | head -1 | awk '{print $1}')
    
    if [[ "$new_revision" != "$current_revision" ]]; then
        log_success "Kubernetes rollback completed successfully"
        log_info "New revision: $new_revision"
        return 0
    else
        log_error "Kubernetes rollback failed - revision unchanged"
        return 1
    fi
}

# Docker container rollback
rollback_docker() {
    local container_name=$1
    local previous_image=$2
    local docker_compose_file=${3:-""}
    
    log_info "Rolling back Docker container: $container_name to image: $previous_image"
    
    if [[ -n "$docker_compose_file" ]] && [[ -f "$docker_compose_file" ]]; then
        # Update docker-compose file
        sed -i.bak "s|image:.*$container_name.*|image: $previous_image|g" "$docker_compose_file"
        
        # Restart services
        docker-compose -f "$docker_compose_file" down
        docker-compose -f "$docker_compose_file" up -d
        
        log_success "Docker Compose rollback completed"
    else
        # Stop current container
        docker stop "$container_name" 2>/dev/null || true
        docker rm "$container_name" 2>/dev/null || true
        
        # Start with previous image
        docker run -d --name "$container_name" "$previous_image"
        
        log_success "Docker container rollback completed"
    fi
}

# Database rollback
rollback_database() {
    local database_type=$1
    local backup_file=$2
    local database_name=$3
    
    log_info "Rolling back database: $database_name from backup: $backup_file"
    
    case $database_type in
        "postgresql")
            # Restore PostgreSQL database
            dropdb --if-exists "$database_name"
            createdb "$database_name"
            pg_restore --dbname="$database_name" --verbose "$backup_file"
            ;;
        "mysql")
            # Restore MySQL database
            mysql -e "DROP DATABASE IF EXISTS $database_name; CREATE DATABASE $database_name;"
            mysql "$database_name" < "$backup_file"
            ;;
        "mongodb")
            # Restore MongoDB database
            mongorestore --drop --db="$database_name" "$backup_file"
            ;;
        *)
            log_error "Unsupported database type: $database_type"
            return 1
            ;;
    esac
    
    log_success "Database rollback completed"
}

# Configuration rollback
rollback_configuration() {
    local config_file=$1
    local backup_config=$2
    
    log_info "Rolling back configuration: $config_file from backup: $backup_config"
    
    if [[ -f "$backup_config" ]]; then
        cp "$backup_config" "$config_file"
        log_success "Configuration rollback completed"
    else
        log_error "Backup configuration file not found: $backup_config"
        return 1
    fi
}

# Blue-green deployment rollback
rollback_blue_green() {
    local environment=$1
    local service_name=$2
    
    log_info "Performing blue-green rollback for service: $service_name in environment: $environment"
    
    # Get current color
    local current_color=$(kubectl get service "$service_name" -n "$environment" -o jsonpath='{.spec.selector.color}' 2>/dev/null || echo "blue")
    local target_color=$([[ "$current_color" == "blue" ]] && echo "green" || echo "blue")
    
    log_info "Switching from $current_color to $target_color"
    
    # Update service selector
    kubectl patch service "$service_name" -n "$environment" -p "{\"spec\":{\"selector\":{\"color\":\"$target_color\"}}}"
    
    # Verify service is working
    if check_service_health "$service_name" "$environment"; then
        log_success "Blue-green rollback completed - traffic switched to $target_color"
        
        # Scale down the old deployment
        local old_deployment="${service_name}-${current_color}"
        kubectl scale deployment/"$old_deployment" -n "$environment" --replicas=0
        
        return 0
    else
        log_error "Blue-green rollback failed - service health check failed"
        
        # Revert service selector
        kubectl patch service "$service_name" -n "$environment" -p "{\"spec\":{\"selector\":{\"color\":\"$current_color\"}}}"
        
        return 1
    fi
}

# Canary deployment rollback
rollback_canary() {
    local deployment_name=$1
    local namespace=$2
    local stable_replicas=$3
    
    log_info "Performing canary rollback for deployment: $deployment_name in namespace: $namespace"
    
    # Scale canary deployment to 0
    kubectl scale deployment/"${deployment_name}-canary" -n "$namespace" --replicas=0
    
    # Scale stable deployment to original replica count
    kubectl scale deployment/"${deployment_name}-stable" -n "$namespace" --replicas="$stable_replicas"
    
    # Update service to point only to stable deployment
    kubectl patch service "$deployment_name" -n "$namespace" -p '{"spec":{"selector":{"version":"stable"}}}'
    
    log_success "Canary rollback completed - traffic routed to stable deployment"
}

# Health check function
check_service_health() {
    local service_name=$1
    local namespace=$2
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1
    
    log_info "Performing health check for service: $service_name"
    
    while [[ $attempt -le $max_attempts ]]; do
        # Check if pods are ready
        local ready_pods=$(kubectl get pods -n "$namespace" -l "app=$service_name" --field-selector=status.phase=Running --no-headers | grep -c "Running" || echo "0")
        local total_pods=$(kubectl get pods -n "$namespace" -l "app=$service_name" --no-headers | wc -l)
        
        if [[ $ready_pods -eq $total_pods ]] && [[ $total_pods -gt 0 ]]; then
            log_success "Health check passed - all pods are ready"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts - $ready_pods/$total_pods pods ready"
        sleep "$HEALTH_CHECK_INTERVAL"
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Automated rollback trigger
trigger_rollback() {
    local deployment_name=$1
    local environment=$2
    local rollback_type=$3
    local failure_reason=$4
    
    log_warn "Triggering automated rollback due to: $failure_reason"
    
    # Create rollback record
    local rollback_record=$(cat <<EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "deployment_name": "$deployment_name",
    "environment": "$environment",
    "rollback_type": "$rollback_type",
    "failure_reason": "$failure_reason",
    "initiated_by": "automated_system"
}
EOF
)
    
    echo "$rollback_record" > "$ROLLBACK_HISTORY_DIR/rollback-trigger-$(date +%Y%m%d-%H%M%S).json"
    
    # Execute rollback based on type
    case $rollback_type in
        "kubernetes")
            rollback_kubernetes "$deployment_name" "$environment"
            ;;
        "docker")
            rollback_docker "$deployment_name" "$environment"
            ;;
        "blue-green")
            rollback_blue_green "$environment" "$deployment_name"
            ;;
        "canary")
            rollback_canary "$deployment_name" "$environment" "3"
            ;;
        *)
            log_error "Unknown rollback type: $rollback_type"
            return 1
            ;;
    esac
}

# List available rollback points
list_rollback_points() {
    local deployment_name=${1:-""}
    local environment=${2:-""}
    
    log_info "Listing available rollback points"
    
    local search_pattern="*.json"
    if [[ -n "$deployment_name" ]] && [[ -n "$environment" ]]; then
        search_pattern="${deployment_name}-${environment}-*.json"
    fi
    
    local snapshots=$(find "$ROLLBACK_HISTORY_DIR" -name "$search_pattern" | sort -r)
    
    if [[ -z "$snapshots" ]]; then
        log_info "No rollback snapshots found"
        return 0
    fi
    
    echo "Available rollback snapshots:"
    echo "$snapshots" | while read -r snapshot; do
        local basename=$(basename "$snapshot" .json)
        local timestamp=$(echo "$basename" | rev | cut -d'-' -f1-2 | rev)
        local version=$(echo "$basename" | rev | cut -d'-' -f3 | rev)
        local env=$(echo "$basename" | rev | cut -d'-' -f4 | rev)
        local name=$(echo "$basename" | sed "s/-${env}-${version}-${timestamp}$//")
        
        printf "%-30s %-10s %-10s %-20s\n" "$name" "$env" "$version" "$timestamp"
    done
}

# Main function
main() {
    local command=$1
    shift
    
    case $command in
        "init")
            init_rollback_history
            ;;
        "snapshot")
            create_deployment_snapshot "$@"
            ;;
        "kubernetes")
            rollback_kubernetes "$@"
            ;;
        "docker")
            rollback_docker "$@"
            ;;
        "database")
            rollback_database "$@"
            ;;
        "config")
            rollback_configuration "$@"
            ;;
        "blue-green")
            rollback_blue_green "$@"
            ;;
        "canary")
            rollback_canary "$@"
            ;;
        "trigger")
            trigger_rollback "$@"
            ;;
        "list")
            list_rollback_points "$@"
            ;;
        *)
            echo "Usage: $0 {init|snapshot|kubernetes|docker|database|config|blue-green|canary|trigger|list} [parameters...]"
            echo ""
            echo "Examples:"
            echo "  $0 init"
            echo "  $0 snapshot my-app production 1.2.3"
            echo "  $0 kubernetes my-app-namespace production"
            echo "  $0 docker my-app previous-image:latest docker-compose.yml"
            echo "  $0 database postgresql backup.sql mydb"
            echo "  $0 blue-green production my-service"
            echo "  $0 trigger my-app production kubernetes 'Health check failed'"
            echo "  $0 list my-app production"
            exit 1
            ;;
    esac
}

# Main entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 {command} [parameters...]"
        exit 1
    fi
    
    main "$@"
fi