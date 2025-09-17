#!/bin/bash
set -euo pipefail

# Comprehensive Cache Management Script
# Usage: ./cache-manager.sh <action> <cache-type> <key-prefix> [additional-params]

ACTION=$1
CACHE_TYPE=$2
KEY_PREFIX=$3
ADDITIONAL_PARAMS=${4:-""}
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

log_cache() {
    echo -e "${PURPLE}[CACHE]${NC} $1"
}

# Error handling
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Error occurred on line $line_number with exit code $error_code"
    exit $error_code
}

trap 'handle_error $LINENO $?' ERR

# Cache configuration
CACHE_DIR="/tmp/github-cache"
CACHE_METADATA_FILE="$CACHE_DIR/cache-metadata.json"
CACHE_MAX_AGE_DAYS=7
CACHE_MAX_SIZE_MB=5000

# Initialize cache directory
init_cache() {
    mkdir -p "$CACHE_DIR"
    
    # Initialize metadata file if it doesn't exist
    if [[ ! -f "$CACHE_METADATA_FILE" ]]; then
        echo '{}' > "$CACHE_METADATA_FILE"
    fi
}

# Generate cache key
generate_cache_key() {
    local cache_type=$1
    local key_prefix=$2
    local additional_params=$3
    
    case "$cache_type" in
        "python-dependencies")
            # Hash requirements files
            local requirements_hash=""
            if [[ -f "requirements.txt" ]]; then
                requirements_hash=$(sha256sum requirements.txt | cut -d' ' -f1)
            fi
            if [[ -f "requirements-dev.txt" ]]; then
                requirements_hash="$requirements_hash-$(sha256sum requirements-dev.txt | cut -d' ' -f1)"
            fi
            if [[ -f "pyproject.toml" ]]; then
                requirements_hash="$requirements_hash-$(sha256sum pyproject.toml | cut -d' ' -f1)"
            fi
            echo "${key_prefix}-python-deps-${requirements_hash:0:16}"
            ;;
            
        "node-dependencies")
            # Hash package files
            local package_hash=""
            if [[ -f "package-lock.json" ]]; then
                package_hash=$(sha256sum package-lock.json | cut -d' ' -f1)
            elif [[ -f "yarn.lock" ]]; then
                package_hash=$(sha256sum yarn.lock | cut -d' ' -f1)
            fi
            echo "${key_prefix}-node-deps-${package_hash:0:16}"
            ;;
            
        "docker-layers")
            # Hash Dockerfile and related files
            local docker_hash=""
            if [[ -f "Dockerfile" ]]; then
                docker_hash=$(sha256sum Dockerfile | cut -d' ' -f1)
            fi
            if [[ -f "docker-compose.yml" ]]; then
                docker_hash="$docker_hash-$(sha256sum docker-compose.yml | cut -d' ' -f1)"
            fi
            echo "${key_prefix}-docker-${docker_hash:0:16}"
            ;;
            
        "build-artifacts")
            # Hash source files
            local source_hash=$(find . -name "*.py" -o -name "*.js" -o -name "*.ts" | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
            echo "${key_prefix}-build-${source_hash:0:16}"
            ;;
            
        "test-results")
            # Hash test files and source files
            local test_hash=$(find . -name "test_*.py" -o -name "*_test.py" -o -name "tests" -type d | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
            local source_hash=$(find . -name "*.py" | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
            echo "${key_prefix}-tests-${test_hash:0:8}-${source_hash:0:8}"
            ;;
            
        "security-scans")
            # Hash security-related files
            local security_hash=""
            if [[ -f "requirements.txt" ]]; then
                security_hash=$(sha256sum requirements.txt | cut -d' ' -f1)
            fi
            if [[ -f ".bandit" ]]; then
                security_hash="$security_hash-$(sha256sum .bandit | cut -d' ' -f1)"
            fi
            if [[ -f ".safety-policy.json" ]]; then
                security_hash="$security_hash-$(sha256sum .safety-policy.json | cut -d' ' -f1)"
            fi
            echo "${key_prefix}-security-${security_hash:0:16}"
            ;;
            
        "custom")
            # Use provided additional parameters
            local custom_hash=$(echo "$additional_params" | sha256sum | cut -d' ' -f1)
            echo "${key_prefix}-custom-${custom_hash:0:16}"
            ;;
            
        *)
            log_error "Unknown cache type: $cache_type"
            exit 1
            ;;
    esac
}

# Get cache paths for different cache types
get_cache_paths() {
    local cache_type=$1
    
    case "$cache_type" in
        "python-dependencies")
            echo "~/.cache/pip ~/.local/lib/python*/site-packages"
            ;;
            
        "node-dependencies")
            echo "node_modules ~/.npm ~/.yarn"
            ;;
            
        "docker-layers")
            echo "/var/lib/docker/image /var/lib/docker/overlay2"
            ;;
            
        "build-artifacts")
            echo "build/ dist/ .pytest_cache/ __pycache__/ .coverage htmlcov/ .mypy_cache/ .tox/"
            ;;
            
        "test-results")
            echo ".pytest_cache/ .coverage htmlcov/ test-results/ junit.xml coverage.xml"
            ;;
            
        "security-scans")
            echo ".bandit_cache/ .mypy_cache/ .tox/ security-scan-results/"
            ;;
            
        "custom")
            echo "$ADDITIONAL_PARAMS"
            ;;
            
        *)
            log_error "Unknown cache type: $cache_type"
            exit 1
            ;;
    esac
}

# Create cache archive
create_cache_archive() {
    local cache_key=$1
    local cache_paths=$2
    local archive_file="$CACHE_DIR/${cache_key}.tar.gz"
    
    log_cache "Creating cache archive: $cache_key"
    
    # Create temporary directory for cache contents
    local temp_dir=$(mktemp -d)
    
    # Copy cacheable files to temporary directory
    for path in $cache_paths; do
        if [[ -e "$path" ]]; then
            local rel_path=$(echo "$path" | sed 's|~||g' | sed 's|^/||g')
            mkdir -p "$temp_dir/$(dirname "$rel_path")"
            cp -r "$path" "$temp_dir/$rel_path" 2>/dev/null || true
        fi
    done
    
    # Create archive
    if tar -czf "$archive_file" -C "$temp_dir" . 2>/dev/null; then
        log_success "Cache archive created: $archive_file"
        
        # Update metadata
        update_cache_metadata "$cache_key" "created" "$(stat -c%s "$archive_file")"
        
        # Clean up temporary directory
        rm -rf "$temp_dir"
        
        return 0
    else
        log_error "Failed to create cache archive"
        rm -rf "$temp_dir"
        return 1
    fi
}

# Extract cache archive
extract_cache_archive() {
    local cache_key=$1
    local archive_file="$CACHE_DIR/${cache_key}.tar.gz"
    
    log_cache "Extracting cache archive: $cache_key"
    
    if [[ ! -f "$archive_file" ]]; then
        log_warning "Cache archive not found: $archive_file"
        return 1
    fi
    
    # Check cache age
    local cache_age_days=$(( ($(date +%s) - $(stat -c%Y "$archive_file")) / 86400 ))
    if [[ $cache_age_days -gt $CACHE_MAX_AGE_DAYS ]]; then
        log_warning "Cache archive is too old ($cache_age_days days), skipping extraction"
        return 1
    fi
    
    # Extract archive
    if tar -xzf "$archive_file" -C / 2>/dev/null; then
        log_success "Cache archive extracted: $cache_key"
        update_cache_metadata "$cache_key" "used" "$(stat -c%s "$archive_file")"
        return 0
    else
        log_error "Failed to extract cache archive"
        return 1
    fi
}

# Update cache metadata
update_cache_metadata() {
    local cache_key=$1
    local action=$2
    local size_bytes=${3:-0}
    
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local size_mb=$((size_bytes / 1024 / 1024))
    
    # Update metadata
    jq --arg key "$cache_key" \
       --arg action "$action" \
       --arg timestamp "$timestamp" \
       --arg size "$size_mb" \
       '.[$key] = {
         "last_action": $action,
         "last_updated": $timestamp,
         "size_mb": ($size | tonumber),
         "hit_count": ((.[$key].hit_count // 0) + (if $action == "used" then 1 else 0 end)),
         "created_count": ((.[$key].created_count // 0) + (if $action == "created" then 1 else 0 end))
       }' "$CACHE_METADATA_FILE" > "$CACHE_METADATA_FILE.tmp" && mv "$CACHE_METADATA_FILE.tmp" "$CACHE_METADATA_FILE"
}

# Clean up old cache entries
cleanup_cache() {
    log_info "Cleaning up old cache entries..."
    
    local current_size_mb=$(du -sm "$CACHE_DIR" 2>/dev/null | cut -f1)
    local deleted_count=0
    
    # Remove cache files older than max age
    find "$CACHE_DIR" -name "*.tar.gz" -type f -mtime +$CACHE_MAX_AGE_DAYS -delete -print | while read -r file; do
        log_info "Deleted old cache file: $(basename "$file")"
        ((deleted_count++))
    done
    
    # If cache is still too large, remove least recently used files
    if [[ $current_size_mb -gt $CACHE_MAX_SIZE_MB ]]; then
        log_info "Cache size exceeds limit ($current_size_mb MB > $CACHE_MAX_SIZE_MB MB), removing least used files..."
        
        # Get cache files sorted by last access time
        find "$CACHE_DIR" -name "*.tar.gz" -type f -exec stat -c "%X %n" {} \; | \
        sort -n | head -10 | while read -r timestamp file; do
            rm -f "$file"
            log_info "Deleted cache file to free space: $(basename "$file")"
            ((deleted_count++))
        done
    fi
    
    log_success "Cache cleanup completed. Deleted $deleted_count files."
}

# Save cache action
save_cache() {
    local cache_type=$1
    local key_prefix=$2
    local additional_params=$3
    
    log_info "Saving cache for type: $cache_type"
    
    # Generate cache key
    local cache_key=$(generate_cache_key "$cache_type" "$key_prefix" "$additional_params")
    log_cache "Generated cache key: $cache_key"
    
    # Get cache paths
    local cache_paths=$(get_cache_paths "$cache_type")
    log_cache "Cache paths: $cache_paths"
    
    # Create cache archive
    if create_cache_archive "$cache_key" "$cache_paths"; then
        log_success "Cache saved successfully: $cache_key"
        return 0
    else
        log_error "Failed to save cache"
        return 1
    fi
}

# Restore cache action
restore_cache() {
    local cache_type=$1
    local key_prefix=$2
    local additional_params=$3
    
    log_info "Restoring cache for type: $cache_type"
    
    # Generate cache key
    local cache_key=$(generate_cache_key "$cache_type" "$key_prefix" "$additional_params")
    log_cache "Generated cache key: $cache_key"
    
    # Try to extract cache archive
    if extract_cache_archive "$cache_key"; then
        log_success "Cache restored successfully: $cache_key"
        return 0
    else
        log_warning "Cache not found or expired: $cache_key"
        return 1
    fi
}

# List cache entries
list_cache() {
    log_info "Listing cache entries..."
    
    if [[ -f "$CACHE_METADATA_FILE" ]]; then
        echo "Cache Key | Last Action | Last Updated | Size (MB) | Hit Count | Created Count"
        echo "=================================================================="
        jq -r 'to_entries[] | "\(.key) | \(.value.last_action) | \(.value.last_updated) | \(.value.size_mb) | \(.value.hit_count) | \(.value.created_count)"' "$CACHE_METADATA_FILE" | \
        sort -k3 -r | column -t -s '|'
    else
        log_warning "No cache metadata found"
    fi
}

# Show cache statistics
show_stats() {
    log_info "Cache Statistics:"
    echo "=================="
    
    if [[ -f "$CACHE_METADATA_FILE" ]]; then
        local total_entries=$(jq 'length' "$CACHE_METADATA_FILE")
        local total_size_mb=$(jq '[.[].size_mb] | add' "$CACHE_METADATA_FILE" 2>/dev/null || echo "0")
        local total_hits=$(jq '[.[].hit_count] | add' "$CACHE_METADATA_FILE" 2>/dev/null || echo "0")
        local total_creates=$(jq '[.[].created_count] | add' "$CACHE_METADATA_FILE" 2>/dev/null || echo "0")
        
        echo "Total cache entries: $total_entries"
        echo "Total cache size: ${total_size_mb} MB"
        echo "Total cache hits: $total_hits"
        echo "Total cache creates: $total_creates"
        
        if [[ $total_creates -gt 0 ]]; then
            local hit_rate=$(echo "scale=2; $total_hits / $total_creates * 100" | bc -l 2>/dev/null || echo "0")
            echo "Cache hit rate: ${hit_rate}%"
        fi
        
        # Show most used caches
        echo ""
        echo "Most used caches:"
        jq -r 'to_entries | sort_by(.value.hit_count) | reverse | .[0:5] | .[] | "\(.key): \(.value.hit_count) hits"' "$CACHE_METADATA_FILE"
    else
        log_warning "No cache metadata available"
    fi
    
    # Show disk usage
    if [[ -d "$CACHE_DIR" ]]; then
        echo ""
        echo "Disk usage:"
        du -sh "$CACHE_DIR"
    fi
}

# Optimize cache configuration
optimize_cache() {
    log_info "Optimizing cache configuration..."
    
    # Analyze cache hit rates
    if [[ -f "$CACHE_METADATA_FILE" ]]; then
        local low_hit_rate_caches=$(jq -r 'to_entries[] | select(.value.hit_count < 2 and .value.created_count > 5) | .key' "$CACHE_METADATA_FILE")
        
        if [[ -n "$low_hit_rate_caches" ]]; then
            log_warning "Found caches with low hit rates:"
            echo "$low_hit_rate_caches"
            log_info "Consider adjusting cache keys or removing these caches"
        fi
        
        # Find large caches
        local large_caches=$(jq -r 'to_entries[] | select(.value.size_mb > 500) | "\(.key): \(.value.size_mb) MB"' "$CACHE_METADATA_FILE")
        
        if [[ -n "$large_caches" ]]; then
            log_warning "Found large caches (>500MB):"
            echo "$large_caches"
            log_info "Consider splitting these caches or reducing their scope"
        fi
    fi
    
    log_success "Cache optimization analysis completed"
}

# Validate cache integrity
validate_cache() {
    local cache_key=$1
    
    log_info "Validating cache integrity: $cache_key"
    
    local archive_file="$CACHE_DIR/${cache_key}.tar.gz"
    
    if [[ ! -f "$archive_file" ]]; then
        log_error "Cache archive not found: $archive_file"
        return 1
    fi
    
    # Test archive integrity
    if tar -tzf "$archive_file" >/dev/null 2>&1; then
        log_success "Cache archive is valid: $cache_key"
        return 0
    else
        log_error "Cache archive is corrupted: $cache_key"
        rm -f "$archive_file"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting cache manager: $ACTION"
    
    # Initialize cache
    init_cache
    
    case "$ACTION" in
        "save")
            save_cache "$CACHE_TYPE" "$KEY_PREFIX" "$ADDITIONAL_PARAMS"
            ;;
            
        "restore")
            restore_cache "$CACHE_TYPE" "$KEY_PREFIX" "$ADDITIONAL_PARAMS"
            ;;
            
        "list")
            list_cache
            ;;
            
        "stats")
            show_stats
            ;;
            
        "cleanup")
            cleanup_cache
            ;;
            
        "optimize")
            optimize_cache
            ;;
            
        "validate")
            if [[ -n "${4:-}" ]]; then
                validate_cache "${4}"
            else
                log_error "Cache key required for validation"
                exit 1
            fi
            ;;
            
        *)
            log_error "Unknown action: $ACTION"
            echo "Usage: $0 <save|restore|list|stats|cleanup|optimize|validate> <cache-type> <key-prefix> [additional-params]"
            exit 1
            ;;
    esac
    
    log_success "Cache manager completed successfully"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi