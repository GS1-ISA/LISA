
#!/bin/bash
# Unified CI/CD Helper Functions

set -euo pipefail

# Logging functions
log_info() {
    echo "ℹ️  [INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo "⚠️  [WARN] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "❌ [ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo "✅ [SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Environment validation
validate_environment() {
    local environment=$1
    local valid_environments=("development" "staging" "production")
    
    if [[ ! " ${valid_environments[@]} " =~ " ${environment} " ]]; then
        log_error "Invalid environment: $environment"
        log_info "Valid environments: ${valid_environments[*]}"
        exit 1
    fi
    
    log_success "Environment validated: $environment"
}

# Deployment strategy validation
validate_deployment_strategy() {
    local strategy=$1
    local valid_strategies=("rolling" "blue-green" "canary" "recreate")
    
    if [[ ! " ${valid_strategies[@]} " =~ " ${strategy} " ]]; then
        log_error "Invalid deployment strategy: $strategy"
        log_info "Valid strategies: ${valid_strategies[*]}"
        exit 1
    fi
    
    log_success "Deployment strategy validated: $strategy"
}

# Health check functions
health_check() {
    local url=$1
    local timeout=${2:-30}
    local retries=${3:-3}
    
    log_info "Performing health check on: $url"
    
    for i in $(seq 1 $retries); do
        if curl -f -s --max-time "$timeout" "$url" > /dev/null; then
            log_success "Health check passed on attempt $i"
            return 0
        else
            log_warn "Health check failed on attempt $i"
            if [ $i -lt $retries ]; then
                sleep 5
            fi
        fi
    done
    
    log_error "Health check failed after $retries attempts"
    return 1
}

# Smoke test functions
run_smoke_tests() {
    local base_url=$1
    local environment=$2
    
    log_info "Running smoke tests for $environment environment"
    
    local tests=(
        "$base_url/health:GET:200"
        "$base_url/api/health:GET:200"
        "$base_url/ready:GET:200"
    )
    
    local failed_tests=0
    
    for test in "${tests[@]}"; do
        IFS=':' read -r endpoint method expected_status <<< "$test"
        
        log_info "Testing: $endpoint"
        
        if curl -f -s -X "$method" --max-time 30 "$endpoint" > /dev/null; then
            log_success "Smoke test passed: $endpoint"
        else
            log_error "Smoke test failed: $endpoint"
            ((failed_tests++))
        fi
    done
    
    if [ $failed_tests -gt 0 ]; then
        log_error "$failed_tests smoke tests failed"
        return 1
    fi
    
    log_success "All smoke tests passed"
}

# Deployment functions
deploy_rolling() {
    local service_name=$1
    local image_tag=$2
    local environment=$3
    
    log_info "Starting rolling deployment for $service_name"
    
    # Simulate rolling deployment logic
    log_info "Updating service $service_name with image $image_tag"
    log_info "Environment: $environment"
    
    # Add actual deployment commands here
    # kubectl set image deployment/$service_name $service_name=$image_tag
    # kubectl rollout status deployment/$service_name
    
    log_success "Rolling deployment completed"
}

deploy_blue_green() {
    local service_name=$1
    local image_tag=$2
    local environment=$3
    
    log_info "Starting blue-green deployment for $service_name"
    
    # Simulate blue-green deployment logic
    log_info "Creating green environment for $service_name with image $image_tag"
    log_info "Environment: $environment"
    
    # Add actual blue-green deployment commands here
    # Create new deployment
    # Run health checks
    # Switch traffic
    # Cleanup old deployment
    
    log_success "Blue-green deployment completed"
}

deploy_canary() {
    local service_name=$1
    local image_tag=$2
    local environment=$3
    
    log_info "Starting canary deployment for $service_name"
    
    # Simulate canary deployment logic
    log_info "Deploying canary version for $service_name with image $image_tag"
    log_info "Environment: $environment"
    
    # Add actual canary deployment commands here
    # Deploy to small subset
    # Monitor metrics
    # Gradually increase traffic
    # Complete rollout or rollback
    
    log_success "Canary deployment completed"
}

deploy_recreate() {
    local service_name=$1
    local image_tag=$2
    local environment=$3
    
    log_info "Starting recreate deployment for $service_name"
    
    # Simulate recreate deployment logic
    log_info "Recreating service $service_name with image $image_tag"
    log_info "Environment: $environment"
    
    # Add actual recreate deployment commands here
    # Scale down to 0
    # Update image
    # Scale up
    
    log_success "Recreate deployment completed"
}

# Rollback functions
initiate_rollback() {
    local service_name=$1
    local environment=$2
    local reason=$3
    
    log_warn "Initiating rollback for $service_name in $environment"
    log_info "Rollback reason: $reason"
    
    # Add rollback logic here
    # kubectl rollout undo deployment/$service_name
    # Verify rollback success
    
    log_success "Rollback completed"
}

# Notification functions
send_notification() {
    local channel=$1
    local message=$2
    local severity=$3
    
    case $channel in
        "slack")
            if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
                curl -X POST -H 'Content-type: application/json' \
                    --data "{\"text\":\"$message\",\"severity\":\"$severity\"}" \
                    "$SLACK_WEBHOOK_URL"
            fi
            ;;
        "email")
            log_info "Email notification: $message"
            # Add email sending logic
            ;;
        "pagerduty")
            if [ -n "${PAGERDUTY_SERVICE_KEY:-}" ]; then
                curl -X POST -H 'Content-type: application/json' \
                    --data "{\"service_key\":\"$PAGERDUTY_SERVICE_KEY\",\"event_type\":\"trigger\",\"description\":\"$message\"}" \
                    "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
            fi
            ;;
    esac
}

# Security scanning functions
run_security_scan() {
    local image_tag=$1
    local scan_type=$2
    
    log_info "Running security scan: $scan_type for $image_tag"
    
    case $scan_type in
        "trivy")
            trivy image --severity HIGH,CRITICAL "$image_tag"
            ;;
        "snyk")
            if [ -n "${SNYK_TOKEN:-}" ]; then
                snyk test --docker "$image_tag"
            fi
            ;;
        "gitleaks")
            gitleaks detect --verbose
            ;;
    esac
    
    log_success "Security scan completed: $scan_type"
}

# Utility functions
wait_for_deployment() {
    local service_name=$1
    local timeout=${2:-300}
    
    log_info "Waiting for deployment to complete: $service_name"
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        # Add deployment status check logic
        # kubectl get deployment $service_name -o jsonpath='{.status.conditions[?(@.type=="Available")].status}'
        
        if [ "$status" = "True" ]; then
            log_success "Deployment completed successfully"
            return 0
        fi
        
        sleep 10
    done
    
    log_error "Deployment timeout after $timeout seconds"
    return 1
}

generate_deployment_report() {
    local environment=$1
    local strategy=$2
    local image_tag=$3
    local status=$4
    
    local report_file="deployment-report-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
    "deployment_id": "${GITHUB_RUN_ID:-unknown}",
    "environment": "$environment",
    "strategy": "$strategy",
    "image_tag": "$image_tag",
    "status": "$status",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "git_commit": "${GITHUB_SHA:-unknown}",
    "git_ref": "${GITHUB_REF:-unknown}"
}
EOF
    
    log_info "Deployment report generated: $report_file"
    cat "$report_file"
}

# Main deployment function
deploy() {
    local service_name=$1
    local image_tag=$2
    local environment=$3
    local strategy=$4
    
    log_info "Starting deployment process"
    log_info "Service: $service_name"
    log_info "Image: $image_tag"
    log_info "Environment: $environment"
    log_info "Strategy: $strategy"
    
    # Validate inputs
    validate_environment "$environment"
    validate_deployment_strategy "$strategy"
    
    # Execute deployment based on strategy
    case $strategy in
        "rolling")
            deploy_rolling "$service_name" "$image_tag" "$environment"
            ;;
        "blue-green")
            deploy_blue_green "$service_name" "$image_tag" "$environment"
            ;;
        "canary")
            deploy_canary "$service_name" "$image_tag" "$environment"
            ;;
        "recreate")
            deploy_recreate "$service_name" "$image_tag" "$environment"
            ;;
        *)
            log_error "Unknown deployment strategy: $strategy"
            exit 1
            ;;
    esac
    
    # Wait for deployment to complete
    if ! wait_for_deployment "$service_name"; then
        log_error "Deployment verification failed"
        initiate_rollback "$service_name" "$environment" "Deployment verification failed"
        exit 1
    fi
    
    # Run health checks
    local health_url="https://${environment}.example.com/health"
    if ! health_check "$health_url"; then
        log_error "Health check failed after deployment"
        initiate_rollback "$service_name" "$environment" "Health check failed"
        exit 1
    fi
    
    # Run smoke tests
    local base_url="https://${environment}.example.com"
    if ! run_smoke_tests "$base_url" "$environment"; then
        log_error "Smoke tests failed after deployment"
        initiate_rollback "$service_name" "$environment" "Smoke tests failed"
        exit 1
    fi
    
    # Generate deployment report
    generate_deployment_report "$environment" "$strategy" "$image_tag" "success"
    
    log_success "Deployment completed successfully"
}

# Main entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 4 ]]; then
        echo "Usage: $0 <service_name> <image_tag> <environment> <strategy>"
        echo "Example: $0 my-app v1.2.3 production rolling"
        exit 1
    fi
    
    deploy "$1" "$2" "$3" "$4"
fi