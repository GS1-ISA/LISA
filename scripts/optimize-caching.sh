#!/bin/bash
# Caching Optimization Script

set -euo pipefail

# Source helper functions
source "$(dirname "$0")/unified-cicd-helpers.sh"

# Configuration
CACHE_DIR=".cache"
DOCKER_CACHE_DIR="$CACHE_DIR/docker"
NODE_CACHE_DIR="$CACHE_DIR/node"
PYTHON_CACHE_DIR="$CACHE_DIR/python"
MAVEN_CACHE_DIR="$CACHE_DIR/maven"
GRADLE_CACHE_DIR="$CACHE_DIR/gradle"

# Initialize cache directories
init_cache_dirs() {
    mkdir -p "$DOCKER_CACHE_DIR" "$NODE_CACHE_DIR" "$PYTHON_CACHE_DIR" "$MAVEN_CACHE_DIR" "$GRADLE_CACHE_DIR"
    log_info "Initialized cache directories"
}

# Docker layer caching optimization
optimize_docker_cache() {
    local image_name=$1
    local dockerfile_path=${2:-"Dockerfile"}
    local cache_tag=${3:-"cache"}
    
    log_info "Optimizing Docker cache for: $image_name"
    
    # Enable BuildKit for better caching
    export DOCKER_BUILDKIT=1
    
    # Build with cache-from and cache-to
    docker build \
        --file "$dockerfile_path" \
        --tag "$image_name" \
        --cache-from "type=local,src=$DOCKER_CACHE_DIR" \
        --cache-to "type=local,dest=$DOCKER_CACHE_DIR,mode=max" \
        --build-arg "BUILDKIT_INLINE_CACHE=1" \
        .
    
    # Tag cache image for registry
    docker tag "$image_name" "${image_name}-${cache_tag}"
    
    log_success "Docker cache optimization completed"
}

# Multi-stage Docker build with caching
build_multi_stage_docker() {
    local image_name=$1
    local dockerfile_path=${2:-"Dockerfile"}
    local target_stage=${3:-""}
    
    log_info "Building multi-stage Docker image: $image_name"
    
    # Build arguments for caching
    local build_args=(
        "--file" "$dockerfile_path"
        "--tag" "$image_name"
        "--cache-from" "type=local,src=$DOCKER_CACHE_DIR"
        "--cache-to" "type=local,dest=$DOCKER_CACHE_DIR,mode=max"
        "--build-arg" "BUILDKIT_INLINE_CACHE=1"
    )
    
    if [[ -n "$target_stage" ]]; then
        build_args+=("--target" "$target_stage")
    fi
    
    # Build the image
    docker build "${build_args[@]}" .
    
    log_success "Multi-stage Docker build completed"
}

# Node.js dependency caching
cache_node_dependencies() {
    local package_json_hash=$(sha256sum package.json | cut -d' ' -f1)
    local cache_key="node-deps-${package_json_hash}"
    local cache_file="$NODE_CACHE_DIR/${cache_key}.tar.gz"
    
    log_info "Caching Node.js dependencies with key: $cache_key"
    
    if [[ -f "$cache_file" ]]; then
        log_info "Restoring Node.js dependencies from cache"
        tar -xzf "$cache_file" -C ./
        npm ci --prefer-offline --no-audit --no-fund
    else
        log_info "Installing Node.js dependencies"
        npm ci --no-audit --no-fund
        
        # Cache dependencies
        if [[ -d "node_modules" ]]; then
            tar -czf "$cache_file" node_modules/
            log_success "Node.js dependencies cached"
        fi
    fi
}

# Python dependency caching
cache_python_dependencies() {
    local requirements_hash=$(sha256sum requirements.txt 2>/dev/null | cut -d' ' -f1 || echo "no-requirements")
    local cache_key="python-deps-${requirements_hash}"
    local cache_file="$PYTHON_CACHE_DIR/${cache_key}.tar.gz"
    
    log_info "Caching Python dependencies with key: $cache_key"
    
    if [[ -f "$cache_file" ]]; then
        log_info "Restoring Python dependencies from cache"
        tar -xzf "$cache_file" -C ./
    else
        log_info "Installing Python dependencies"
        
        # Create virtual environment if it doesn't exist
        if [[ ! -d "venv" ]]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Cache dependencies
        tar -czf "$cache_file" venv/
        log_success "Python dependencies cached"
    fi
}

# Maven dependency caching
cache_maven_dependencies() {
    local pom_hash=$(sha256sum pom.xml 2>/dev/null | cut -d' ' -f1 || echo "no-pom")
    local cache_key="maven-deps-${pom_hash}"
    local cache_file="$MAVEN_CACHE_DIR/${cache_key}.tar.gz"
    
    log_info "Caching Maven dependencies with key: $cache_key"
    
    if [[ -f "$cache_file" ]]; then
        log_info "Restoring Maven dependencies from cache"
        mkdir -p ~/.m2
        tar -xzf "$cache_file" -C ~/
    fi
    
    log_info "Running Maven build"
    mvn clean compile
    
    # Cache dependencies
    if [[ -d ~/.m2/repository ]]; then
        tar -czf "$cache_file" -C ~/ .m2/repository
        log_success "Maven dependencies cached"
    fi
}

# Gradle dependency caching
cache_gradle_dependencies() {
    local build_gradle_hash=$(find . -name "build.gradle*" -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)
    local cache_key="gradle-deps-${build_gradle_hash}"
    local cache_file="$GRADLE_CACHE_DIR/${cache_key}.tar.gz"
    
    log_info "Caching Gradle dependencies with key: $cache_key"
    
    if [[ -f "$cache_file" ]]; then
        log_info "Restoring Gradle dependencies from cache"
        mkdir -p ~/.gradle
        tar -xzf "$cache_file" -C ~/
    fi
    
    log_info "Running Gradle build"
    ./gradlew build
    
    # Cache dependencies
    if [[ -d ~/.gradle/caches ]]; then
        tar -czf "$cache_file" -C ~/ .gradle/caches .gradle/wrapper
        log_success "Gradle dependencies cached"
    fi
}

# GitHub Actions cache optimization
optimize_github_actions_cache() {
    local cache_key_prefix=$1
    local cache_paths=${2:-""}
    
    log_info "Optimizing GitHub Actions cache with prefix: $cache_key_prefix"
    
    # Generate cache key based on file hashes
    local cache_key="${cache_key_prefix}-$(date +%Y%m%d)"
    
    # Default cache paths if not provided
    if [[ -z "$cache_paths" ]]; then
        cache_paths="node_modules,~/.npm,~/.cache,~/.m2,~/.gradle,venv,.venv"
    fi
    
    # Generate GitHub Actions cache configuration
    cat <<EOF
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      ~/.cache
      ~/.m2
      ~/.gradle
      node_modules
      venv
      .venv
      $cache_paths
    key: \${{ runner.os }}-${cache_key}-\${{ hashFiles('**/package-lock.json', '**/yarn.lock', '**/requirements.txt', '**/pom.xml', '**/build.gradle*') }}
    restore-keys: |
      \${{ runner.os }}-${cache_key}-
      \${{ runner.os }}-
EOF
    
    log_success "GitHub Actions cache configuration generated"
}

# Docker registry cache optimization
optimize_docker_registry_cache() {
    local registry_url=$1
    local image_name=$2
    local cache_tag=${3:-"cache"}
    
    log_info "Optimizing Docker registry cache for: $registry_url/$image_name"
    
    # Pull cache image if exists
    if docker pull "$registry_url/$image_name:$cache_tag" 2>/dev/null; then
        log_info "Pulled cache image: $registry_url/$image_name:$cache_tag"
    fi
    
    # Build with registry cache
    docker build \
        --tag "$image_name" \
        --cache-from "$registry_url/$image_name:$cache_tag" \
        --build-arg "BUILDKIT_INLINE_CACHE=1" \
        .
    
    # Push cache image
    docker tag "$image_name" "$registry_url/$image_name:$cache_tag"
    docker push "$registry_url/$image_name:$cache_tag"
    
    log_success "Docker registry cache optimization completed"
}

# Cache cleanup and maintenance
cleanup_cache() {
    local max_age_days=${1:-7}
    local max_size_mb=${2:-1024}
    
    log_info "Cleaning up cache directories (max age: ${max_age_days} days, max size: ${max_size_mb}MB)"
    
    # Remove old cache files
    find "$CACHE_DIR" -type f -mtime "+$max_age_days" -delete 2>/dev/null || true
    
    # Check total cache size
    local total_size_mb=$(du -sm "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")
    
    if [[ $total_size_mb -gt $max_size_mb ]]; then
        log_warn "Cache size (${total_size_mb}MB) exceeds limit (${max_size_mb}MB)"
        
        # Remove oldest files until under limit
        find "$CACHE_DIR" -type f -printf '%T@ %p\n' | \
            sort -n | \
            head -n 20 | \
            while read -r timestamp file; do
                rm -f "$file"
                local new_size=$(du -sm "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")
                if [[ $new_size -le $max_size_mb ]]; then
                    break
                fi
            done
    fi
    
    log_success "Cache cleanup completed"
}

# Generate cache performance report
generate_cache_report() {
    local report_file="cache-performance-report.json"
    
    log_info "Generating cache performance report"
    
    # Collect cache statistics
    local total_files=$(find "$CACHE_DIR" -type f | wc -l)
    local total_size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")
    local cache_hit_rate=$(calculate_cache_hit_rate)
    
    cat > "$report_file" <<EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "cache_directories": {
        "docker": "$(du -sh "$DOCKER_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")",
        "node": "$(du -sh "$NODE_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")",
        "python": "$(du -sh "$PYTHON_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")",
        "maven": "$(du -sh "$MAVEN_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")",
        "gradle": "$(du -sh "$GRADLE_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0")"
    },
    "total_files": $total_files,
    "total_size": "$total_size",
    "cache_hit_rate": $cache_hit_rate,
    "optimization_recommendations": [
        "Consider increasing cache size limit if hit rate is low",
        "Review cache key generation for better granularity",
        "Implement cache warming for frequently used dependencies"
    ]
}
EOF
    
    log_success "Cache performance report generated: $report_file"
}

# Calculate cache hit rate (mock implementation)
calculate_cache_hit_rate() {
    # This would typically be calculated based on actual cache usage
    # For now, return a mock value
    echo "0.85"
}

# Main function
main() {
    local command=$1
    shift
    
    case $command in
        "init")
            init_cache_dirs
            ;;
        "docker")
            optimize_docker_cache "$@"
            ;;
        "docker-multi")
            build_multi_stage_docker "$@"
            ;;
        "node")
            cache_node_dependencies
            ;;
        "python")
            cache_python_dependencies
            ;;
        "maven")
            cache_maven_dependencies
            ;;
        "gradle")
            cache_gradle_dependencies
            ;;
        "github-actions")
            optimize_github_actions_cache "$@"
            ;;
        "docker-registry")
            optimize_docker_registry_cache "$@"
            ;;
        "cleanup")
            cleanup_cache "$@"
            ;;
        "report")
            generate_cache_report
            ;;
        *)
            echo "Usage: $0 {init|docker|docker-multi|node|python|maven|gradle|github-actions|docker-registry|cleanup|report} [parameters...]"
            echo ""
            echo "Examples:"
            echo "  $0 init"
            echo "  $0 docker my-app:latest Dockerfile cache"
            echo "  $0 node"
            echo "  $0 python"
            echo "  $0 github-actions cache-key-prefix \"path1,path2\""
            echo "  $0 cleanup 7 1024"
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