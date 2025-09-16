#!/bin/bash

# Security scanning script for ISA SuperApp containers
# This script performs vulnerability scanning and security checks

set -e

echo "🔒 Starting security scan for ISA SuperApp..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image if it doesn't exist
IMAGE_NAME="isa-superapp:latest"
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "📦 Building Docker image..."
    docker build -t "$IMAGE_NAME" .
fi

echo "🔍 Running security scans..."

# Run Trivy vulnerability scanner
echo "📊 Running Trivy vulnerability scan..."
if command -v trivy > /dev/null 2>&1; then
    trivy image --exit-code 1 --no-progress --format table "$IMAGE_NAME"
else
    echo "⚠️  Trivy not found. Installing Trivy..."
    # Install Trivy (example for Linux)
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    trivy image --exit-code 1 --no-progress --format table "$IMAGE_NAME"
fi

# Run Docker Bench Security
echo "🔐 Running Docker Bench Security..."
if command -v docker-bench-security > /dev/null 2>&1; then
    docker-bench-security
else
    echo "⚠️  Docker Bench Security not found. Skipping..."
fi

# Check for secrets in image
echo "🔑 Checking for secrets in Docker image..."
if command -v dockle > /dev/null 2>&1; then
    dockle --exit-code 1 "$IMAGE_NAME"
else
    echo "⚠️  Dockle not found. Skipping secret check..."
fi

# Run Hadolint for Dockerfile linting
echo "📝 Running Hadolint for Dockerfile..."
if command -v hadolint > /dev/null 2>&1; then
    hadolint Dockerfile
else
    echo "⚠️  Hadolint not found. Skipping Dockerfile linting..."
fi

echo "✅ Security scan completed!"
echo "📋 Review the output above for any security issues that need to be addressed."