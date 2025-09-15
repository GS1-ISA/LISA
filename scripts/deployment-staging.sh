#!/bin/bash
# Deployment Staging and Gating Script

set -euo pipefail

# Source helper functions
source "$(dirname "$0")/unified-cicd-helpers.sh"

# Configuration
STAGING_CONFIG_FILE="staging-config.json"
DEPLOYMENT_GATES_FILE="deployment-gates.json"
APPROVAL_TIMEOUT=3600  # 1 hour
STAGING_TIMEOUT=1800   # 30 minutes

# Initialize staging configuration
init_staging_config() {
    log_info "Initializing staging configuration"
    
    cat > "$STAGING_CONFIG_FILE" <<EOF
{
    "environments": {
        "development": {
            "auto_deploy": true,
            "required_approvals": 0,
            "staging_timeout": 300,
            "gates": ["build", "unit_tests", "security_scan"]
        },
        "staging": {
            "auto_deploy": false,
            "required_approvals": 1,
            "staging_timeout": 1800,
            "gates": ["build", "unit_tests", "integration_tests", "security_scan", "performance_tests"]
        },
        "production": {
            "auto_deploy": false,
            "required_approvals": 2,
            "staging_timeout": 3600,
            "gates": ["build", "unit_tests", "integration_tests", "security_scan", "performance_tests", "smoke_tests", "manual_approval"]
        }
    },
    "deployment_strategies": {
        "blue_green": {
            "enabled": true,
            "health_check_timeout": 300,
            "traffic_switch_timeout": 60
        },
        "canary": {
            "enabled": true,
            "canary_percentage": 10,
            "progressive_rollout": true,
            "rollback_threshold": 5
        },
        "rolling": {
            "enabled": true,
            "max_unavailable": 1,
            "max_surge": 1
        }
    }
}
EOF
    
    log_success "Staging configuration initialized: $STAGING_CONFIG_FILE"
}

# Create deployment gates configuration
create_deployment_gates() {
    log_info "Creating deployment gates configuration"
    
    cat > "$DEPLOYMENT_GATES_FILE" <<EOF
{
    "gates": {
        "build": {
            "type": "automated",
            "description": "Build and package application",
            "retry_count": 3,
            "timeout": 1800,
            "failure_threshold": 1
        },
        "unit_tests": {
            "type": "automated",
            "description": "Run unit tests",
            "retry_count": 2,
            "timeout": 900,
            "failure_threshold": 1,
            "coverage_threshold": 80
        },
        "integration_tests": {
            "type": "automated",
            "description": "Run integration tests",
            "retry_count": 2,
            "timeout": 1800,
            "failure_threshold": 1
        },
        "security_scan": {
            "type": "automated",
            "description": "Security vulnerability scanning",
            "retry_count": 1,
            "timeout": 1200,
            "failure_threshold": 0,
            "severity_threshold": "high"
        },
        "performance_tests": {
            "type": "automated",
            "description": "Performance and load testing",
            "retry_count": 1,
            "timeout": 3600,
            "failure_threshold": 1,
            "performance_thresholds": {
                "response_time_ms": 500,
                "error_rate_percent": 1,
                "throughput_rps": 100
            }
        },
        "smoke_tests": {
            "type": "automated",
            "description": "Smoke tests in staging environment",
            "retry_count": 2,
            "timeout": 600,
            "failure_threshold": 0
        },
        "manual_approval": {
            "type": "manual",
            "description": "Manual approval required",
            "timeout": 7200,
            "required_approvers": ["team_lead", "product_owner"]
        }
    }
}
EOF
    
    log_success "Deployment gates configuration created: $DEPLOYMENT_GATES_FILE"
}

# Execute deployment gate
execute_gate() {
    local gate_name=$1
    local environment=$2
    local deployment_id=$3
    
    log_info "Executing deployment gate: $gate_name for environment: $environment"
    
    local gate_config=$(jq -r ".gates.$gate_name" "$DEPLOYMENT_GATES_FILE")
    local gate_type=$(echo "$gate_config" | jq -r '.type')
    local timeout=$(echo "$gate_config" | jq -r '.timeout')
    local retry_count=$(echo "$gate_config" | jq -r '.retry_count')
    
    case $gate_type in
        "automated")
            execute_automated_gate "$gate_name" "$gate_config" "$environment" "$deployment_id" "$retry_count" "$timeout"
            ;;
        "manual")
            execute_manual_gate "$gate_name" "$gate_config" "$environment" "$deployment_id" "$timeout"
            ;;
        *)
            log_error "Unknown gate type: $gate_type"
            return 1
            ;;
    esac
}

# Execute automated gate
execute_automated_gate() {
    local gate_name=$1
    local gate_config=$2
    local environment=$3
    local deployment_id=$4
    local retry_count=$5
    local timeout=$6
    
    local attempt=1
    local success=false
    
    while [[ $attempt -le $retry_count ]] && [[ "$success" == "false" ]]; do
        log_info "Attempt $attempt/$retry_count for gate: $gate_name"
        
        case $gate_name in
            "build")
                success=$(execute_build_gate "$environment" "$deployment_id" "$timeout")
                ;;
            "unit_tests")
                success=$(execute_unit_tests_gate "$environment" "$deployment_id" "$timeout")
                ;;
            "integration_tests")
                success=$(execute_integration_tests_gate "$environment" "$deployment_id" "$timeout")
                ;;
            "security_scan")
                success=$(execute_security_scan_gate "$environment" "$deployment_id" "$timeout")
                ;;
            "performance_tests")
                success=$(execute_performance_tests_gate "$environment" "$deployment_id" "$timeout")
                ;;
            "smoke_tests")
                success=$(execute_smoke_tests_gate "$environment" "$deployment_id" "$timeout")
                ;;
            *)
                log_error "Unknown automated gate: $gate_name"
                return 1
                ;;
        esac
        
        if [[ "$success" == "true" ]]; then
            log_success "Gate $gate_name passed on attempt $attempt"
            return 0
        else
            log_warn "Gate $gate_name failed on attempt $attempt"
            ((attempt++))
            sleep 30  # Wait before retry
        fi
    done
    
    log_error "Gate $gate_name failed after $retry_count attempts"
    return 1
}

# Execute build gate
execute_build_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing build gate for environment: $environment"
    
    # Run build process
    if timeout "$timeout" ./scripts/unified-cicd-pipeline.sh build; then
        log_success "Build gate passed"
        echo "true"
    else
        log_error "Build gate failed"
        echo "false"
    fi
}

# Execute unit tests gate
execute_unit_tests_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing unit tests gate for environment: $environment"
    
    # Run unit tests
    if timeout "$timeout" ./scripts/unified-cicd-pipeline.sh test; then
        # Check coverage threshold
        local coverage=$(get_test_coverage)
        local threshold=$(jq -r '.gates.unit_tests.coverage_threshold' "$DEPLOYMENT_GATES_FILE")
        
        if (( $(echo "$coverage >= $threshold" | bc -l) )); then
            log_success "Unit tests gate passed with coverage: $coverage%"
            echo "true"
        else
            log_error "Unit tests gate failed - coverage $coverage% below threshold $threshold%"
            echo "false"
        fi
    else
        log_error "Unit tests gate failed"
        echo "false"
    fi
}

# Execute integration tests gate
execute_integration_tests_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing integration tests gate for environment: $environment"
    
    # Deploy to staging environment first
    if deploy_to_staging "$deployment_id"; then
        # Run integration tests
        if timeout "$timeout" ./scripts/unified-cicd-pipeline.sh integration-test; then
            log_success "Integration tests gate passed"
            echo "true"
        else
            log_error "Integration tests gate failed"
            echo "false"
        fi
    else
        log_error "Failed to deploy to staging for integration tests"
        echo "false"
    fi
}

# Execute security scan gate
execute_security_scan_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing security scan gate for environment: $environment"
    
    # Run security scans
    if timeout "$timeout" ./scripts/security-scanning.sh scan-all; then
        # Check for high severity vulnerabilities
        local high_severity_count=$(get_security_scan_results | jq -r '.high_severity_count // 0')
        local threshold=$(jq -r '.gates.security_scan.failure_threshold' "$DEPLOYMENT_GATES_FILE")
        
        if [[ $high_severity_count -le $threshold ]]; then
            log_success "Security scan gate passed - $high_severity_count high severity issues found"
            echo "true"
        else
            log_error "Security scan gate failed - $high_severity_count high severity issues exceed threshold $threshold"
            echo "false"
        fi
    else
        log_error "Security scan gate failed"
        echo "false"
    fi
}

# Execute performance tests gate
execute_performance_tests_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing performance tests gate for environment: $environment"
    
    # Run performance tests
    if timeout "$timeout" ./scripts/unified-cicd-pipeline.sh performance-test; then
        # Check performance thresholds
        local perf_results=$(get_performance_test_results)
        local response_time=$(echo "$perf_results" | jq -r '.response_time_ms')
        local error_rate=$(echo "$perf_results" | jq -r '.error_rate_percent')
        
        local response_threshold=$(jq -r '.gates.performance_tests.performance_thresholds.response_time_ms' "$DEPLOYMENT_GATES_FILE")
        local error_threshold=$(jq -r '.gates.performance_tests.performance_thresholds.error_rate_percent' "$DEPLOYMENT_GATES_FILE")
        
        if [[ $(echo "$response_time <= $response_threshold" | bc -l) == 1 ]] && [[ $(echo "$error_rate <= $error_threshold" | bc -l) == 1 ]]; then
            log_success "Performance tests gate passed - response time: ${response_time}ms, error rate: ${error_rate}%"
            echo "true"
        else
            log_error "Performance tests gate failed - response time: ${response_time}ms (threshold: ${response_threshold}ms), error rate: ${error_rate}% (threshold: ${error_threshold}%)"
            echo "false"
        fi
    else
        log_error "Performance tests gate failed"
        echo "false"
    fi
}

# Execute smoke tests gate
execute_smoke_tests_gate() {
    local environment=$1
    local deployment_id=$2
    local timeout=$3
    
    log_info "Executing smoke tests gate for environment: $environment"
    
    # Deploy to staging environment
    if deploy_to_staging "$deployment_id"; then
        # Run smoke tests
        if timeout "$timeout" ./scripts/unified-cicd-pipeline.sh smoke-test; then
            log_success "Smoke tests gate passed"
            echo "true"
        else
            log_error "Smoke tests gate failed"
            echo "false"
        fi
    else
        log_error "Failed to deploy to staging for smoke tests"
        echo "false"
    fi
}

# Execute manual gate
execute_manual_gate() {
    local gate_name=$1
    local gate_config=$2
    local environment=$3
    local deployment_id=$4
    local timeout=$5
    
    log_info "Executing manual gate: $gate_name for environment: $environment"
    
    local required_approvers=$(echo "$gate_config" | jq -r '.required_approvers[]')
    local approval_count=0
    
    # Create approval request
    local approval_request=$(create_approval_request "$gate_name" "$environment" "$deployment_id" "$required_approvers")
    local request_id=$(echo "$approval_request" | jq -r '.request_id')
    
    log_info "Created approval request: $request_id"
    log_info "Waiting for manual approval (timeout: $timeout seconds)"
    
    # Wait for approval
    local start_time=$(date +%s)
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -ge $timeout ]]; then
            log_error "Manual approval timeout reached"
            cancel_approval_request "$request_id"
            return 1
        fi
        
        # Check approval status
        local status=$(check_approval_status "$request_id")
        if [[ "$status" == "approved" ]]; then
            log_success "Manual gate approved"
            return 0
        elif [[ "$status" == "rejected" ]]; then
            log_error "Manual gate rejected"
            return 1
        fi
        
        sleep 30
    done
}

# Create approval request
create_approval_request() {
    local gate_name=$1
    local environment=$2
    local deployment_id=$3
    local required_approvers=$4
    
    local request_id=$(uuidgen)
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    local approval_request=$(cat <<EOF
{
    "request_id": "$request_id",
    "gate_name": "$gate_name",
    "environment": "$environment",
    "deployment_id": "$deployment_id",
    "timestamp": "$timestamp",
    "status": "pending",
    "required_approvers": [$required_approvers],
    "approvals": [],
    "rejections": []
}
EOF
)
    
    echo "$approval_request" > "approval-requests/${request_id}.json"
    echo "$approval_request"
}

# Deploy to staging environment
deploy_to_staging() {
    local deployment_id=$1
    
    log_info "Deploying to staging environment for deployment: $deployment_id"
    
    # Deploy using staging configuration
    if ./scripts/unified-cicd-pipeline.sh deploy staging "$deployment_id"; then
        log_success "Deployment to staging completed"
        return 0
    else
        log_error "Deployment to staging failed"
        return 1
    fi
}

# Main staging deployment process
execute_staging_deployment() {
    local deployment_name=$1
    local environment=$2
    local version=$3
    local deployment_id=$(uuidgen)
    
    log_info "Starting staging deployment process for: $deployment_name v$version to $environment"
    
    # Get environment configuration
    local env_config=$(jq -r ".environments.$environment" "$STAGING_CONFIG_FILE")
    local gates=$(echo "$env_config" | jq -r '.gates[]')
    local staging_timeout=$(echo "$env_config" | jq -r '.staging_timeout')
    
    # Execute each gate
    for gate in $gates; do
        log_info "Executing gate: $gate"
        
        if ! execute_gate "$gate" "$environment" "$deployment_id"; then
            log_error "Deployment gate failed: $gate"
            
            # Trigger rollback if configured
            if [[ -f "rollback-triggered" ]]; then
                ./scripts/rollback-deployment.sh trigger "$deployment_name" "$environment" "staging" "Gate $gate failed"
            fi
            
            return 1
        fi
        
        log_success "Gate passed: $gate"
    done
    
    log_success "All deployment gates passed for: $deployment_name v$version to $environment"
    return 0
}

# Helper functions (mock implementations)
get_test_coverage() {
    echo "85.5"
}

get_security_scan_results() {
    echo '{"high_severity_count": 0, "medium_severity_count": 2, "low_severity_count": 5}'
}

get_performance_test_results() {
    echo '{"response_time_ms": 250, "error_rate_percent": 0.1, "throughput_rps": 150}'
}

check_approval_status() {
    local request_id=$1
    # Mock implementation - would check actual approval status
    echo "pending"
}

cancel_approval_request() {
    local request_id=$1
    # Mock implementation - would cancel actual approval request
    log_info "Approval request cancelled: $request_id"
}

# Main function
main() {
    local command=$1
    shift
    
    case $command in
        "init")
            init_staging_config
            create_deployment_gates
            mkdir -p approval-requests
            ;;
        "deploy")
            execute_staging_deployment "$@"
            ;;
        "gate")
            execute_gate "$@"
            ;;
        *)
            echo "Usage: $0 {init|deploy|gate} [parameters...]"
            echo ""
            echo "Examples:"
            echo "  $0 init"
            echo "  $0 deploy my-app production 1.2.3"
            echo "  $0 gate manual_approval production deployment-123"
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