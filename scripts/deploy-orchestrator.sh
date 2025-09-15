#!/bin/bash

# Unified Deployment Orchestrator
# This script coordinates all deployment activities across platforms and environments

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/deployment-config.yaml"
LOG_FILE="/tmp/deployment-$(date +%Y%m%d-%H%M%S).log"
DEPLOYMENT_ID="$(date +%s)-${RANDOM}"

# Default values
ENVIRONMENT=""
PLATFORM=""
IMAGE_TAG=""
DEPLOYMENT_STRATEGY=""
SKIP_SECURITY_SCAN=false
FORCE_DEPLOYMENT=false
VERBOSE=false
DRY_RUN=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
    
    case "${level}" in
        ERROR) echo -e "${RED}${timestamp} [ERROR] ${message}${NC}" ;;
        WARN) echo -e "${YELLOW}${timestamp} [WARN] ${message}${NC}" ;;
        INFO) echo -e "${GREEN}${timestamp} [INFO] ${message}${NC}" ;;
        DEBUG) 
            if [[ "${VERBOSE}" == "true" ]]; then
                echo -e "${BLUE}${timestamp} [DEBUG] ${message}${NC}"
            fi
            ;;
    esac
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    cleanup_on_failure
    exit 1
}

# Cleanup function
cleanup_on_failure() {
    log "INFO" "Cleaning up on failure..."
    
    # Archive deployment logs
    if [[ -f "${LOG_FILE}" ]]; then
        aws s3 cp "${LOG_FILE}" "s3://deployment-logs/${DEPLOYMENT_ID}/" || true
    fi
    
    # Send failure notification
    send_notification "failure" "Deployment failed: ${DEPLOYMENT_ID}"
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Unified Deployment Orchestrator

OPTIONS:
    -e, --environment ENV       Target environment (development|staging|production)
    -p, --platform PLATFORM     Target platform (kubernetes|ecs|docker)
    -i, --image-tag TAG         Docker image tag to deploy
    -s, --strategy STRATEGY     Deployment strategy (rolling|blue-green|canary|recreate)
    --skip-security-scan        Skip security scanning (not recommended)
    --force                     Force deployment even if checks fail
    --dry-run                   Perform a dry run without actual deployment
    -v, --verbose               Enable verbose logging
    -h, --help                  Show this help message

EXAMPLES:
    $0 -e production -p kubernetes -i v1.2.3 -s canary
    $0 -e staging -p ecs -i latest -s blue-green --verbose
    $0 -e development -p docker -i dev-build -s rolling --dry-run

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
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -i|--image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -s|--strategy)
                DEPLOYMENT_STRATEGY="$2"
                shift 2
                ;;
            --skip-security-scan)
                SKIP_SECURITY_SCAN=true
                shift
                ;;
            --force)
                FORCE_DEPLOYMENT=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1"
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    log "INFO" "Validating inputs..."
    
    # Check required parameters
    if [[ -z "${ENVIRONMENT}" ]]; then
        error_exit "Environment is required"
    fi
    
    if [[ -z "${PLATFORM}" ]]; then
        error_exit "Platform is required"
    fi
    
    if [[ -z "${IMAGE_TAG}" ]]; then
        error_exit "Image tag is required"
    fi
    
    # Validate environment
    if [[ ! "${ENVIRONMENT}" =~ ^(development|staging|production)$ ]]; then
        error_exit "Invalid environment: ${ENVIRONMENT}. Must be development, staging, or production"
    fi
    
    # Validate platform
    if [[ ! "${PLATFORM}" =~ ^(kubernetes|ecs|docker)$ ]]; then
        error_exit "Invalid platform: ${PLATFORM}. Must be kubernetes, ecs, or docker"
    fi
    
    # Validate deployment strategy if provided
    if [[ -n "${DEPLOYMENT_STRATEGY}" ]] && [[ ! "${DEPLOYMENT_STRATEGY}" =~ ^(rolling|blue-green|canary|recreate)$ ]]; then
        error_exit "Invalid deployment strategy: ${DEPLOYMENT_STRATEGY}. Must be rolling, blue-green, canary, or recreate"
    fi
    
    # Check if config file exists
    if [[ ! -f "${CONFIG_FILE}" ]]; then
        error_exit "Configuration file not found: ${CONFIG_FILE}"
    fi
    
    log "INFO" "Input validation completed successfully"
}

# Load configuration
load_configuration() {
    log "INFO" "Loading configuration from ${CONFIG_FILE}..."
    
    # Check if yq is available
    if ! command -v yq &> /dev/null; then
        log "WARN" "yq not found, installing..."
        wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
        chmod +x /usr/local/bin/yq
    fi
    
    # Load environment-specific configuration
    ENV_CONFIG=$(yq eval ".environments.${ENVIRONMENT}" "${CONFIG_FILE}")
    if [[ "${ENV_CONFIG}" == "null" ]]; then
        error_exit "Environment configuration not found: ${ENVIRONMENT}"
    fi
    
    # Load platform-specific configuration
    PLATFORM_CONFIG=$(yq eval ".platforms.${PLATFORM}" "${CONFIG_FILE}")
    if [[ "${PLATFORM_CONFIG}" == "null" ]]; then
        error_exit "Platform configuration not found: ${PLATFORM}"
    fi
    
    # Set deployment strategy if not provided
    if [[ -z "${DEPLOYMENT_STRATEGY}" ]]; then
        DEPLOYMENT_STRATEGY=$(yq eval ".environments.${ENVIRONMENT}.deployment_strategy" "${CONFIG_FILE}")
        if [[ "${DEPLOYMENT_STRATEGY}" == "null" ]]; then
            DEPLOYMENT_STRATEGY="rolling"
        fi
    fi
    
    log "INFO" "Configuration loaded successfully"
    log "DEBUG" "Environment: ${ENVIRONMENT}, Platform: ${PLATFORM}, Strategy: ${DEPLOYMENT_STRATEGY}"
}

# Check environment protection rules
check_environment_protection() {
    log "INFO" "Checking environment protection rules..."
    
    # Check if environment is enabled
    ENV_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.enabled" "${CONFIG_FILE}")
    if [[ "${ENV_ENABLED}" != "true" ]]; then
        error_exit "Environment ${ENVIRONMENT} is not enabled"
    fi
    
    # Check deployment branch
    DEPLOYMENT_BRANCH=$(yq eval ".environments.${ENVIRONMENT}.deployment_branch" "${CONFIG_FILE}")
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "${DEPLOYMENT_BRANCH}" != "null" ]] && [[ "${CURRENT_BRANCH}" != "${DEPLOYMENT_BRANCH}" ]]; then
        error_exit "Deployment from branch ${CURRENT_BRANCH} not allowed. Must be from ${DEPLOYMENT_BRANCH}"
    fi
    
    # Check deployment window
    DEPLOYMENT_WINDOW_START=$(yq eval ".environments.${ENVIRONMENT}.deployment_window.start" "${CONFIG_FILE}")
    DEPLOYMENT_WINDOW_END=$(yq eval ".environments.${ENVIRONMENT}.deployment_window.end" "${CONFIG_FILE}")
    if [[ "${DEPLOYMENT_WINDOW_START}" != "null" ]] && [[ "${DEPLOYMENT_WINDOW_END}" != "null" ]]; then
        CURRENT_TIME=$(date +%H:%M)
        if [[ "${CURRENT_TIME}" < "${DEPLOYMENT_WINDOW_START}" ]] || [[ "${CURRENT_TIME}" > "${DEPLOYMENT_WINDOW_END}" ]]; then
            error_exit "Deployment outside allowed window (${DEPLOYMENT_WINDOW_START} - ${DEPLOYMENT_WINDOW_END})"
        fi
    fi
    
    # Check approval requirements
    APPROVAL_REQUIRED=$(yq eval ".environments.${ENVIRONMENT}.approval_required" "${CONFIG_FILE}")
    if [[ "${APPROVAL_REQUIRED}" == "true" ]] && [[ "${FORCE_DEPLOYMENT}" != "true" ]]; then
        log "WARN" "Approval required for ${ENVIRONMENT} environment"
        # In a real implementation, this would check for actual approvals
        # For now, we'll prompt for manual confirmation
        read -p "Deployment to ${ENVIRONMENT} requires approval. Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error_exit "Deployment cancelled by user"
        fi
    fi
    
    log "INFO" "Environment protection checks passed"
}

# Run security scanning
run_security_scan() {
    if [[ "${SKIP_SECURITY_SCAN}" == "true" ]]; then
        log "WARN" "Security scanning skipped"
        return 0
    fi
    
    log "INFO" "Running security scanning..."
    
    # Check if security scanning is enabled
    SECURITY_ENABLED=$(yq eval ".security.scan_enabled" "${CONFIG_FILE}")
    if [[ "${SECURITY_ENABLED}" != "true" ]]; then
        log "INFO" "Security scanning disabled in configuration"
        return 0
    fi
    
    # Run Trivy scan
    log "INFO" "Running Trivy vulnerability scan..."
    trivy image --severity HIGH,CRITICAL --exit-code 1 "${IMAGE_TAG}" || {
        if [[ "${FORCE_DEPLOYMENT}" != "true" ]]; then
            error_exit "Trivy scan failed. Use --force to deploy anyway."
        else
            log "WARN" "Trivy scan failed but continuing due to --force flag"
        fi
    }
    
    # Run Snyk scan
    log "INFO" "Running Snyk security scan..."
    snyk test --docker "${IMAGE_TAG}" --severity-threshold=high || {
        if [[ "${FORCE_DEPLOYMENT}" != "true" ]]; then
            error_exit "Snyk scan failed. Use --force to deploy anyway."
        else
            log "WARN" "Snyk scan failed but continuing due to --force flag"
        fi
    }
    
    log "INFO" "Security scanning completed successfully"
}

# Execute deployment
execute_deployment() {
    log "INFO" "Executing deployment..."
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "DRY RUN: Would deploy to ${ENVIRONMENT} on ${PLATFORM} with strategy ${DEPLOYMENT_STRATEGY}"
        return 0
    fi
    
    # Select deployment script based on platform
    case "${PLATFORM}" in
        kubernetes)
            DEPLOY_SCRIPT="${SCRIPT_DIR}/deploy-kubernetes.sh"
            ;;
        ecs)
            DEPLOY_SCRIPT="${SCRIPT_DIR}/deploy-ecs.sh"
            ;;
        docker)
            DEPLOY_SCRIPT="${SCRIPT_DIR}/deploy-docker.sh"
            ;;
        *)
            error_exit "Unsupported platform: ${PLATFORM}"
            ;;
    esac
    
    # Check if deployment script exists
    if [[ ! -f "${DEPLOY_SCRIPT}" ]]; then
        error_exit "Deployment script not found: ${DEPLOY_SCRIPT}"
    fi
    
    # Execute deployment script
    log "INFO" "Executing deployment script: ${DEPLOY_SCRIPT}"
    "${DEPLOY_SCRIPT}" \
        --environment "${ENVIRONMENT}" \
        --image-tag "${IMAGE_TAG}" \
        --strategy "${DEPLOYMENT_STRATEGY}" \
        --deployment-id "${DEPLOYMENT_ID}" \
        --config-file "${CONFIG_FILE}" \
        --verbose || {
        error_exit "Deployment failed"
    }
    
    log "INFO" "Deployment executed successfully"
}

# Run health checks
run_health_checks() {
    log "INFO" "Running health checks..."
    
    # Check if health checks are enabled
    HEALTH_CHECK_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.health_check.enabled" "${CONFIG_FILE}")
    if [[ "${HEALTH_CHECK_ENABLED}" != "true" ]]; then
        log "INFO" "Health checks disabled for ${ENVIRONMENT}"
        return 0
    fi
    
    # Get health check configuration
    HEALTH_CHECK_ENDPOINT=$(yq eval ".environments.${ENVIRONMENT}.health_check.endpoint" "${CONFIG_FILE}")
    HEALTH_CHECK_TIMEOUT=$(yq eval ".environments.${ENVIRONMENT}.health_check.timeout" "${CONFIG_FILE}")
    HEALTH_CHECK_RETRIES=$(yq eval ".environments.${ENVIRONMENT}.health_check.retries" "${CONFIG_FILE}")
    HEALTH_CHECK_RETRY_DELAY=$(yq eval ".environments.${ENVIRONMENT}.health_check.retry_delay" "${CONFIG_FILE}")
    
    # Execute health check script
    HEALTH_CHECK_SCRIPT="${SCRIPT_DIR}/health-check.sh"
    if [[ -f "${HEALTH_CHECK_SCRIPT}" ]]; then
        "${HEALTH_CHECK_SCRIPT}" \
            --environment "${ENVIRONMENT}" \
            --platform "${PLATFORM}" \
            --endpoint "${HEALTH_CHECK_ENDPOINT}" \
            --timeout "${HEALTH_CHECK_TIMEOUT}" \
            --retries "${HEALTH_CHECK_RETRIES}" \
            --retry-delay "${HEALTH_CHECK_RETRY_DELAY}" \
            --verbose || {
            log "ERROR" "Health checks failed"
            execute_rollback
            error_exit "Health checks failed, rollback executed"
        }
    else
        log "WARN" "Health check script not found, skipping health checks"
    fi
    
    log "INFO" "Health checks completed successfully"
}

# Execute rollback
execute_rollback() {
    log "INFO" "Executing rollback..."
    
    # Check if rollback is enabled
    ROLLBACK_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.rollback.enabled" "${CONFIG_FILE}")
    if [[ "${ROLLBACK_ENABLED}" != "true" ]]; then
        log "WARN" "Rollback disabled for ${ENVIRONMENT}"
        return 0
    fi
    
    # Execute rollback script
    ROLLBACK_SCRIPT="${SCRIPT_DIR}/rollback-deployment.sh"
    if [[ -f "${ROLLBACK_SCRIPT}" ]]; then
        "${ROLLBACK_SCRIPT}" \
            --environment "${ENVIRONMENT}" \
            --platform "${PLATFORM}" \
            --deployment-id "${DEPLOYMENT_ID}" \
            --config-file "${CONFIG_FILE}" \
            --verbose || {
            log "ERROR" "Rollback failed"
        }
    else
        log "WARN" "Rollback script not found"
    fi
}

# Send notifications
send_notification() {
    local status="$1"
    local message="$2"
    
    log "INFO" "Sending notification: ${status} - ${message}"
    
    # Get notification configuration
    SLACK_ENABLED=$(yq eval ".notifications.slack.enabled" "${CONFIG_FILE}")
    EMAIL_ENABLED=$(yq eval ".notifications.email.enabled" "${CONFIG_FILE}")
    
    # Send Slack notification
    if [[ "${SLACK_ENABLED}" == "true" ]]; then
        SLACK_WEBHOOK=$(yq eval ".notifications.slack.webhook_url" "${CONFIG_FILE}")
        SLACK_CHANNEL=$(yq eval ".notifications.slack.channels.${ENVIRONMENT}" "${CONFIG_FILE}")
        
        if [[ "${SLACK_WEBHOOK}" != "null" ]] && [[ "${SLACK_CHANNEL}" != "null" ]]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{
                    \"channel\": \"${SLACK_CHANNEL}\",
                    \"username\": \"Deployment Bot\",
                    \"text\": \"${message}\",
                    \"icon_emoji\": \":rocket:\"
                }" \
                "${SLACK_WEBHOOK}" || log "WARN" "Failed to send Slack notification"
        fi
    fi
    
    # Send email notification (simplified implementation)
    if [[ "${EMAIL_ENABLED}" == "true" ]]; then
        log "INFO" "Email notification would be sent (implementation required)"
    fi
}

# Main execution
main() {
    log "INFO" "Starting unified deployment orchestrator"
    log "INFO" "Deployment ID: ${DEPLOYMENT_ID}"
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate inputs
    validate_inputs
    
    # Load configuration
    load_configuration
    
    # Check environment protection
    check_environment_protection
    
    # Run security scanning
    run_security_scan
    
    # Execute deployment
    execute_deployment
    
    # Run health checks
    run_health_checks
    
    # Send success notification
    send_notification "success" "Deployment completed successfully: ${DEPLOYMENT_ID}"
    
    log "INFO" "Deployment orchestrator completed successfully"
}

# Execute main function
main "$@"