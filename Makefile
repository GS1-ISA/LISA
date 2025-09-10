# ISA SuperApp Development Makefile
.PHONY: help install install-dev test test-unit test-integration test-performance test-all lint format type-check security-check clean build docs audit

# Default target
help:
	@echo "ISA SuperApp Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-all     - Run all tests with coverage"
	@echo ""
	@echo "Quality Commands:"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  security     - Run security scans"
	@echo "  audit        - Run comprehensive audit with issue creation"
	@echo ""
	@echo "Build Commands:"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docs         - Generate documentation"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev-setup    - Complete development setup"
	@echo "  pre-commit   - Run pre-commit hooks"
	@echo "  ci           - Run CI pipeline locally"
	@echo "  agent-sync   - Refresh meta audit, docs build, cost report"
	@echo "  virtuous-cycle - Run meta audit + quick verify + log"
	@echo "  pdf-index     - Build PDF index from ISA goals PDFs into artifacts/"

# Setup commands
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .[dev]

dev-setup: install-dev
	pre-commit install
	mkdir -p logs
	mkdir -p data/cache
	mkdir -p data/vector_store
	@echo "Development setup complete!"

# Testing commands
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v --cov=isa_superapp --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v --cov=isa_superapp --cov-report=term-missing

test-performance:
	pytest tests/performance/ -v --benchmark-only

test-all:
	pytest tests/ -v --cov=isa_superapp --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-parallel:
	pytest tests/ -v -n auto --dist=loadfile

test-markers:
	@echo "Available test markers:"
	@echo "  unit         - Unit tests"
	@echo "  integration  - Integration tests"
	@echo "  performance  - Performance tests"
	@echo "  slow         - Slow running tests"
	@echo "  flaky        - Flaky tests"
	@echo "  requires_api - Tests requiring external API"
	@echo "  requires_db  - Tests requiring database"
	@echo "  requires_redis - Tests requiring Redis"
	@echo "  requires_chroma - Tests requiring ChromaDB"

# Quality commands
lint:
	flake8 isa_superapp/ tests/ scripts/
	bandit -r isa_superapp/ -f json -o bandit-report.json || true

format:
	black isa_superapp/ tests/ scripts/
	isort isa_superapp/ tests/ scripts/

format-check:
	black --check --diff isa_superapp/ tests/ scripts/
	isort --check-only --diff isa_superapp/ tests/ scripts/

type-check:
	mypy isa_superapp/ --ignore-missing-imports

security:
	bandit -r isa_superapp/
	safety check

# Build commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .benchmarks/

build:
	python setup.py sdist bdist_wheel

docs:
	sphinx-build -b html docs/ docs/_build/html

# Development commands
pre-commit:
	pre-commit run --all-files

ci: format-check lint type-check security test-all
audit:
	@echo "🔍 Running comprehensive audit with indexing and issue creation..."
	@echo "📊 This will run the full audit suite and create issues if score delta > 5%"
	@echo ""
	@echo "🔄 Phase 1: Running audit completeness check..."
	python scripts/audit_completeness.py
	@echo "✅ Phase 1 complete"
	@echo ""
	@echo "🔄 Phase 2: Running audit synthesis..."
	python scripts/audit_synthesis.py
	@echo "✅ Phase 2 complete"
	@echo ""
	@echo "🔄 Phase 3: Running comprehensive audit with issue creation..."
	python scripts/audit_with_issue.py --verbose
	@echo "✅ Comprehensive audit complete!"
	@echo ""
	@echo "📋 Audit Results:"
	@echo "  - Report: docs/audit/audit_report.md"
	@echo "  - Remediation: docs/audit/remediation_plan.md"
	@echo "  - Rule Confidence: docs/audit/rule_confidence.csv"
	@echo "  - Baseline: docs/audit/coverage_baseline.json"

	@echo "CI pipeline complete!"

# Automation targets
agent-sync:
	python3 scripts/meta_audit.py
	python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
	python3 -m pip install sphinx myst-parser sphinxcontrib-mermaid sphinx-rtd-theme >/dev/null 2>&1 || true
	sphinx-build -b html docs/ docs/_build/html || true
	python3 scripts/cost_telemetry.py || true

virtue-log:
	python3 scripts/virtue_log.py || true

virtuous-cycle: agent-sync virtue-log

# Build a local PDF index (advisory/offline)
.PHONY: pdf-index
pdf-index:
	mkdir -p artifacts
	python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
	# Ensure optional deps are present
	python3 -c "import PyPDF2, yaml" 2>/dev/null || python3 -m pip install PyPDF2 pyyaml
	python3 scripts/ingest_pdfs.py --manifest data/ingestion_manifests/isa_goals_pdfs_manifest.yaml --out artifacts/pdf_index.jsonl
	@echo "✅ Wrote artifacts/pdf_index.jsonl"

# Docker commands
docker-build:
	docker build -t isa-superapp:latest .

docker-test:
	docker run --rm isa-superapp:latest make test

# Performance commands
profile:
	python -m cProfile -o profile.stats -m pytest tests/performance/
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

benchmark:
	pytest tests/performance/ --benchmark-only --benchmark-autosave

# Database commands
db-migrate:
	alembic upgrade head

db-reset:
	alembic downgrade base
	alembic upgrade head

# Cache commands
cache-clear:
	redis-cli FLUSHALL || echo "Redis not available"

# Monitoring commands
logs:
	tail -f logs/*.log || echo "No log files found"

health-check:
	curl -f http://localhost:8000/health || echo "Service not running"

# Release commands
version-patch:
	bump2version patch

version-minor:
	bump2version minor

version-major:
	bump2version major

# Git hooks
install-hooks:
	pre-commit install
	git config core.hooksPath .githooks

# Environment commands
env-check:
	@echo "Checking environment..."
	@python -c "import sys; print(f'Python: {sys.version}')"
	@pip list | grep -E "(pytest|black|isort|mypy|flake8)"
	@echo "Environment check complete!"

# Help for specific commands
help-test:
	@echo "Test Command Options:"
	@echo "  make test-unit marker=unit"
	@echo "  make test-integration marker=integration"
	@echo "  make test-performance marker=performance"
	@echo "  make test-all cov-fail-under=90"
