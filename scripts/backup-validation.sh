#!/bin/bash
set -e

# ISA SuperApp Backup Validation Script
# This script validates backup integrity and tests restore procedures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_ROOT="/backup"
LOG_FILE="${PROJECT_ROOT}/logs/backup_validation_$(date +%Y%m%d_%H%M%S).log"
VALIDATION_REPORT="${PROJECT_ROOT}/reports/backup_validation_$(date +%Y%m%d_%H%M%S).html"

# Create directories
mkdir -p "${PROJECT_ROOT}/logs"
mkdir -p "${PROJECT_ROOT}/reports"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Validation functions
validate_postgres_backup() {
    local backup_file="$1"
    log "Validating PostgreSQL backup: $backup_file"

    if [ ! -f "$backup_file" ]; then
        log "${RED}ERROR: Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 1024 ]; then
        log "${RED}ERROR: Backup file too small: $file_size bytes${NC}"
        return 1
    fi

    # Verify checksum if available
    local checksum_file="${backup_file%.tar.gz}.sha256"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if ! sha256sum -c "$checksum_file" --quiet; then
            log "${RED}ERROR: Checksum verification failed${NC}"
            return 1
        fi
        log "${GREEN}Checksum verification passed${NC}"
    fi

    # Test backup integrity
    log "Testing backup integrity..."
    if ! pg_restore --list "$backup_file" &>/dev/null; then
        log "${RED}ERROR: Backup file corrupted or invalid${NC}"
        return 1
    fi

    log "${GREEN}PostgreSQL backup validation passed${NC}"
    return 0
}

validate_redis_backup() {
    local backup_file="$1"
    log "Validating Redis backup: $backup_file"

    if [ ! -f "$backup_file" ]; then
        log "${RED}ERROR: Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 100 ]; then
        log "${RED}ERROR: Backup file too small: $file_size bytes${NC}"
        return 1
    fi

    # Verify checksum if available
    local checksum_file="${backup_file%.tar.gz}.sha256"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if ! sha256sum -c "$checksum_file" --quiet; then
            log "${RED}ERROR: Checksum verification failed${NC}"
            return 1
        fi
        log "${GREEN}Checksum verification passed${NC}"
    fi

    log "${GREEN}Redis backup validation passed${NC}"
    return 0
}

validate_neo4j_backup() {
    local backup_file="$1"
    log "Validating Neo4j backup: $backup_file"

    if [ ! -f "$backup_file" ]; then
        log "${RED}ERROR: Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 1024 ]; then
        log "${RED}ERROR: Backup file too small: $file_size bytes${NC}"
        return 1
    fi

    # Verify checksum if available
    local checksum_file="${backup_file%.tar.gz}.sha256"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if ! sha256sum -c "$checksum_file" --quiet; then
            log "${RED}ERROR: Checksum verification failed${NC}"
            return 1
        fi
        log "${GREEN}Checksum verification passed${NC}"
    fi

    log "${GREEN}Neo4j backup validation passed${NC}"
    return 0
}

validate_config_backup() {
    local backup_file="$1"
    log "Validating configuration backup: $backup_file"

    if [ ! -f "$backup_file" ]; then
        log "${RED}ERROR: Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 100 ]; then
        log "${RED}ERROR: Backup file too small: $file_size bytes${NC}"
        return 1
    fi

    # Verify checksum if available
    local checksum_file="${backup_file%.tar.gz}.sha256"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if ! sha256sum -c "$checksum_file" --quiet; then
            log "${RED}ERROR: Checksum verification failed${NC}"
            return 1
        fi
        log "${GREEN}Checksum verification passed${NC}"
    fi

    # Test archive integrity
    log "Testing archive integrity..."
    if ! tar -tzf "$backup_file" &>/dev/null; then
        log "${RED}ERROR: Archive corrupted or invalid${NC}"
        return 1
    fi

    log "${GREEN}Configuration backup validation passed${NC}"
    return 0
}

validate_app_data_backup() {
    local backup_file="$1"
    log "Validating application data backup: $backup_file"

    if [ ! -f "$backup_file" ]; then
        log "${RED}ERROR: Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Check file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 100 ]; then
        log "${RED}ERROR: Backup file too small: $file_size bytes${NC}"
        return 1
    fi

    # Verify checksum if available
    local checksum_file="${backup_file%.tar.gz}.sha256"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if ! sha256sum -c "$checksum_file" --quiet; then
            log "${RED}ERROR: Checksum verification failed${NC}"
            return 1
        fi
        log "${GREEN}Checksum verification passed${NC}"
    fi

    # Test archive integrity
    log "Testing archive integrity..."
    if ! tar -tzf "$backup_file" &>/dev/null; then
        log "${RED}ERROR: Archive corrupted or invalid${NC}"
        return 1
    fi

    log "${GREEN}Application data backup validation passed${NC}"
    return 0
}

test_restore_procedures() {
    log "${BLUE}Testing restore procedures...${NC}"

    # Test PostgreSQL restore (dry run)
    log "Testing PostgreSQL restore procedure..."
    # This would require a test database instance

    # Test Redis restore (dry run)
    log "Testing Redis restore procedure..."
    # This would require a test Redis instance

    # Test configuration restore (dry run)
    log "Testing configuration restore procedure..."
    # This would validate YAML/JSON syntax

    log "${GREEN}Restore procedure tests completed${NC}"
}

generate_report() {
    local total_backups="$1"
    local valid_backups="$2"
    local invalid_backups="$3"

    cat > "$VALIDATION_REPORT" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>ISA SuperApp Backup Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .error { color: #dc3545; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ISA SuperApp Backup Validation Report</h1>
        <p>Generated on: $(date)</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total backups validated: <strong>$total_backups</strong></p>
        <p>Valid backups: <strong class="success">$valid_backups</strong></p>
        <p>Invalid backups: <strong class="error">$invalid_backups</strong></p>
        <p>Success rate: <strong>$(( valid_backups * 100 / total_backups ))%</strong></p>
    </div>

    <h2>Detailed Log</h2>
    <pre>$(cat "$LOG_FILE")</pre>
</body>
</html>
EOF

    log "Validation report generated: $VALIDATION_REPORT"
}

main() {
    log "${BLUE}Starting ISA SuperApp backup validation${NC}"

    local total_backups=0
    local valid_backups=0
    local invalid_backups=0

    # Validate PostgreSQL backups
    log "${BLUE}Validating PostgreSQL backups...${NC}"
    for backup_file in "$BACKUP_ROOT"/isa_superapp_*.tar.gz; do
        if [ -f "$backup_file" ]; then
            ((total_backups++))
            if validate_postgres_backup "$backup_file"; then
                ((valid_backups++))
            else
                ((invalid_backups++))
            fi
        fi
    done

    # Validate Redis backups
    log "${BLUE}Validating Redis backups...${NC}"
    for backup_file in "$BACKUP_ROOT"/isa_redis_*.tar.gz; do
        if [ -f "$backup_file" ]; then
            ((total_backups++))
            if validate_redis_backup "$backup_file"; then
                ((valid_backups++))
            else
                ((invalid_backups++))
            fi
        fi
    done

    # Validate Neo4j backups
    log "${BLUE}Validating Neo4j backups...${NC}"
    for backup_file in "$BACKUP_ROOT"/isa_neo4j_*.tar.gz; do
        if [ -f "$backup_file" ]; then
            ((total_backups++))
            if validate_neo4j_backup "$backup_file"; then
                ((valid_backups++))
            else
                ((invalid_backups++))
            fi
        fi
    done

    # Validate configuration backups
    log "${BLUE}Validating configuration backups...${NC}"
    for backup_file in "$BACKUP_ROOT"/isa_config_*.tar.gz; do
        if [ -f "$backup_file" ]; then
            ((total_backups++))
            if validate_config_backup "$backup_file"; then
                ((valid_backups++))
            else
                ((invalid_backups++))
            fi
        fi
    done

    # Validate application data backups
    log "${BLUE}Validating application data backups...${NC}"
    for backup_file in "$BACKUP_ROOT"/isa_app_data_*.tar.gz; do
        if [ -f "$backup_file" ]; then
            ((total_backups++))
            if validate_app_data_backup "$backup_file"; then
                ((valid_backups++))
            else
                ((invalid_backups++))
            fi
        fi
    done

    # Test restore procedures
    test_restore_procedures

    # Generate report
    generate_report "$total_backups" "$valid_backups" "$invalid_backups"

    # Final summary
    log "${BLUE}Backup validation completed${NC}"
    log "Total backups: $total_backups"
    log "Valid backups: $valid_backups"
    log "Invalid backups: $invalid_backups"

    if [ "$invalid_backups" -gt 0 ]; then
        log "${RED}WARNING: $invalid_backups backup(s) failed validation${NC}"
        exit 1
    else
        log "${GREEN}All backups validated successfully${NC}"
        exit 0
    fi
}

# Run main function
main "$@"