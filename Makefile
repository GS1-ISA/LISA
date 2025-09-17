# ISA SuperApp Makefile
.PHONY: help install dev-install lint format test test-cov security-scan build run clean

# Default target
help:
	@echo "ISA SuperApp - Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  lint         - Run linting with ruff"
	@echo "  format       - Format code with ruff"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  security-scan - Run security scans"
	@echo "  build        - Build Docker image"
	@echo "  run          - Run application locally"
	@echo "  clean        - Clean up build artifacts"

# Install production dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Install development dependencies
dev-install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-research.txt
	pip install ruff pytest pytest-cov

# Run linting
lint:
	ruff check .
	ruff format --check .
	./scripts/check-imports.sh

# Format code
format:
	ruff format .

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Run security scans
security-scan:
	@echo "Running security scans..."
	@echo "1. Dependency vulnerability scan with pip-audit"
	pip install pip-audit
	pip-audit --desc --format=json --output=vulnerability-report.json || true
	@echo "2. Secret scan with detect-secrets"
	pip install detect-secrets
	detect-secrets scan --all-files --baseline .secrets.baseline || true
	@echo "Security scan complete. Check vulnerability-report.json and .secrets.baseline"

# Build Docker image
build:
	docker build -t isa-superapp:latest .

# Run application locally
run:
	python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf vulnerability-report.json
	rm -rf .secrets.baseline
	docker image prune -f

# CI/CD targets
ci: lint test security-scan

# Development workflow
dev: dev-install format lint test-cov