#!/bin/bash

# Unified CI/CD Validation Script
# This script validates the unified CI/CD pipeline setup and functionality

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_DIR="${PROJECT_ROOT}/config"
LOGS_DIR="${PROJECT_ROOT}/logs"
VALIDATION_LOG="${LOGS_DIR}/validation.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$VALIDATION_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$VALIDATION_LOG"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$VALIDATION_LOG"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$VALIDATION_LOG"
}

# Test result tracking
test_passed() {
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
    success "✓ $1"
}

test_failed() {
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
    error "✗ $1"
}

# Initialize validation
initialize_validation() {
    log "Initializing validation..."
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOGS_DIR"
    
    # Clear previous validation log
    > "$VALIDATION_LOG"
    
    # Check if setup is complete
    if [[ ! -f "$PROJECT_ROOT/.unified-cicd-setup-complete" ]]; then
        error "Unified CI/CD setup not completed. Please run ./scripts/setup-unified-cicd.sh first."
        exit 1
    fi
    
    success "Validation initialized"
}

# Test 1: Configuration validation
test_configuration() {
    log "Testing configuration..."
    
    # Test main configuration file
    if [[ -f "$CONFIG_DIR/unified-cicd.conf" ]]; then
        test_passed "Main configuration file exists"
        
        # Test configuration syntax
        if source "$CONFIG_DIR/unified-cicd.conf" 2>/dev/null; then
            test_passed "Main configuration syntax is valid"
        else
            test_failed "Main configuration syntax is invalid"
        fi
    else
        test_failed "Main configuration file missing"
    fi
    
    # Test environment configurations
    for env in development staging production; do
        if [[ -f "$CONFIG_DIR/environments/${env}.conf" ]]; then
            test_passed "Environment configuration for $env exists"
            
            if source "$CONFIG_DIR/environments/${env}.conf" 2>/dev/null; then
                test_passed "Environment configuration for $env syntax is valid"
            else
                test_failed "Environment configuration for $env syntax is invalid"
            fi
        else
            test_failed "Environment configuration for $env missing"
        fi
    done
    
    # Test security configuration
    if [[ -f "$CONFIG_DIR/security/security.conf" ]]; then
        test_passed "Security configuration exists"
        
        if source "$CONFIG_DIR/security/security.conf" 2>/dev/null; then
            test_passed "Security configuration syntax is valid"
        else
            test_failed "Security configuration syntax is invalid"
        fi
    else
        test_failed "Security configuration missing"
    fi
    
    # Test deployment configuration
    if [[ -f "$CONFIG_DIR/deployment/deployment.conf" ]]; then
        test_passed "Deployment configuration exists"
        
        if source "$CONFIG_DIR/deployment/deployment.conf" 2>/dev/null; then
            test_passed "Deployment configuration syntax is valid"
        else
            test_failed "Deployment configuration syntax is invalid"
        fi
    else
        test_failed "Deployment configuration missing"
    fi
    
    # Test performance configuration
    if [[ -f "$CONFIG_DIR/performance/performance.conf" ]]; then
        test_passed "Performance configuration exists"
        
        if source "$CONFIG_DIR/performance/performance.conf" 2>/dev/null; then
            test_passed "Performance configuration syntax is valid"
        else
            test_failed "Performance configuration syntax is invalid"
        fi
    else
        test_failed "Performance configuration missing"
    fi
}

# Test 2: Script validation
test_scripts() {
    log "Testing scripts..."
    
    local scripts=(
        "unified-cicd-pipeline.sh"
        "security-scanning.sh"
        "rollback-deployment.sh"
        "performance-testing.sh"
        "deployment-staging.sh"
        "monitoring.sh"
        "backup-config.sh"
    )
    
    for script in "${scripts[@]}"; do
        local script_path="$SCRIPT_DIR/$script"
        
        if [[ -f "$script_path" ]]; then
            test_passed "Script $script exists"
            
            if [[ -x "$script_path" ]]; then
                test_passed "Script $script is executable"
            else
                test_failed "Script $script is not executable"
            fi
            
            # Test script syntax
            if bash -n "$script_path" 2>/dev/null; then
                test_passed "Script $script syntax is valid"
            else
                test_failed "Script $script syntax is invalid"
            fi
        else
            test_failed "Script $script missing"
        fi
    done
}

# Test 3: GitHub Actions workflow validation
test_github_actions() {
    log "Testing GitHub Actions workflows..."
    
    local workflow_file="$PROJECT_ROOT/.github/workflows/unified-cicd.yml"
    
    if [[ -f "$workflow_file" ]]; then
        test_passed "Unified CI/CD workflow exists"
        
        # Test YAML syntax
        if python3 -c "import yaml; yaml.safe_load(open('$workflow_file'))" 2>/dev/null; then
            test_passed "Workflow YAML syntax is valid"
        else
            test_failed "Workflow YAML syntax is invalid"
        fi
        
        # Test workflow structure
        if grep -q "name:" "$workflow_file" && \
           grep -q "on:" "$workflow_file" && \
           grep -q "jobs:" "$workflow_file"; then
            test_passed "Workflow has required structure"
        else
            test_failed "Workflow missing required structure"
        fi
    else
        test_failed "Unified CI/CD workflow missing"
    fi
    
    # Test workflow templates
    local template_dir="$PROJECT_ROOT/.github/workflow-templates"
    if [[ -d "$template_dir" ]]; then
        test_passed "Workflow templates directory exists"
        
        local templates=("security-only.yml" "performance-only.yml")
        for template in "${templates[@]}"; do
            if [[ -f "$template_dir/$template" ]]; then
                test_passed "Workflow template $template exists"
            else
                test_failed "Workflow template $template missing"
            fi
        done
    else
        test_failed "Workflow templates directory missing"
    fi
}

# Test 4: Security tools validation
test_security_tools() {
    log "Testing security tools..."
    
    local security_tools=(
        "trivy"
        "grype"
        "semgrep"
        "trufflehog"
        "k6"
    )
    
    for tool in "${security_tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            test_passed "Security tool $tool is installed"
            
            # Test tool functionality
            case "$tool" in
                "trivy")
                    if trivy --version &>/dev/null; then
                        test_passed "Trivy is functional"
                    else
                        test_failed "Trivy is not functional"
                    fi
                    ;;
                "grype")
                    if grype --version &>/dev/null; then
                        test_passed "Grype is functional"
                    else
                        test_failed "Grype is not functional"
                    fi
                    ;;
                "semgrep")
                    if semgrep --version &>/dev/null; then
                        test_passed "Semgrep is functional"
                    else
                        test_failed "Semgrep is not functional"
                    fi
                    ;;
                "trufflehog")
                    if trufflehog --version &>/dev/null; then
                        test_passed "TruffleHog is functional"
                    else
                        test_failed "TruffleHog is not functional"
                    fi
                    ;;
                "k6")
                    if k6 version &>/dev/null; then
                        test_passed "K6 is functional"
                    else
                        test_failed "K6 is not functional"
                    fi
                    ;;
            esac
        else
            test_failed "Security tool $tool is not installed"
        fi
    done
}

# Test 5: Directory structure validation
test_directory_structure() {
    log "Testing directory structure..."
    
    local required_directories=(
        "$CONFIG_DIR"
        "$LOGS_DIR"
        "$PROJECT_ROOT/backups"
        "$CONFIG_DIR/environments"
        "$CONFIG_DIR/security"
        "$CONFIG_DIR/deployment"
        "$CONFIG_DIR/performance"
        "$PROJECT_ROOT/security-reports"
        "$PROJECT_ROOT/compliance-reports"
        "$PROJECT_ROOT/performance-reports"
        "$PROJECT_ROOT/deployment-logs"
    )
    
    for dir in "${required_directories[@]}"; do
        if [[ -d "$dir" ]]; then
            test_passed "Directory $dir exists"
        else
            test_failed "Directory $dir missing"
        fi
    done
}

# Test 6: Functionality validation
test_functionality() {
    log "Testing functionality..."
    
    # Test unified pipeline help
    if "$SCRIPT_DIR/unified-cicd-pipeline.sh" --help &>/dev/null; then
        test_passed "Unified pipeline help command works"
    else
        test_failed "Unified pipeline help command failed"
    fi
    
    # Test security scanning help
    if "$SCRIPT_DIR/security-scanning.sh" --help &>/dev/null; then
        test_passed "Security scanning help command works"
    else
        test_failed "Security scanning help command failed"
    fi
    
    # Test rollback deployment help
    if "$SCRIPT_DIR/rollback-deployment.sh" --help &>/dev/null; then
        test_passed "Rollback deployment help command works"
    else
        test_failed "Rollback deployment help command failed"
    fi
    
    # Test performance testing help
    if "$SCRIPT_DIR/performance-testing.sh" --help &>/dev/null; then
        test_passed "Performance testing help command works"
    else
        test_failed "Performance testing help command failed"
    fi
    
    # Test deployment staging help
    if "$SCRIPT_DIR/deployment-staging.sh" --help &>/dev/null; then
        test_passed "Deployment staging help command works"
    else
        test_failed "Deployment staging help command failed"
    fi
    
    # Test backup functionality
    if "$SCRIPT_DIR/backup-config.sh" list &>/dev/null; then
        test_passed "Backup functionality works"
    else
        test_failed "Backup functionality failed"
    fi
}

# Test 7: Integration validation
test_integration() {
    log "Testing integration..."
    
    # Test configuration loading in scripts
    if "$SCRIPT_DIR/unified-cicd-pipeline.sh" --dry-run &>/dev/null; then
        test_passed "Unified pipeline configuration loading works"
    else
        test_failed "Unified pipeline configuration loading failed"
    fi
    
    # Test security scanning dry run
    if "$SCRIPT_DIR/security-scanning.sh" --dry-run &>/dev/null; then
        test_passed "Security scanning dry run works"
    else
        test_failed "Security scanning dry run failed"
    fi
    
    # Test performance testing dry run
    if "$SCRIPT_DIR/performance-testing.sh" --dry-run &>/dev/null; then
        test_passed "Performance testing dry run works"
    else
        test_failed "Performance testing dry run failed"
    fi
}

# Test 8: Security validation
test_security() {
    log "Testing security..."
    
    # Test file permissions
    local sensitive_files=(
        "$CONFIG_DIR/unified-cicd.conf"
        "$CONFIG_DIR/security/security.conf"
        "$CONFIG_DIR/monitoring.conf"
    )
    
    for file in "${sensitive_files[@]}"; do
        if [[ -f "$file" ]]; then
            local permissions=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%A" "$file" 2>/dev/null)
            if [[ "$permissions" == "600" || "$permissions" == "644" ]]; then
                test_passed "File $file has appropriate permissions"
            else
                warning "File $file has permissions $permissions (should be 600 or 644)"
            fi
        fi
    done
    
    # Test for hardcoded secrets in scripts
    if grep -r "password\|secret\|token" "$SCRIPT_DIR" --include="*.sh" | grep -v "grep\|#.*password\|#.*secret\|#.*token" &>/dev/null; then
        warning "Potential hardcoded secrets found in scripts"
    else
        test_passed "No hardcoded secrets found in scripts"
    fi
}

# Test 9: Performance validation
test_performance() {
    log "Testing performance..."
    
    # Test script execution time
    local start_time=$(date +%s)
    
    # Run a simple test
    "$SCRIPT_DIR/unified-cicd-pipeline.sh" --help &>/dev/null
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    if [[ $execution_time -lt 5 ]]; then
        test_passed "Script execution is fast enough ($execution_time seconds)"
    else
        warning "Script execution took $execution_time seconds"
    fi
}

# Test 10: Documentation validation
test_documentation() {
    log "Testing documentation..."
    
    # Test main documentation
    if [[ -f "$PROJECT_ROOT/docs/unified-cicd-architecture.md" ]]; then
        test_passed "Architecture documentation exists"
    else
        test_failed "Architecture documentation missing"
    fi
    
    # Test README
    if [[ -f "$PROJECT_ROOT/README.md" ]]; then
        test_passed "README exists"
    else
        test_failed "README missing"
    fi
    
    # Test inline documentation in scripts
    local documented_scripts=0
    local total_scripts=0
    
    for script in "$SCRIPT_DIR"/*.sh; do
        if [[ -f "$script" ]]; then
            ((total_scripts++))
            if grep -q "#!/bin/bash" "$script" && grep -q "#.*script" "$script"; then
                ((documented_scripts++))
            fi
        fi
    done
    
    if [[ $documented_scripts -eq $total_scripts ]]; then
        test_passed "All scripts have documentation"
    else
        test_failed "Only $documented_scripts out of $total_scripts scripts are documented"
    fi
}

# Generate validation report
generate_report() {
    log "Generating validation report..."
    
    local report_file="$LOGS_DIR/validation-report.md"
    
    cat > "$report_file" << EOF
# Unified CI/CD Validation Report

**Generated:** $(date)

## Summary

- **Total Tests:** $TESTS_TOTAL
- **Tests Passed:** $TESTS_PASSED
- **Tests Failed:** $TESTS_FAILED
- **Success Rate:** $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

## Test Results

### Configuration Tests
- Main configuration: $([[ -f "$CONFIG_DIR/unified-cicd.conf" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Environment configurations: $([[ -f "$CONFIG_DIR/environments/development.conf" && -f "$CONFIG_DIR/environments/staging.conf" && -f "$CONFIG_DIR/environments/production.conf" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Security configuration: $([[ -f "$CONFIG_DIR/security/security.conf" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Deployment configuration: $([[ -f "$CONFIG_DIR/deployment/deployment.conf" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Performance configuration: $([[ -f "$CONFIG_DIR/performance/performance.conf" ]] && echo "✓ PASS" || echo "✗ FAIL")

### Script Tests
- All scripts exist: $([[ $(ls -1 "$SCRIPT_DIR"/*.sh 2>/dev/null | wc -l) -ge 6 ]] && echo "✓ PASS" || echo "✗ FAIL")
- All scripts are executable: $([[ $(find "$SCRIPT_DIR" -name "*.sh" -executable | wc -l) -ge 6 ]] && echo "✓ PASS" || echo "✗ FAIL")
- Script syntax validation: $([[ $(find "$SCRIPT_DIR" -name "*.sh" -exec bash -n {} \; 2>/dev/null | wc -l) -eq 0 ]] && echo "✓ PASS" || echo "✗ FAIL")

### GitHub Actions Tests
- Unified workflow exists: $([[ -f "$PROJECT_ROOT/.github/workflows/unified-cicd.yml" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Workflow templates exist: $([[ -d "$PROJECT_ROOT/.github/workflow-templates" ]] && echo "✓ PASS" || echo "✗ FAIL")

### Security Tools Tests
- Trivy installed: $(command -v trivy &> /dev/null && echo "✓ PASS" || echo "✗ FAIL")
- Grype installed: $(command -v grype &> /dev/null && echo "✓ PASS" || echo "✗ FAIL")
- Semgrep installed: $(command -v semgrep &> /dev/null && echo "✓ PASS" || echo "✗ FAIL")
- TruffleHog installed: $(command -v trufflehog &> /dev/null && echo "✓ PASS" || echo "✗ FAIL")
- K6 installed: $(command -v k6 &> /dev/null && echo "✓ PASS" || echo "✗ FAIL")

### Directory Structure Tests
- Configuration directory: $([[ -d "$CONFIG_DIR" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Logs directory: $([[ -d "$LOGS_DIR" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Backup directory: $([[ -d "$PROJECT_ROOT/backups" ]] && echo "✓ PASS" || echo "✗ FAIL")
- Security reports directory: $([[ -d "$PROJECT_ROOT/security-reports" ]] && echo "✓ PASS" || echo "✗ FAIL")

### Documentation Tests
- Architecture documentation: $([[ -f "$PROJECT_ROOT/docs/unified-cicd-architecture.md" ]] && echo "✓ PASS" || echo "✗ FAIL")
- README exists: $([[ -f "$PROJECT_ROOT/README.md" ]] && echo "✓ PASS" || echo "✗ FAIL")

## Recommendations

EOF

    if [[ $TESTS_FAILED -gt 0 ]]; then
        cat >> "$report_file" << EOF
### Critical Issues
- $TESTS_FAILED tests failed. Please address these issues before proceeding.

### Next Steps
1. Review the failed tests above
2. Fix any configuration issues
3. Install missing tools
4. Run validation again: ./scripts/validate-unified-cicd.sh
EOF
    else
        cat >> "$report_file" << EOF
### Status: READY FOR PRODUCTION
- All tests passed successfully
- The unified CI/CD pipeline is ready for use

### Next Steps
1. Configure GitHub repository secrets
2. Set up cloud provider access
3. Configure notification channels
4. Test the pipeline in development environment
5. Run your first deployment: ./scripts/unified-cicd-pipeline.sh deploy development
EOF
    fi
    
    success "Validation report generated: $report_file"
}

# Main validation function
main() {
    log "Starting Unified CI/CD validation..."
    
    # Initialize validation
    initialize_validation
    
    # Run all tests
    test_configuration
    test_scripts
    test_github_actions
    test_security_tools
    test_directory_structure
    test_functionality
    test_integration
    test_security
    test_performance
    test_documentation
    
    # Generate report
    generate_report
    
    # Print summary
    echo
    log "Validation Summary:"
    log "Total Tests: $TESTS_TOTAL"
    log "Tests Passed: $TESTS_PASSED"
    log "Tests Failed: $TESTS_FAILED"
    log "Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        success "All tests passed! The unified CI/CD pipeline is ready for use."
        exit 0
    else
        error "$TESTS_FAILED tests failed. Please review the validation report and fix the issues."
        exit 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi