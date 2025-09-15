#!/bin/bash
# Unified Security Scanning Script

set -euo pipefail

# Source helper functions
source "$(dirname "$0")/unified-cicd-helpers.sh"

# Configuration
SCAN_RESULTS_DIR="security-scan-results"
MAX_SEVERITY_SCORE=7.0
FAIL_ON_CRITICAL=true

# Initialize scan results directory
init_scan_results() {
    mkdir -p "$SCAN_RESULTS_DIR"
    log_info "Initialized security scan results directory: $SCAN_RESULTS_DIR"
}

# Run Trivy vulnerability scan
run_trivy_scan() {
    local image_tag=$1
    local output_file="$SCAN_RESULTS_DIR/trivy-results.json"
    
    log_info "Running Trivy vulnerability scan for: $image_tag"
    
    trivy image \
        --severity HIGH,CRITICAL \
        --format json \
        --output "$output_file" \
        "$image_tag"
    
    # Check for critical vulnerabilities
    local critical_count=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$output_file" 2>/dev/null || echo "0")
    
    if [[ $critical_count -gt 0 ]]; then
        log_error "Found $critical_count CRITICAL vulnerabilities"
        if [[ "$FAIL_ON_CRITICAL" == "true" ]]; then
            return 1
        fi
    fi
    
    log_success "Trivy scan completed. Results saved to: $output_file"
}

# Run Snyk security scan
run_snyk_scan() {
    local image_tag=$1
    local output_file="$SCAN_RESULTS_DIR/snyk-results.json"
    
    if [[ -z "${SNYK_TOKEN:-}" ]]; then
        log_warn "SNYK_TOKEN not set, skipping Snyk scan"
        return 0
    fi
    
    log_info "Running Snyk security scan for: $image_tag"
    
    snyk test --docker "$image_tag" --json > "$output_file" || true
    
    # Check for high severity issues
    local high_severity_count=$(jq '[.vulnerabilities[]? | select(.severity == "high" or .severity == "critical")] | length' "$output_file" 2>/dev/null || echo "0")
    
    if [[ $high_severity_count -gt 0 ]]; then
        log_warn "Found $high_severity_count high/critical severity issues in Snyk scan"
    fi
    
    log_success "Snyk scan completed. Results saved to: $output_file"
}

# Run Gitleaks secrets scan
run_gitleaks_scan() {
    local output_file="$SCAN_RESULTS_DIR/gitleaks-results.json"
    
    log_info "Running Gitleaks secrets scan"
    
    gitleaks detect \
        --verbose \
        --report-format json \
        --report-path "$output_file" \
        --source .
    
    # Check for leaked secrets
    local leaks_count=$(jq '[.[]?] | length' "$output_file" 2>/dev/null || echo "0")
    
    if [[ $leaks_count -gt 0 ]]; then
        log_error "Found $leaks_count potential secrets leaked"
        return 1
    fi
    
    log_success "Gitleaks scan completed. Results saved to: $output_file"
}

# Run OWASP Dependency Check
run_dependency_check() {
    local output_file="$SCAN_RESULTS_DIR/dependency-check-report.html"
    
    log_info "Running OWASP Dependency Check"
    
    dependency-check.sh \
        --scan . \
        --format HTML \
        --out "$SCAN_RESULTS_DIR" \
        --project "Security Scan" \
        --enableExperimental
    
    log_success "Dependency check completed. Report saved to: $output_file"
}

# Generate consolidated security report
generate_security_report() {
    local image_tag=$1
    local report_file="$SCAN_RESULTS_DIR/security-summary-$(date +%Y%m%d-%H%M%S).json"
    
    log_info "Generating consolidated security report"
    
    # Collect results from all scans
    local trivy_critical=0
    local trivy_high=0
    local snyk_high=0
    local gitleaks_leaks=0
    
    if [[ -f "$SCAN_RESULTS_DIR/trivy-results.json" ]]; then
        trivy_critical=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "$SCAN_RESULTS_DIR/trivy-results.json" 2>/dev/null || echo "0")
        trivy_high=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "$SCAN_RESULTS_DIR/trivy-results.json" 2>/dev/null || echo "0")
    fi
    
    if [[ -f "$SCAN_RESULTS_DIR/snyk-results.json" ]]; then
        snyk_high=$(jq '[.vulnerabilities[]? | select(.severity == "high" or .severity == "critical")] | length' "$SCAN_RESULTS_DIR/snyk-results.json" 2>/dev/null || echo "0")
    fi
    
    if [[ -f "$SCAN_RESULTS_DIR/gitleaks-results.json" ]]; then
        gitleaks_leaks=$(jq '[.[]?] | length' "$SCAN_RESULTS_DIR/gitleaks-results.json" 2>/dev/null || echo "0")
    fi
    
    # Calculate overall risk score
    local risk_score=$(echo "scale=2; ($trivy_critical * 10 + $trivy_high * 5 + $snyk_high * 5 + $gitleaks_leaks * 8) / 4" | bc -l 2>/dev/null || echo "0")
    
    cat > "$report_file" <<EOF
{
    "scan_id": "$(uuidgen 2>/dev/null || echo "scan-$(date +%s)")",
    "image_tag": "$image_tag",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "git_commit": "${GITHUB_SHA:-unknown}",
    "git_ref": "${GITHUB_REF:-unknown}",
    "summary": {
        "trivy_critical": $trivy_critical,
        "trivy_high": $trivy_high,
        "snyk_high_critical": $snyk_high,
        "gitleaks_secrets": $gitleaks_leaks,
        "overall_risk_score": $risk_score
    },
    "status": "$([ $(echo "$risk_score > $MAX_SEVERITY_SCORE" | bc -l 2>/dev/null || echo "0") -eq 1 ] && echo "FAIL" || echo "PASS")",
    "threshold_exceeded": $(echo "$risk_score > $MAX_SEVERITY_SCORE" | bc -l 2>/dev/null || echo "0")
}
EOF
    
    log_info "Security report generated: $report_file"
    cat "$report_file"
    
    # Fail if threshold exceeded
    if [[ $(echo "$risk_score > $MAX_SEVERITY_SCORE" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        log_error "Risk score $risk_score exceeds maximum threshold $MAX_SEVERITY_SCORE"
        return 1
    fi
}

# Main security scanning function
run_security_scans() {
    local image_tag=$1
    local scan_types=${2:-"trivy,snyk,gitleaks"}
    
    log_info "Starting security scanning process"
    log_info "Image: $image_tag"
    log_info "Scan types: $scan_types"
    
    # Initialize results directory
    init_scan_results
    
    # Split scan types and run each
    IFS=',' read -ra SCANS <<< "$scan_types"
    local failed_scans=0
    
    for scan_type in "${SCANS[@]}"; do
        case $scan_type in
            "trivy")
                if ! run_trivy_scan "$image_tag"; then
                    ((failed_scans++))
                fi
                ;;
            "snyk")
                if ! run_snyk_scan "$image_tag"; then
                    ((failed_scans++))
                fi
                ;;
            "gitleaks")
                if ! run_gitleaks_scan; then
                    ((failed_scans++))
                fi
                ;;
            "dependency-check")
                if ! run_dependency_check; then
                    ((failed_scans++))
                fi
                ;;
            *)
                log_warn "Unknown scan type: $scan_type"
                ;;
        esac
    done
    
    # Generate consolidated report
    if ! generate_security_report "$image_tag"; then
        ((failed_scans++))
    fi
    
    if [[ $failed_scans -gt 0 ]]; then
        log_error "$failed_scans security scans failed"
        return 1
    fi
    
    log_success "All security scans completed successfully"
}

# Main entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <image_tag> [scan_types]"
        echo "Example: $0 my-app:v1.2.3 trivy,snyk,gitleaks"
        echo "Available scan types: trivy, snyk, gitleaks, dependency-check"
        exit 1
    fi
    
    run_security_scans "$1" "${2:-trivy,snyk,gitleaks}"
fi