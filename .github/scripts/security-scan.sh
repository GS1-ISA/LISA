#!/bin/bash
set -euo pipefail

# Comprehensive Security Scanning Script
# Usage: ./security-scan.sh <scan-type> <output-format> <severity-threshold>

SCAN_TYPE=${1:-"all"}
OUTPUT_FORMAT=${2:-"sarif"}
SEVERITY_THRESHOLD=${3:-"HIGH"}
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

log_scan() {
    echo -e "${PURPLE}[SCAN]${NC} $1"
}

# Error handling
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Error occurred on line $line_number with exit code $error_code"
    exit $error_code
}

trap 'handle_error $LINENO $?' ERR

# Initialize scan results
SCAN_RESULTS_DIR="security-scan-results"
mkdir -p "$SCAN_RESULTS_DIR"
SCAN_SUMMARY="$SCAN_RESULTS_DIR/scan-summary.json"
SCAN_EXIT_CODE=0

# Initialize summary
cat > "$SCAN_SUMMARY" <<EOF
{
  "scan_id": "$(date +%s)",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "${GITHUB_REPOSITORY:-unknown}",
  "commit_sha": "${GITHUB_SHA:-unknown}",
  "scan_type": "$SCAN_TYPE",
  "results": {},
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  }
}
EOF

# Function to update summary
update_summary() {
    local tool=$1
    local severity=$2
    local count=$3
    
    # Update tool-specific results
    if ! jq -e ".results.$tool" "$SCAN_SUMMARY" > /dev/null 2>&1; then
        jq ".results.$tool = {}" "$SCAN_SUMMARY" > "$SCAN_SUMMARY.tmp" && mv "$SCAN_SUMMARY.tmp" "$SCAN_SUMMARY"
    fi
    
    jq ".results.$tool.$severity = $count" "$SCAN_SUMMARY" > "$SCAN_SUMMARY.tmp" && mv "$SCAN_SUMMARY.tmp" "$SCAN_SUMMARY"
    
    # Update overall summary
    local current_count=$(jq -r ".summary.$severity" "$SCAN_SUMMARY")
    local new_count=$((current_count + count))
    jq ".summary.$severity = $new_count" "$SCAN_SUMMARY" > "$SCAN_SUMMARY.tmp" && mv "$SCAN_SUMMARY.tmp" "$SCAN_SUMMARY"
    
    local total=$(jq -r ".summary.total_findings" "$SCAN_SUMMARY")
    jq ".summary.total_findings = $((total + count))" "$SCAN_SUMMARY" > "$SCAN_SUMMARY.tmp" && mv "$SCAN_SUMMARY.tmp" "$SCAN_SUMMARY"
}

# Function to check severity threshold
check_severity_threshold() {
    local severity=$1
    local count=$2
    
    case "$SEVERITY_THRESHOLD" in
        "CRITICAL")
            [[ "$severity" == "critical" && $count -gt 0 ]] && return 1
            ;;
        "HIGH")
            [[ "$severity" =~ ^(critical|high)$ && $count -gt 0 ]] && return 1
            ;;
        "MEDIUM")
            [[ "$severity" =~ ^(critical|high|medium)$ && $count -gt 0 ]] && return 1
            ;;
        "LOW")
            [[ $count -gt 0 ]] && return 1
            ;;
    esac
    
    return 0
}

# Python dependency vulnerability scanning
scan_dependencies() {
    log_scan "Starting dependency vulnerability scan..."
    
    local output_file="$SCAN_RESULTS_DIR/dependency-scan.json"
    local exit_code=0
    
    # Check if requirements files exist
    if [[ ! -f "requirements.txt" && ! -f "requirements-dev.txt" && ! -f "pyproject.toml" ]]; then
        log_warning "No Python dependency files found, skipping dependency scan"
        return 0
    fi
    
    # Install pip-audit if not available
    if ! command -v pip-audit >/dev/null 2>&1; then
        log_info "Installing pip-audit..."
        pip install pip-audit >/dev/null 2>&1
    fi
    
    # Run pip-audit
    log_info "Running pip-audit..."
    if pip-audit --desc --format=json --output="$output_file" --requirement=requirements.txt 2>/dev/null; then
        log_success "Dependency scan completed"
        
        # Parse results
        if [[ -f "$output_file" ]]; then
            local vuln_count=$(jq '.vulnerabilities | length' "$output_file" 2>/dev/null || echo "0")
            local critical_count=$(jq '[.vulnerabilities[] | select(.severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
            local high_count=$(jq '[.vulnerabilities[] | select(.severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
            local medium_count=$(jq '[.vulnerabilities[] | select(.severity == "MEDIUM")] | length' "$output_file" 2>/dev/null || echo "0")
            local low_count=$(jq '[.vulnerabilities[] | select(.severity == "LOW")] | length' "$output_file" 2>/dev/null || echo "0")
            
            update_summary "dependencies" "critical" "$critical_count"
            update_summary "dependencies" "high" "$high_count"
            update_summary "dependencies" "medium" "$medium_count"
            update_summary "dependencies" "low" "$low_count"
            
            # Check thresholds
            if ! check_severity_threshold "critical" "$critical_count"; then
                log_error "Critical vulnerabilities found in dependencies"
                exit_code=1
            fi
            
            if ! check_severity_threshold "high" "$high_count"; then
                log_error "High severity vulnerabilities found in dependencies"
                exit_code=1
            fi
        fi
    else
        log_error "Dependency scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# Python code security scanning with Bandit
scan_code_security() {
    log_scan "Starting code security scan..."
    
    local output_file="$SCAN_RESULTS_DIR/code-security-scan.json"
    local exit_code=0
    
    # Install bandit if not available
    if ! command -v bandit >/dev/null 2>&1; then
        log_info "Installing bandit..."
        pip install bandit >/dev/null 2>&1
    fi
    
    # Find Python files to scan
    local python_files=$(find . -name "*.py" -not -path "./tests/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./build/*" -not -path "./dist/*" | head -100)
    
    if [[ -z "$python_files" ]]; then
        log_warning "No Python files found to scan"
        return 0
    fi
    
    log_info "Scanning Python code files..."
    
    # Run bandit
    if echo "$python_files" | xargs bandit -f json -o "$output_file" -r 2>/dev/null; then
        log_success "Code security scan completed"
        
        # Parse results
        if [[ -f "$output_file" ]]; then
            local issue_count=$(jq '.results | length' "$output_file" 2>/dev/null || echo "0")
            local critical_count=$(jq '[.results[] | select(.issue_severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
            local high_count=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
            local medium_count=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "$output_file" 2>/dev/null || echo "0")
            local low_count=$(jq '[.results[] | select(.issue_severity == "LOW")] | length' "$output_file" 2>/dev/null || echo "0")
            
            update_summary "code_security" "critical" "$critical_count"
            update_summary "code_security" "high" "$high_count"
            update_summary "code_security" "medium" "$medium_count"
            update_summary "code_security" "low" "$low_count"
            
            # Check thresholds
            if ! check_severity_threshold "critical" "$critical_count"; then
                log_error "Critical security issues found in code"
                exit_code=1
            fi
            
            if ! check_severity_threshold "high" "$high_count"; then
                log_error "High severity security issues found in code"
                exit_code=1
            fi
        fi
    else
        log_error "Code security scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# Secret scanning with detect-secrets
scan_secrets() {
    log_scan "Starting secret scanning..."
    
    local output_file="$SCAN_RESULTS_DIR/secret-scan.json"
    local exit_code=0
    
    # Install detect-secrets if not available
    if ! command -v detect-secrets >/dev/null 2>&1; then
        log_info "Installing detect-secrets..."
        pip install detect-secrets >/dev/null 2>&1
    fi
    
    # Create baseline if it doesn't exist
    if [[ ! -f ".secrets.baseline" ]]; then
        log_info "Creating secrets baseline..."
        detect-secrets scan --all-files --baseline .secrets.baseline >/dev/null 2>&1
    fi
    
    log_info "Scanning for secrets..."
    
    # Run detect-secrets
    if detect-secrets scan --all-files --baseline .secrets.baseline --json > "$output_file" 2>/dev/null; then
        log_success "Secret scan completed"
        
        # Parse results
        if [[ -f "$output_file" ]]; then
            local secret_count=$(jq '[.results[] | length] | add' "$output_file" 2>/dev/null || echo "0")
            
            if [[ $secret_count -gt 0 ]]; then
                log_error "Potential secrets found: $secret_count"
                update_summary "secrets" "high" "$secret_count"
                exit_code=1
            else
                update_summary "secrets" "high" "0"
                log_success "No secrets detected"
            fi
        fi
    else
        log_error "Secret scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# Container image scanning with Trivy
scan_container() {
    log_scan "Starting container image scan..."
    
    local image_name=${1:-""}
    local output_file="$SCAN_RESULTS_DIR/container-scan.json"
    local exit_code=0
    
    if [[ -z "$image_name" ]]; then
        log_warning "No container image specified, skipping container scan"
        return 0
    fi
    
    # Install Trivy if not available
    if ! command -v trivy >/dev/null 2>&1; then
        log_info "Installing Trivy..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin >/dev/null 2>&1
    fi
    
    log_info "Scanning container image: $image_name"
    
    # Run Trivy scan
    if trivy image --format json --output "$output_file" --severity CRITICAL,HIGH,MEDIUM "$image_name" >/dev/null 2>&1; then
        log_success "Container scan completed"
        
        # Parse results
        if [[ -f "$output_file" ]]; then
            local critical_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
            local high_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
            local medium_count=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM")] | length' "$output_file" 2>/dev/null || echo "0")
            
            update_summary "container" "critical" "$critical_count"
            update_summary "container" "high" "$high_count"
            update_summary "container" "medium" "$medium_count"
            
            # Check thresholds
            if ! check_severity_threshold "critical" "$critical_count"; then
                log_error "Critical vulnerabilities found in container image"
                exit_code=1
            fi
            
            if ! check_severity_threshold "high" "$high_count"; then
                log_error "High severity vulnerabilities found in container image"
                exit_code=1
            fi
        fi
    else
        log_error "Container scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# Infrastructure as Code scanning
scan_iac() {
    log_scan "Starting Infrastructure as Code scan..."
    
    local output_file="$SCAN_RESULTS_DIR/iac-scan.json"
    local exit_code=0
    
    # Find IaC files
    local terraform_files=$(find . -name "*.tf" -o -name "*.tfvars" | head -50)
    local k8s_files=$(find . -name "*.yaml" -o -name "*.yml" | grep -E "(k8s|kubernetes|deployment|service)" | head -50)
    
    if [[ -z "$terraform_files" && -z "$k8s_files" ]]; then
        log_warning "No IaC files found, skipping IaC scan"
        return 0
    fi
    
    # Install Checkov if not available
    if ! command -v checkov >/dev/null 2>&1; then
        log_info "Installing Checkov..."
        pip install checkov >/dev/null 2>&1
    fi
    
    log_info "Scanning Infrastructure as Code..."
    
    # Run Checkov
    local checkov_args=""
    [[ -n "$terraform_files" ]] && checkov_args="$checkov_args --directory ."
    [[ -n "$k8s_files" ]] && checkov_args="$checkov_args --kubernetes"
    
    if checkov $checkov_args --output json --output-file "$output_file" --quiet >/dev/null 2>&1; then
        log_success "IaC scan completed"
        
        # Parse results
        if [[ -f "$output_file" ]]; then
            local failed_count=$(jq '.summary.failed' "$output_file" 2>/dev/null || echo "0")
            local critical_count=$(jq '[.results.failed_checks[]? | select(.severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
            local high_count=$(jq '[.results.failed_checks[]? | select(.severity == "HIGH")] | length' "$output_file" 2>/dev/null || echo "0")
            
            update_summary "iac" "critical" "$critical_count"
            update_summary "iac" "high" "$high_count"
            update_summary "iac" "medium" "$failed_count"
            
            # Check thresholds
            if ! check_severity_threshold "critical" "$critical_count"; then
                log_error "Critical IaC security issues found"
                exit_code=1
            fi
            
            if ! check_severity_threshold "high" "$high_count"; then
                log_error "High severity IaC security issues found"
                exit_code=1
            fi
        fi
    else
        log_error "IaC scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# License compliance scanning
scan_licenses() {
    log_scan "Starting license compliance scan..."
    
    local output_file="$SCAN_RESULTS_DIR/license-scan.json"
    local exit_code=0
    
    # Check if requirements files exist
    if [[ ! -f "requirements.txt" ]]; then
        log_warning "No requirements.txt found, skipping license scan"
        return 0
    fi
    
    # Install pip-licenses if not available
    if ! command -v pip-licenses >/dev/null 2>&1; then
        log_info "Installing pip-licenses..."
        pip install pip-licenses >/dev/null 2>&1
    fi
    
    log_info "Scanning license compliance..."
    
    # Run pip-licenses
    if pip-licenses --format=json --output-file="$output_file" >/dev/null 2>&1; then
        log_success "License scan completed"
        
        # Parse results and check for problematic licenses
        if [[ -f "$output_file" ]]; then
            local gpl_count=$(jq '[.[] | select(.License | test("GPL"; "i"))] | length' "$output_file" 2>/dev/null || echo "0")
            local unknown_count=$(jq '[.[] | select(.License == "UNKNOWN" or .License == null)] | length' "$output_file" 2>/dev/null || echo "0")
            
            if [[ $gpl_count -gt 0 ]]; then
                log_warning "GPL licenses found: $gpl_count"
                update_summary "licenses" "high" "$gpl_count"
                exit_code=1
            fi
            
            if [[ $unknown_count -gt 0 ]]; then
                log_warning "Unknown licenses found: $unknown_count"
                update_summary "licenses" "medium" "$unknown_count"
            fi
            
            update_summary "licenses" "low" "0"
        fi
    else
        log_error "License scan failed"
        exit_code=1
    fi
    
    return $exit_code
}

# Generate SARIF output
generate_sarif() {
    log_info "Generating SARIF output..."
    
    local sarif_file="$SCAN_RESULTS_DIR/security-scan.sarif"
    
    cat > "$sarif_file" <<EOF
{
  "\$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Security Scan Suite",
          "informationUri": "https://github.com/${GITHUB_REPOSITORY}",
          "version": "1.0.0",
          "rules": []
        }
      },
      "results": [],
      "invocations": [
        {
          "executionSuccessful": true,
          "startTimeUtc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
          "endTimeUtc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        }
      ]
    }
  ]
}
EOF
    
    log_success "SARIF output generated: $sarif_file"
}

# Generate HTML report
generate_html_report() {
    log_info "Generating HTML report..."
    
    local html_file="$SCAN_RESULTS_DIR/security-scan-report.html"
    
    cat > "$html_file" <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>Security Scan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .critical { color: #d32f2f; font-weight: bold; }
        .high { color: #f57c00; font-weight: bold; }
        .medium { color: #fbc02d; }
        .low { color: #689f38; }
        .info { color: #0288d1; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .tool-result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .success { background-color: #e8f5e8; border: 1px solid #4caf50; }
        .warning { background-color: #fff3e0; border: 1px solid #ff9800; }
        .error { background-color: #ffebee; border: 1px solid #f44336; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Scan Report</h1>
        <p><strong>Repository:</strong> ${GITHUB_REPOSITORY:-unknown}</p>
        <p><strong>Commit:</strong> ${GITHUB_SHA:-unknown}</p>
        <p><strong>Scan Date:</strong> $(date)</p>
        <p><strong>Scan Type:</strong> $SCAN_TYPE</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Severity</th>
                <th>Count</th>
            </tr>
            <tr>
                <td class="critical">Critical</td>
                <td>$(jq -r '.summary.critical' "$SCAN_SUMMARY")</td>
            </tr>
            <tr>
                <td class="high">High</td>
                <td>$(jq -r '.summary.high' "$SCAN_SUMMARY")</td>
            </tr>
            <tr>
                <td class="medium">Medium</td>
                <td>$(jq -r '.summary.medium' "$SCAN_SUMMARY")</td>
            </tr>
            <tr>
                <td class="low">Low</td>
                <td>$(jq -r '.summary.low' "$SCAN_SUMMARY")</td>
            </tr>
            <tr>
                <td class="info">Info</td>
                <td>$(jq -r '.summary.info' "$SCAN_SUMMARY")</td>
            </tr>
        </table>
    </div>
    
    <div class="details">
        <h2>Detailed Results</h2>
        <!-- Tool-specific results would be populated here -->
    </div>
</body>
</html>
EOF
    
    log_success "HTML report generated: $html_file"
}

# Main scanning function
run_scan() {
    local scan_type=$1
    local exit_code=0
    
    log_info "Starting security scan: $scan_type"
    
    case "$scan_type" in
        "dependencies")
            scan_dependencies || exit_code=1
            ;;
        "code")
            scan_code_security || exit_code=1
            ;;
        "secrets")
            scan_secrets || exit_code=1
            ;;
        "container")
            local image_name=${2:-""}
            scan_container "$image_name" || exit_code=1
            ;;
        "iac")
            scan_iac || exit_code=1
            ;;
        "licenses")
            scan_licenses || exit_code=1
            ;;
        "all")
            scan_dependencies || exit_code=1
            scan_code_security || exit_code=1
            scan_secrets || exit_code=1
            scan_iac || exit_code=1
            scan_licenses || exit_code=1
            ;;
        *)
            log_error "Unknown scan type: $scan_type"
            exit 1
            ;;
    esac
    
    return $exit_code
}

# Print summary
print_summary() {
    log_info "Security Scan Summary:"
    echo "=================================="
    jq -r '.summary | to_entries[] | "\(.key | ascii_upcase): \(.value)"' "$SCAN_SUMMARY"
    echo "=================================="
    
    local total=$(jq -r '.summary.total_findings' "$SCAN_SUMMARY")
    local critical=$(jq -r '.summary.critical' "$SCAN_SUMMARY")
    local high=$(jq -r '.summary.high' "$SCAN_SUMMARY")
    
    if [[ $total -eq 0 ]]; then
        log_success "No security findings detected!"
    else
        log_warning "Total findings: $total"
        if [[ $critical -gt 0 ]]; then
            log_error "Critical findings: $critical"
        fi
        if [[ $high -gt 0 ]]; then
            log_error "High severity findings: $high"
        fi
    fi
}

# Main execution
main() {
    log_info "Starting comprehensive security scanning..."
    log_info "Scan type: $SCAN_TYPE"
    log_info "Output format: $OUTPUT_FORMAT"
    log_info "Severity threshold: $SEVERITY_THRESHOLD"
    
    # Run the scan
    if run_scan "$SCAN_TYPE" "$@"; then
        log_success "Security scan completed successfully"
    else
        log_error "Security scan completed with issues"
        SCAN_EXIT_CODE=1
    fi
    
    # Generate output formats
    if [[ "$OUTPUT_FORMAT" == "sarif" || "$OUTPUT_FORMAT" == "all" ]]; then
        generate_sarif
    fi
    
    if [[ "$OUTPUT_FORMAT" == "html" || "$OUTPUT_FORMAT" == "all" ]]; then
        generate_html_report
    fi
    
    # Print summary
    print_summary
    
    # Exit with appropriate code
    exit $SCAN_EXIT_CODE
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi