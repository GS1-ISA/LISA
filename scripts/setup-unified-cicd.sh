#!/bin/bash

# Unified CI/CD Setup Script
# This script initializes and configures the unified CI/CD pipeline

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_DIR="${PROJECT_ROOT}/config"
LOGS_DIR="${PROJECT_ROOT}/logs"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running on supported OS
    if [[ "$OSTYPE" != "linux-gnu"* && "$OSTYPE" != "darwin"* ]]; then
        error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("git" "curl" "jq" "docker" "docker-compose")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        error "Missing required tools: ${missing_tools[*]}"
        error "Please install the missing tools and try again."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    local directories=(
        "$CONFIG_DIR"
        "$LOGS_DIR"
        "$BACKUP_DIR"
        "$CONFIG_DIR/environments"
        "$CONFIG_DIR/security"
        "$CONFIG_DIR/deployment"
        "$CONFIG_DIR/performance"
        "$PROJECT_ROOT/security-reports"
        "$PROJECT_ROOT/compliance-reports"
        "$PROJECT_ROOT/performance-reports"
        "$PROJECT_ROOT/deployment-logs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
    
    success "Directory structure created"
}

# Initialize configuration files
initialize_config() {
    log "Initializing configuration files..."
    
    # Main configuration file
    cat > "$CONFIG_DIR/unified-cicd.conf" << 'EOF'
# Unified CI/CD Configuration

# General settings
PROJECT_NAME="unified-cicd"
ENVIRONMENTS="development,staging,production"
DEPLOYMENT_TIMEOUT=1800
ROLLBACK_ENABLED=true

# Security settings
SECURITY_SCAN_ENABLED=true
COMPLIANCE_CHECK_ENABLED=true
VULNERABILITY_THRESHOLD=high
SECRET_SCAN_ENABLED=true

# Performance settings
PERFORMANCE_TEST_ENABLED=true
LOAD_TEST_ENABLED=true
STRESS_TEST_ENABLED=true
PERFORMANCE_THRESHOLD=95

# Deployment settings
DEFAULT_DEPLOYMENT_STRATEGY="blue-green"
SUPPORTED_STRATEGIES="rolling,blue-green,canary"
MAX_CONCURRENT_DEPLOYMENTS=3

# Notification settings
NOTIFICATION_ENABLED=true
SLACK_WEBHOOK_URL=""
EMAIL_NOTIFICATIONS=true

# Caching settings
CACHE_ENABLED=true
CACHE_TTL=3600
DOCKER_CACHE_ENABLED=true
DEPENDENCY_CACHE_ENABLED=true
EOF

    # Environment-specific configurations
    for env in development staging production; do
        cat > "$CONFIG_DIR/environments/${env}.conf" << EOF
# ${env^} Environment Configuration

ENVIRONMENT_NAME="$env"
DEPLOYMENT_STRATEGY="blue-green"
HEALTH_CHECK_ENABLED=true
PERFORMANCE_MONITORING_ENABLED=true
ROLLBACK_THRESHOLD=5
MAX_DEPLOYMENT_TIME=1800

# Resource limits
CPU_LIMIT="1000m"
MEMORY_LIMIT="1Gi"
REPLICA_COUNT=3

# Health check settings
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3

# Performance thresholds
RESPONSE_TIME_THRESHOLD=2000
ERROR_RATE_THRESHOLD=5
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
EOF
    done

    # Security configuration
    cat > "$CONFIG_DIR/security/security.conf" << 'EOF'
# Security Configuration

# SCA (Software Composition Analysis)
SCA_ENABLED=true
SCA_TOOLS="snyk,grype"
SCA_SEVERITY_THRESHOLD=high

# Container Security
CONTAINER_SCAN_ENABLED=true
CONTAINER_SCAN_TOOLS="trivy,clair"
CONTAINER_SEVERITY_THRESHOLD=medium

# SAST (Static Application Security Testing)
SAST_ENABLED=true
SAST_TOOLS="semgrep,sonarqube"
SAST_SEVERITY_THRESHOLD=medium

# Secret Detection
SECRET_SCAN_ENABLED=true
SECRET_SCAN_TOOLS="truffleHog,gitleaks"
SECRET_SEVERITY_THRESHOLD=critical

# Compliance
COMPLIANCE_ENABLED=true
COMPLIANCE_STANDARDS="soc2,hipaa,pci-dss"
COMPLIANCE_SEVERITY_THRESHOLD=medium
EOF

    # Deployment configuration
    cat > "$CONFIG_DIR/deployment/deployment.conf" << 'EOF'
# Deployment Configuration

# Deployment strategies
ROLLING_UPDATE_ENABLED=true
BLUE_GREEN_ENABLED=true
CANARY_ENABLED=true

# Rolling deployment settings
ROLLING_MAX_UNAVAILABLE=1
ROLLING_MAX_SURGE=1

# Blue-green deployment settings
BLUE_GREEN_SWITCH_TIMEOUT=300
BLUE_GREEN_HEALTH_CHECK_ENABLED=true

# Canary deployment settings
CANARY_TRAFFIC_INCREMENT=10
CANARY_TRAFFIC_INTERVAL=60
CANARY_SUCCESS_THRESHOLD=95

# Rollback settings
ROLLBACK_ENABLED=true
ROLLBACK_TIMEOUT=600
ROLLBACK_VERIFICATION_ENABLED=true
AUTO_ROLLBACK_ENABLED=true

# Health check settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
EOF

    # Performance configuration
    cat > "$CONFIG_DIR/performance/performance.conf" << 'EOF'
# Performance Testing Configuration

# Load testing
LOAD_TEST_ENABLED=true
LOAD_TEST_TOOL="k6"
LOAD_TEST_DURATION=300
LOAD_TEST_VUS=100
LOAD_TEST_RAMP_UP=60

# Stress testing
STRESS_TEST_ENABLED=true
STRESS_TEST_TOOL="k6"
STRESS_TEST_DURATION=600
STRESS_TEST_VUS=1000
STRESS_TEST_RAMP_UP=120

# Performance thresholds
RESPONSE_TIME_THRESHOLD=2000
ERROR_RATE_THRESHOLD=5
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
THROUGHPUT_THRESHOLD=1000

# Monitoring
PERFORMANCE_MONITORING_ENABLED=true
METRICS_COLLECTION_ENABLED=true
ALERTING_ENABLED=true
EOF

    success "Configuration files initialized"
}

# Setup GitHub Actions workflow
setup_github_actions() {
    log "Setting up GitHub Actions workflow..."
    
    # Create .github directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/.github/workflows"
    
    # The unified workflow should already be created, but let's verify it
    if [[ -f "$PROJECT_ROOT/.github/workflows/unified-cicd.yml" ]]; then
        success "Unified CI/CD workflow already exists"
    else
        warning "Unified CI/CD workflow not found. Please ensure it's created."
    fi
    
    # Create workflow templates for common scenarios
    mkdir -p "$PROJECT_ROOT/.github/workflow-templates"
    
    cat > "$PROJECT_ROOT/.github/workflow-templates/security-only.yml" << 'EOF'
name: Security Only
on:
  pull_request:
    branches: [ main, develop ]
jobs:
  security:
    uses: ./.github/workflows/unified-cicd.yml
    with:
      environment: development
      skip_tests: true
    secrets: inherit
EOF

    cat > "$PROJECT_ROOT/.github/workflow-templates/performance-only.yml" << 'EOF'
name: Performance Only
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:
jobs:
  performance:
    uses: ./.github/workflows/unified-cicd.yml
    with:
      environment: staging
      deployment_strategy: canary
    secrets: inherit
EOF

    success "GitHub Actions workflow setup completed"
}

# Setup security tools
setup_security_tools() {
    log "Setting up security tools..."
    
    # Create security tool installation script
    cat > "$SCRIPT_DIR/install-security-tools.sh" << 'EOF'
#!/bin/bash

# Install security scanning tools

# Install Trivy for container scanning
if ! command -v trivy &> /dev/null; then
    echo "Installing Trivy..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

# Install Grype for vulnerability scanning
if ! command -v grype &> /dev/null; then
    echo "Installing Grype..."
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
fi

# Install Semgrep for SAST
if ! command -v semgrep &> /dev/null; then
    echo "Installing Semgrep..."
    python3 -m pip install semgrep
fi

# Install TruffleHog for secret scanning
if ! command -v trufflehog &> /dev/null; then
    echo "Installing TruffleHog..."
    curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
fi

# Install K6 for performance testing
if ! command -v k6 &> /dev/null; then
    echo "Installing K6..."
    sudo gpg -k
    sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
    sudo apt-get update
    sudo apt-get install k6
fi

echo "Security tools installation completed"
EOF

    chmod +x "$SCRIPT_DIR/install-security-tools.sh"
    
    # Run the installation script
    log "Installing security tools..."
    "$SCRIPT_DIR/install-security-tools.sh"
    
    success "Security tools setup completed"
}

# Setup monitoring and alerting
setup_monitoring() {
    log "Setting up monitoring and alerting..."
    
    # Create monitoring configuration
    cat > "$CONFIG_DIR/monitoring.conf" << 'EOF'
# Monitoring Configuration

# Health check endpoints
HEALTH_CHECK_ENDPOINT="/health"
METRICS_ENDPOINT="/metrics"
STATUS_ENDPOINT="/status"

# Monitoring intervals
HEALTH_CHECK_INTERVAL=30
METRICS_COLLECTION_INTERVAL=60
ALERT_CHECK_INTERVAL=300

# Alert thresholds
ERROR_RATE_THRESHOLD=5
RESPONSE_TIME_THRESHOLD=2000
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=90

# Notification channels
SLACK_WEBHOOK_URL=""
EMAIL_SMTP_SERVER=""
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=""
EMAIL_PASSWORD=""

# PagerDuty integration
PAGERDUTY_INTEGRATION_KEY=""
PAGERDUTY_SERVICE_KEY=""

# Webhook notifications
WEBHOOK_URL=""
WEBHOOK_SECRET=""
EOF

    # Create monitoring script
    cat > "$SCRIPT_DIR/monitoring.sh" << 'EOF'
#!/bin/bash

# Monitoring and alerting script

CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/config/monitoring.conf"

# Source the configuration
source "$CONFIG_FILE"

# Function to send Slack notification
send_slack_notification() {
    local message="$1"
    local severity="$2"
    
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\",\"severity\":\"$severity\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Function to send email notification
send_email_notification() {
    local subject="$1"
    local body="$2"
    
    if [[ -n "$EMAIL_SMTP_SERVER" ]]; then
        echo "$body" | mail -s "$subject" -S smtp="$EMAIL_SMTP_SERVER:$EMAIL_SMTP_PORT" \
            -S smtp-use-starttls -S smtp-auth=login \
            -S smtp-auth-user="$EMAIL_USERNAME" -S smtp-auth-password="$EMAIL_PASSWORD"
    fi
}

# Function to check health
check_health() {
    local endpoint="$1"
    local timeout=10
    
    if curl -f -s --max-time "$timeout" "$endpoint" > /dev/null; then
        echo "healthy"
    else
        echo "unhealthy"
    fi
}

# Function to collect metrics
collect_metrics() {
    local endpoint="$1"
    
    curl -s "$endpoint" || echo "{}"
}

# Main monitoring loop
main() {
    while true; do
        # Health checks
        health_status=$(check_health "$HEALTH_CHECK_ENDPOINT")
        
        if [[ "$health_status" == "unhealthy" ]]; then
            send_slack_notification "Health check failed for $HEALTH_CHECK_ENDPOINT" "critical"
            send_email_notification "Health Check Alert" "Health check failed for $HEALTH_CHECK_ENDPOINT"
        fi
        
        # Metrics collection
        metrics=$(collect_metrics "$METRICS_ENDPOINT")
        
        # Alert checking logic would go here
        # This is a simplified version
        
        sleep "$HEALTH_CHECK_INTERVAL"
    done
}

# Run monitoring if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF

    chmod +x "$SCRIPT_DIR/monitoring.sh"
    
    success "Monitoring and alerting setup completed"
}

# Create backup and restore functionality
setup_backup_restore() {
    log "Setting up backup and restore functionality..."
    
    # Create backup script
    cat > "$SCRIPT_DIR/backup-config.sh" << 'EOF'
#!/bin/bash

# Backup configuration script

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/backups"
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup
create_backup() {
    local backup_name="config_backup_${TIMESTAMP}"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    mkdir -p "$backup_path"
    
    # Copy configuration files
    cp -r "$CONFIG_DIR" "$backup_path/"
    
    # Copy GitHub workflows
    cp -r "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.github" "$backup_path/"
    
    # Copy scripts
    cp -r "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts" "$backup_path/"
    
    # Create tarball
    tar -czf "${backup_path}.tar.gz" -C "$BACKUP_DIR" "$backup_name"
    
    # Remove temporary directory
    rm -rf "$backup_path"
    
    echo "Backup created: ${backup_path}.tar.gz"
}

# List backups
list_backups() {
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "No backups found"
}

# Restore backup
restore_backup() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        echo "Backup file not found: $backup_file"
        exit 1
    fi
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Find the extracted directory
    local extracted_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "config_backup_*")
    
    if [[ -z "$extracted_dir" ]]; then
        echo "Invalid backup file structure"
        exit 1
    fi
    
    # Restore configuration
    cp -r "${extracted_dir}/config" "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/"
    
    # Restore GitHub workflows
    cp -r "${extracted_dir}/.github" "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/"
    
    # Restore scripts
    cp -r "${extracted_dir}/scripts" "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/"
    
    # Cleanup
    rm -rf "$temp_dir"
    
    echo "Backup restored from: $backup_file"
}

# Main function
main() {
    case "${1:-}" in
        create)
            create_backup
            ;;
        list)
            list_backups
            ;;
        restore)
            if [[ -z "${2:-}" ]]; then
                echo "Usage: $0 restore <backup_file>"
                exit 1
            fi
            restore_backup "$2"
            ;;
        *)
            echo "Usage: $0 {create|list|restore}"
            echo "  create  - Create a new backup"
            echo "  list    - List available backups"
            echo "  restore - Restore from backup file"
            exit 1
            ;;
    esac
}

main "$@"
EOF

    chmod +x "$SCRIPT_DIR/backup-config.sh"
    
    success "Backup and restore functionality setup completed"
}

# Main setup function
main() {
    log "Starting Unified CI/CD setup..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create directory structure
    create_directories
    
    # Initialize configuration
    initialize_config
    
    # Setup GitHub Actions
    setup_github_actions
    
    # Setup security tools
    setup_security_tools
    
    # Setup monitoring
    setup_monitoring
    
    # Setup backup and restore
    setup_backup_restore
    
    # Create setup completion marker
    touch "$PROJECT_ROOT/.unified-cicd-setup-complete"
    
    success "Unified CI/CD setup completed successfully!"
    log "Next steps:"
    log "1. Review and customize configuration files in $CONFIG_DIR"
    log "2. Set up GitHub repository secrets for cloud provider access"
    log "3. Configure notification channels (Slack, email, etc.)"
    log "4. Test the pipeline in development environment"
    log "5. Run: ./scripts/unified-cicd-pipeline.sh --help for usage information"
    log "6. Create your first deployment with: ./scripts/unified-cicd-pipeline.sh deploy development"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi