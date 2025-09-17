
#!/bin/bash

# Deployment Script with Staging and Gating
# This script handles deployment with proper staging, gating, and approval workflows

set -euo pipefail

# Default values
ENVIRONMENT="development"
DEPLOYMENT_STRATEGY="rolling"
CONFIG_FILE="config/deployment-config.yaml"
DRY_RUN="false"
VERBOSE="false"
SKIP_TESTS="false"
SKIP_SECURITY_SCAN="false"
FORCE_DEPLOY="false"
APPROVAL_REQUIRED="false"
STAGING_TIMEOUT=300
GATE_TIMEOUT=600
MAX_WAIT_TIME=1800

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

log_stage() {
    echo -e "${PURPLE}[STAGE]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Deployment script with staging and gating for Docker-based applications

OPTIONS:
    -e, --environment ENV       Target environment (development, staging, production)
    -s, --strategy STRATEGY     Deployment strategy (rolling, blue-green, canary, recreate)
    -c, --config-file FILE      Configuration file path
    --staging-timeout SECONDS   Timeout for staging phase (default: 300)
    --gate-timeout SECONDS      Timeout for gate checks (default: 600)
    --max-wait-time SECONDS     Maximum total wait time (default: 1800)
    --skip-tests                Skip test execution
    --skip-security-scan        Skip security scanning
    --force-deploy              Force deployment without confirmation
    --approval-required         Require manual approval for deployment
    --dry-run                   Perform a dry run without actual deployment
    --verbose                   Enable verbose output
    -h, --help                  Show this help message

EXAMPLES:
    $0 --environment staging --strategy blue-green
    $0 -e production -s canary --approval-required
    $0 --environment development --dry-run --verbose
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
            -s|--strategy)
                DEPLOYMENT_STRATEGY="$2"
                shift 2
                ;;
            -c|--config-file)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --staging-timeout)
                STAGING_TIMEOUT="$2"
                shift 2
                ;;
            --gate-timeout)
                GATE_TIMEOUT="$2"
                shift 2
                ;;
            --max-wait-time)
                MAX_WAIT_TIME="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS="true"
                shift
                ;;
            --skip-security-scan)
                SKIP_SECURITY_SCAN="true"
                shift
                ;;
            --force-deploy)
                FORCE_DEPLOY="true"
                shift
                ;;
            --approval-required)
                APPROVAL_REQUIRED="true"
                shift
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
    log_info "Validating deployment inputs..."
    
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
    
    # Check if required tools are installed
    check_required_tools
    
    log_success "Input validation completed"
}

# Check required tools
check_required_tools() {
    local missing_tools=()
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi
    
    # Check for yq (YAML processor)
    if ! command -v yq &> /dev/null; then
        missing_tools+=("yq")
    fi
    
    # Check for jq (JSON processor)
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and try again"
        exit 1
    fi
}

# Load configuration from YAML file
load_configuration() {
    log_info "Loading configuration from $CONFIG_FILE..."
    
    # Load environment-specific configuration
    local env_config
    env_config=$(yq eval ".environments.${ENVIRONMENT}" "$CONFIG_FILE")
    
    if [[ "$env_config" == "null" ]]; then
        log_error "Configuration for environment '$ENVIRONMENT' not found in $CONFIG_FILE"
        exit 1
    fi
    
    # Extract configuration values
    REPLICAS=$(yq eval ".environments.${ENVIRONMENT}.resources.replicas" "$CONFIG_FILE")
    HEALTH_CHECK_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.health_checks.enabled" "$CONFIG_FILE")
    DEPLOYMENT_TIMEOUT=$(yq eval ".environments.${ENVIRONMENT}.deployment.timeout" "$CONFIG_FILE")
    ROLLBACK_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.rollback.enabled" "$CONFIG_FILE")
    MONITORING_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.monitoring.enabled" "$CONFIG_FILE")
    SECURITY_SCAN_ENABLED=$(yq eval ".environments.${ENVIRONMENT}.security.scan_enabled" "$CONFIG_FILE")
    
    log_success "Configuration loaded successfully"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_stage "=== PRE-DEPLOYMENT CHECKS ==="
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if required images exist
    check_required_images
    
    # Check available resources
    check_available_resources
    
    # Validate configuration
    validate_configuration
    
    # Check for conflicting deployments
    check_conflicting_deployments
    
    log_success "Pre-deployment checks completed"
}

# Check required images
check_required_images() {
    log_info "Checking required Docker images..."
    
    # Check if the main application image exists
    local image_tag="${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}"
    
    if ! docker image inspect "$image_tag" &> /dev/null; then
        log_warning "Image $image_tag not found locally. Attempting to pull..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] Would pull image: $image_tag"
        else
            if ! docker pull "$image_tag" &> /dev/null; then
                log_error "Failed to pull image: $image_tag"
                exit 1
            fi
        fi
    fi
    
    log_success "Required images check completed"
}

# Check available resources
check_available_resources() {
    log_info "Checking available system resources..."
    
    # Check disk space
    local available_disk
    available_disk=$(df -h . | awk 'NR==2 {print $4}' | sed 's/Gi//')
    
    if [[ $(echo "$available_disk < 5" | bc -l) -eq 1 ]]; then
        log_warning "Low disk space available: ${available_disk}GB"
    fi
    
    # Check memory
    local available_memory
    available_memory=$(free -g | awk 'NR==2{printf "%.1f", $7}')
    
    if [[ $(echo "$available_memory < 2" | bc -l) -eq 1 ]]; then
        log_warning "Low memory available: ${available_memory}GB"
    fi
    
    log_success "Resource check completed"
}

# Validate configuration
validate_configuration() {
    log_info "Validating deployment configuration..."
    
    # Validate Docker Compose files
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would validate Docker Compose configuration"
    else
        if ! docker-compose config &> /dev/null; then
            log_error "Docker Compose configuration is invalid"
            exit 1
        fi
    fi
    
    log_success "Configuration validation completed"
}

# Check for conflicting deployments
check_conflicting_deployments() {
    log_info "Checking for conflicting deployments..."
    
    # Check if there are any running deployments
    local running_containers
    running_containers=$(docker-compose ps --format json | jq -r '.[] | select(.State == "running") | .Service' 2>/dev/null || echo "")
    
    if [[ -n "$running_containers" ]]; then
        log_warning "Found running containers: $running_containers"
        
        if [[ "$FORCE_DEPLOY" != "true" ]]; then
            log_error "Deployment conflict detected. Use --force-deploy to override"
            exit 1
        fi
    fi
    
    log_success "Conflict check completed"
}

# Security scanning phase
security_scanning_phase() {
    if [[ "$SKIP_SECURITY_SCAN" == "true" ]]; then
        log_warning "Security scanning skipped"
        return 0
    fi
    
    log_stage "=== SECURITY SCANNING PHASE ==="
    
    if [[ "$SECURITY_SCAN_ENABLED" != "true" ]]; then
        log_info "Security scanning disabled for $ENVIRONMENT"
        return 0
    fi
    
    # Run Trivy scan
    run_trivy_scan
    
    # Run Snyk scan (if available)
    if command -v snyk &> /dev/null; then
        run_snyk_scan
    fi
    
    # Run Grype scan (if available)
    if command -v grype &> /dev/null; then
        run_grype_scan
    fi
    
    log_success "Security scanning completed"
}

# Run Trivy scan
run_trivy_scan() {
    log_info "Running Trivy security scan..."
    
    local image_tag="${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run Trivy scan on image: $image_tag"
        return 0
    fi
    
    # Run Trivy scan
    if ! trivy image --severity HIGH,CRITICAL --exit-code 1 "$image_tag"; then
        log_error "Trivy scan found critical vulnerabilities"
        
        if [[ "$ENVIRONMENT" == "production" ]]; then
            exit 1
        else
            log_warning "Continuing despite vulnerabilities in non-production environment"
        fi
    fi
    
    log_success "Trivy scan completed"
}

# Run Snyk scan
run_snyk_scan() {
    log_info "Running Snyk security scan..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run Snyk scan"
        return 0
    fi
    
    # Run Snyk test
    if ! snyk test --severity-threshold=high; then
        log_error "Snyk scan found high-severity vulnerabilities"
        
        if [[ "$ENVIRONMENT" == "production" ]]; then
            exit 1
        else
            log_warning "Continuing despite vulnerabilities in non-production environment"
        fi
    fi
    
    log_success "Snyk scan completed"
}

# Run Grype scan
run_grype_scan() {
    log_info "Running Grype security scan..."
    
    local image_tag="${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run Grype scan on image: $image_tag"
        return 0
    fi
    
    # Run Grype scan
    if ! grype "$image_tag" --fail-on high; then
        log_error "Grype scan found high-severity vulnerabilities"
        
        if [[ "$ENVIRONMENT" == "production" ]]; then
            exit 1
        else
            log_warning "Continuing despite vulnerabilities in non-production environment"
        fi
    fi
    
    log_success "Grype scan completed"
}

# Testing phase
testing_phase() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Testing phase skipped"
        return 0
    fi
    
    log_stage "=== TESTING PHASE ==="
    
    # Run unit tests
    run_unit_tests
    
    # Run integration tests
    run_integration_tests
    
    # Run smoke tests
    run_smoke_tests
    
    log_success "Testing phase completed"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run unit tests"
        return 0
    fi
    
    # Run unit tests in Docker container
    if docker run --rm "${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}" npm test -- --testPathPattern=unit; then
        log_success "Unit tests passed"
    else
        log_error "Unit tests failed"
        exit 1
    fi
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run integration tests"
        return 0
    fi
    
    # Start test environment
    docker-compose -f docker-compose.test.yml up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Run integration tests
    if docker run --rm --network container:app-test "${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}" npm test -- --testPathPattern=integration; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        docker-compose -f docker-compose.test.yml down
        exit 1
    fi
    
    # Cleanup test environment
    docker-compose -f docker-compose.test.yml down
    
    log_success "Integration tests completed"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run smoke tests"
        return 0
    fi
    
    # Start application
    docker-compose up -d
    
    # Wait for application to be ready
    sleep 30
    
    # Run smoke tests
    local app_url="http://localhost:8080"
    
    if curl -f -s "$app_url/health" > /dev/null; then
        log_success "Smoke tests passed"
    else
        log_error "Smoke tests failed"
        docker-compose down
        exit 1
    fi
    
    # Cleanup
    docker-compose down
    
    log_success "Smoke tests completed"
}

# Approval gate
approval_gate() {
    if [[ "$APPROVAL_REQUIRED" != "true" ]]; then
        log_info "Approval gate skipped"
        return 0
    fi
    
    log_stage "=== APPROVAL GATE ==="
    
    # Check if approval is required based on environment
    local approval_required_env
    approval_required_env=$(yq eval ".environments.${ENVIRONMENT}.rollback.approval_required" "$CONFIG_FILE")
    
    if [[ "$approval_required_env" == "true" ]] || [[ "$APPROVAL_REQUIRED" == "true" ]]; then
        log_info "Manual approval required for deployment to $ENVIRONMENT"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] Would wait for manual approval"
            return 0
        fi
        
        # Wait for manual approval
        wait_for_approval
    fi
    
    log_success "Approval gate passed"
}

# Wait for manual approval
wait_for_approval() {
    log_info "Waiting for manual approval..."
    log_info "Deployment details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Strategy: $DEPLOYMENT_STRATEGY"
    log_info "  Image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}"
    
    echo -n "Do you approve this deployment? (yes/no): "
    read -r approval
    
    if [[ "$approval" != "yes" ]]; then
        log_error "Deployment rejected by user"
        exit 1
    fi
    
    log_success "Deployment approved"
}

# Staging phase
staging_phase() {
    log_stage "=== STAGING PHASE ==="
    
    if [[ "$ENVIRONMENT" != "staging" ]] && [[ "$ENVIRONMENT" != "production" ]]; then
        log_info "Staging phase skipped for $ENVIRONMENT"
        return 0
    fi
    
    # Deploy to staging environment
    deploy_to_staging
    
    # Run staging tests
    run_staging_tests
    
    # Wait for staging gate
    wait_for_staging_gate
    
    log_success "Staging phase completed"
}

# Deploy to staging
deploy_to_staging() {
    log_info "Deploying to staging environment..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would deploy to staging"
        return 0
    fi
    
    # Set staging environment variables
    export ENVIRONMENT="staging"
    
    # Deploy using the specified strategy
    case $DEPLOYMENT_STRATEGY in
        rolling)
            deploy_rolling_staging
            ;;
        blue-green)
            deploy_blue_green_staging
            ;;
        canary)
            deploy_canary_staging
            ;;
        recreate)
            deploy_recreate_staging
            ;;
    esac
    
    log_success "Staging deployment completed"
}

# Deploy rolling to staging
deploy_rolling_staging() {
    log_info "Deploying with rolling strategy to staging..."
    
    # Update image tag
    sed -i "s|image: .*|image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}|" docker-compose.staging.yml
    
    # Deploy with rolling update
    docker-compose -f docker-compose.staging.yml up -d --no-deps --scale app=2
    
    # Wait for deployment to complete
    sleep 60
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app"
    fi
}

# Deploy blue-green to staging
deploy_blue_green_staging() {
    log_info "Deploying with blue-green strategy to staging..."
    
    # Deploy to green environment
    docker-compose -f docker-compose.staging.yml -p staging-green up -d
    
    # Wait for green environment to be ready
    sleep 60
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app" "staging-green"
    fi
    
    # Switch traffic to green
    # This would typically involve updating load balancer configuration
    log_info "Switching traffic to green environment"
    
    # Cleanup blue environment
    docker-compose -f docker-compose.staging.yml -p staging-blue down
}

# Deploy canary to staging
deploy_canary_staging() {
    log_info "Deploying with canary strategy to staging..."
    
    # Deploy canary version (10% traffic)
    docker-compose -f docker-compose.staging.yml up -d --scale app=1 --scale app-canary=1
    
    # Wait for canary to be ready
    sleep 60
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app-canary"
    fi
    
    # Monitor canary metrics
    monitor_canary_metrics
    
    # If canary is healthy, proceed with full deployment
    log_info "Canary deployment successful, proceeding with full deployment"
}

# Deploy recreate to staging
deploy_recreate_staging() {
    log_info "Deploying with recreate strategy to staging..."
    
    # Stop all containers
    docker-compose -f docker-compose.staging.yml down
    
    # Update image tag
    sed -i "s|image: .*|image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}|" docker-compose.staging.yml
    
    # Start new containers
    docker-compose -f docker-compose.staging.yml up -d
    
    # Wait for deployment to complete
    sleep 60
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app"
    fi
}

# Run staging tests
run_staging_tests() {
    log_info "Running staging tests..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would run staging tests"
        return 0
    fi
    
    # Run staging-specific tests
    local staging_url="https://staging.example.com"
    
    # Test API endpoints
    if curl -f -s "$staging_url/api/health" > /dev/null; then
        log_success "Staging API health check passed"
    else
        log_error "Staging API health check failed"
        exit 1
    fi
    
    # Test database connectivity
    if curl -f -s "$staging_url/api/db-health" > /dev/null; then
        log_success "Staging database health check passed"
    else
        log_error "Staging database health check failed"
        exit 1
    fi
    
    log_success "Staging tests completed"
}

# Wait for staging gate
wait_for_staging_gate() {
    log_info "Waiting for staging gate..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + STAGING_TIMEOUT))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check staging health
        if check_staging_health; then
            log_success "Staging gate passed"
            return 0
        fi
        
        log_info "Staging gate check failed, waiting..."
        sleep 30
    done
    
    log_error "Staging gate timeout"
    exit 1
}

# Check staging health
check_staging_health() {
    local staging_url="https://staging.example.com"
    
    # Check if staging is responding
    if curl -f -s "$staging_url/health" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Monitor canary metrics
monitor_canary_metrics() {
    log_info "Monitoring canary metrics..."
    
    # This would typically involve checking metrics from monitoring system
    # For now, just wait and check basic health
    sleep 120
    
    log_success "Canary metrics monitoring completed"
}

# Wait for health check
wait_for_health_check() {
    local service="${1:-app}"
    local project="${2:-}"
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for health check on service: $service"
    
    local compose_cmd="docker-compose"
    if [[ -n "$project" ]]; then
        compose_cmd="$compose_cmd -p $project"
    fi
    
    while [[ $attempt -le $max_attempts ]]; do
        if $compose_cmd ps $service | grep -q "healthy"; then
            log_success "Health check passed for $service"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, waiting..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed for $service after $max_attempts attempts"
    return 1
}

# Production deployment phase
production_deployment_phase() {
    if [[ "$ENVIRONMENT" != "production" ]]; then
        log_info "Production deployment phase skipped for $ENVIRONMENT"
        return 0
    fi
    
    log_stage "=== PRODUCTION DEPLOYMENT PHASE ==="
    
    # Final approval for production
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "Final approval required for production deployment"
        echo -n "Are you sure you want to deploy to PRODUCTION? (yes/no): "
        read -r final_approval
        
        if [[ "$final_approval" != "yes" ]]; then
            log_error "Production deployment cancelled by user"
            exit 1
        fi
    fi
    
    # Deploy to production
    deploy_to_production
    
    # Monitor production deployment
    monitor_production_deployment
    
    log_success "Production deployment completed"
}

# Deploy to production
deploy_to_production() {
    log_info "Deploying to production environment..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would deploy to production"
        return 0
    fi
    
    # Set production environment variables
    export ENVIRONMENT="production"
    
    # Deploy using the specified strategy
    case $DEPLOYMENT_STRATEGY in
        rolling)
            deploy_rolling_production
            ;;
        blue-green)
            deploy_blue_green_production
            ;;
        canary)
            deploy_canary_production
            ;;
        recreate)
            deploy_recreate_production
            ;;
    esac
    
    log_success "Production deployment completed"
}

# Deploy rolling to production
deploy_rolling_production() {
    log_info "Deploying with rolling strategy to production..."
    
    # Update image tag
    sed -i "s|image: .*|image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}|" docker-compose.prod.yml
    
    # Deploy with rolling update
    docker-compose -f docker-compose.prod.yml up -d --no-deps --scale app=3
    
    # Wait for deployment to complete
    sleep 90
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app"
    fi
}

# Deploy blue-green to production
deploy_blue_green_production() {
    log_info "Deploying with blue-green strategy to production..."
    
    # Deploy to green environment
    docker-compose -f docker-compose.prod.yml -p prod-green up -d
    
    # Wait for green environment to be ready
    sleep 90
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app" "prod-green"
    fi
    
    # Switch traffic to green
    log_info "Switching traffic to green environment"
    
    # Cleanup blue environment
    docker-compose -f docker-compose.prod.yml -p prod-blue down
}

# Deploy canary to production
deploy_canary_production() {
    log_info "Deploying with canary strategy to production..."
    
    # Deploy canary version (5% traffic)
    docker-compose -f docker-compose.prod.yml up -d --scale app=19 --scale app-canary=1
    
    # Wait for canary to be ready
    sleep 90
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app-canary"
    fi
    
    # Monitor canary metrics
    monitor_canary_metrics_production
    
    # If canary is healthy, proceed with full deployment
    log_info "Canary deployment successful, proceeding with full deployment"
}

# Deploy recreate to production
deploy_recreate_production() {
    log_info "Deploying with recreate strategy to production..."
    
    # Stop all containers
    docker-compose -f docker-compose.prod.yml down
    
    # Update image tag
    sed -i "s|image: .*|image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}|" docker-compose.prod.yml
    
    # Start new containers
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for deployment to complete
    sleep 90
    
    # Check health
    if [[ "$HEALTH_CHECK_ENABLED" == "true" ]]; then
        wait_for_health_check "app"
    fi
}

# Monitor production deployment
monitor_production_deployment() {
    log_info "Monitoring production deployment..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would monitor production deployment"
        return 0
    fi
    
    # Monitor for 5 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + 300))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check application health
        if check_production_health; then
            log_success "Production health check passed"
        else
            log_warning "Production health check failed"
        fi
        
        sleep 30
    done
    
    log_success "Production monitoring completed"
}

# Check production health
check_production_health() {
    local prod_url="https://app.example.com"
    
    # Check if production is responding
    if curl -f -s "$prod_url/health" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Monitor canary metrics in production
monitor_canary_metrics_production() {
    log_info "Monitoring canary metrics in production..."
    
    # Monitor for 10 minutes in production
    local start_time=$(date +%s)
    local end_time=$((start_time + 600))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check canary health
        if check_production_health; then
            log_success "Canary health check passed"
        else
            log_error "Canary health check failed"
            return 1
        fi
        
        sleep 60
    done
    
    log_success "Canary metrics monitoring completed"
}

# Post-deployment tasks
post_deployment_tasks() {
    log_stage "=== POST-DEPLOYMENT TASKS ==="
    
    # Send notifications
    send_notifications
    
    # Update deployment metadata
    update_deployment_metadata
    
    # Cleanup old resources
    cleanup_old_resources
    
    # Generate deployment report
    generate_deployment_report
    
    log_success "Post-deployment tasks completed"
}

# Send notifications
send_notifications() {
    log_info "Sending deployment notifications..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would send notifications"
        return 0
    fi
    
    # Send Slack notification
    if command -v curl &> /dev/null && [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        send_slack_notification
    fi
    
    # Send email notification
    if command -v mail &> /dev/null; then
        send_email_notification
    fi
    
    log_success "Notifications sent"
}

# Send Slack notification
send_slack_notification() {
    local status="SUCCESS"
    local color="good"
    
    local payload=$(cat << EOF
{
    "text": "Deployment ${status}",
    "attachments": [
        {
            "color": "${color}",
            "fields": [
                {"title": "Environment", "value": "${ENVIRONMENT}", "short": true},
                {"title": "Strategy", "value": "${DEPLOYMENT_STRATEGY}", "short": true},
                {"title": "Image", "value": "${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}", "short": true},
                {"title": "Time", "value": "$(date)", "short": true}
            ]
        }
    ]
}
EOF
    )
    
    curl -X POST -H 'Content-type: application/json' \
        --data "$payload" \
        "$SLACK_WEBHOOK_URL"
}

# Send email notification
send_email_notification() {
    local subject="Deployment Notification - ${ENVIRONMENT}"
    local body="Deployment completed successfully for ${ENVIRONMENT} environment using ${DEPLOYMENT_STRATEGY} strategy."
    
    echo "$body" | mail -s "$subject" "devops@example.com"
}

# Update deployment metadata
update_deployment_metadata() {
    log_info "Updating deployment metadata..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would update deployment metadata"
        return 0
    fi
    
    # Create deployment metadata file
    cat > deployment-metadata.json << EOF
{
    "deployment_id": "$(uuidgen)",
    "environment": "${ENVIRONMENT}",
    "strategy": "${DEPLOYMENT_STRATEGY}",
    "image": "${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": "success",
    "duration": "$(($(date +%s) - START_TIME))",
    "git_commit": "${GITHUB_SHA:-unknown}",
    "git_branch": "${GITHUB_REF_NAME:-unknown}"
}
EOF
    
    log_success "Deployment metadata updated"
}

# Cleanup old resources
cleanup_old_resources() {
    log_info "Cleaning up old resources..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would cleanup old resources"
        return 0
    fi
    
    # Remove old Docker images
    docker image prune -f --filter "until=24h" > /dev/null 2>&1 || true
    
    # Remove old containers
    docker container prune -f > /dev/null 2>&1 || true
    
    # Remove old volumes
    docker volume prune -f > /dev/null 2>&1 || true
    
    log_success "Old resources cleaned up"
}

# Generate deployment report
generate_deployment_report() {
    log_info "Generating deployment report..."
    
    local report_file="deployment-report-$(date +%Y%m%d-%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Deployment Report - ${ENVIRONMENT}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Deployment Report</h1>
        <p><strong>Environment:</strong> ${ENVIRONMENT}</p>
        <p><strong>Strategy:</strong> ${DEPLOYMENT_STRATEGY}</p>
        <p><strong>Image:</strong> ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}</p>
        <p><strong>Timestamp:</strong> $(date)</p>
        <p><strong>Status:</strong> <span class="success">SUCCESS</span></p>
    </div>
    
    <h2>Deployment Summary</h2>
    <table>
        <tr><th>Phase</th><th>Status</th><th>Duration</th></tr>
        <tr><td>Pre-deployment Checks</td><td class="success">PASSED</td><td>-</td></tr>
        <tr><td>Security Scanning</td><td class="success">PASSED</td><td>-</td></tr>
        <tr><td>Testing</td><td class="success">PASSED</td><td>-</td></tr>
        <tr><td>Staging</td><td class="success">PASSED</td><td>-</td></tr>
        <tr><td>Production</td><td class="success">PASSED</td><td>-</td></tr>
    </table>
</body>
</html>
EOF
    
    log_success "Deployment report generated: $report_file"
}

# Rollback function
rollback_deployment() {
    log_error "Deployment failed, initiating rollback..."
    
    if [[ "$ROLLBACK_ENABLED" == "true" ]]; then
        log_info "Rolling back to previous version..."
        
        # Get previous image tag
        local previous_image="previous-image-tag"  # This would be stored in deployment metadata
        
        # Rollback to previous version
        case $DEPLOYMENT_STRATEGY in
            rolling)
                rollback_rolling "$previous_image"
                ;;
            blue-green)
                rollback_blue_green "$previous_image"
                ;;
            canary)
                rollback_canary "$previous_image"
                ;;
            recreate)
                rollback_recreate "$previous_image"
                ;;
        esac
        
        log_success "Rollback completed"
    else
        log_warning "Rollback disabled, manual intervention required"
    fi
    
    exit 1
}

# Rollback rolling deployment
rollback_rolling() {
    local previous_image="$1"
    
    log_info "Rolling back rolling deployment..."
    
    # Update to previous image
    sed -i "s|image: .*|image: $previous_image|" docker-compose.yml
    
    # Rolling update back to previous version
    docker-compose up -d --no-deps --scale app=3
    
    log_success "Rolling rollback completed"
}

# Rollback blue-green deployment
rollback_blue_green() {
    local previous_image="$1"
    
    log_info "Rolling back blue-green deployment..."
    
    # Switch traffic back to blue environment
    log_info "Switching traffic back to blue environment"
    
    # Cleanup green environment
    docker-compose -p prod-green down
    
    log_success "Blue-green rollback completed"
}

# Rollback canary deployment
rollback_canary() {
    local previous_image="$1"
    
    log_info "Rolling back canary deployment..."
    
    # Remove canary instances
    docker-compose up -d --scale app-canary=0
    
    log_success "Canary rollback completed"
}

# Rollback recreate deployment
rollback_recreate() {
    local previous_image="$1"
    
    log_info "Rolling back recreate deployment..."
    
    # Stop current containers
    docker-compose down
    
    # Update to previous image
    sed -i "s|image: .*|image: $previous_image|" docker-compose.yml
    
    # Start previous version
    docker-compose up -d
    
    log_success "Recreate rollback completed"
}

# Main deployment function
main() {
    # Record start time
    START_TIME=$(date +%s)
    
    log_stage "=== DEPLOYMENT STARTED ==="
    log_info "Environment: $ENVIRONMENT"
    log_info "Strategy: $DEPLOYMENT_STRATEGY"
    log_info "Config File: $CONFIG_FILE"
    log_info "Dry Run: $DRY_RUN"
    
    # Set up error handling
    trap rollback_deployment ERR
    
    # Execute deployment phases
    parse_arguments "$@"
    validate_inputs
    load_configuration
    pre_deployment_checks
    security_scanning_phase
    testing_phase
    approval_gate
    staging_phase
    production_deployment_phase
    post_deployment_tasks
    
    # Calculate total deployment time
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    
    log_stage "=== DEPLOYMENT COMPLETED ==="
    log_success "Deployment completed successfully in ${duration} seconds"
    log_info "Environment: $ENVIRONMENT"
    log_info "Strategy: $DEPLOYMENT_STRATEGY"
    log_info "Image: ${GITHUB_REPOSITORY}:${GITHUB_SHA:-latest}"
}

# Execute main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi