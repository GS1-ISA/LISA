# ISA Development Makefile (aligned with current repo)
.PHONY: help install install-dev test test-core test-all lint format format-check type-check security clean build docs audit ci-local \
	dev-setup pre-commit agent-sync virtuous-cycle virtue-log pdf-index profile benchmark docker-build docker-test \
	env-check help-test

# Default target
help:
	@echo "ISA Development Commands"
	@echo "========================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         - Run core tests (agent_core/orchestrator/infra/rag)"
	@echo "  test-core    - Alias for 'test'"
	@echo "  test-all     - Run tests with coverage across core paths"
	@echo ""
	@echo "Quality Commands:"
	@echo "  lint         - ruff check"
	@echo "  format       - ruff format ."
	@echo "  format-check - ruff format --check ."
	@echo "  type-check   - mypy src/"
	@echo "  security     - bandit + pip-audit (advisory)"
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
	@echo "  ci-local     - Run local CI subset (lint/type/tests/coverage/docs/perf)"
	@echo "  agent-sync   - Refresh meta audit, docs build, cost report"
	@echo "  virtuous-cycle - Run meta audit + quick verify + log"
	@echo "  pdf-index     - Build PDF index from ISA goals PDFs into artifacts/"

# Setup commands
TEST_PATHS=src/agent_core src/orchestrator infra/rag
CORE_COV=--cov=src/agent_core --cov=src/orchestrator

install:
	python3 -m pip install -r requirements.txt || true

install-dev:
	python3 -m pip install -r requirements.txt || true
	python3 -m pip install -r requirements-dev.txt || true

dev-setup: install-dev
	pre-commit install
	mkdir -p logs
	mkdir -p data/cache
	mkdir -p data/vector_store
	@echo "Development setup complete!"

# Testing commands
test:
	pytest -q -n auto $(TEST_PATHS)

test-core: test

test-all:
	pytest -q -n auto $(TEST_PATHS) $(CORE_COV) --cov-report=term-missing --cov-report=xml

# Quality commands
lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

type-check:
	mypy src/ || true

security:
	bandit -r src/ scripts/ || true
	pip-audit -r requirements.txt || true

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
	@echo "No packaging configured for this repo variant."

docs:
	sphinx-build -b html docs/ docs/_build/html

# Development commands
pre-commit:
	pre-commit run --all-files || true

ci-local: format-check lint type-check test-all docs
	python3 scripts/perf_hist.py --runs 50 --out perf_histogram.json || true
	python3 scripts/memory_coherence_gate.py --log agent/memory/memory_log.jsonl || true
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

# Docker commands (optional)
docker-build:
	@echo "No container configured in this repo variant."

docker-test:
	@echo "No container configured in this repo variant."

# Performance commands
profile:
	python -m cProfile -o profile.stats -m pytest tests/performance/
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

benchmark:
	pytest tests/performance/ --benchmark-only --benchmark-autosave

# Removed legacy DB/cache/health commands not applicable to this repo variant

# Release commands
# Release commands (not configured for this variant)
version-patch:
	@echo "No versioning configured."

version-minor:
	@echo "No versioning configured."

version-major:
	@echo "No versioning configured."

# Git hooks
install-hooks:
	pre-commit install
	git config core.hooksPath .githooks

# Environment commands
env-check:
	@echo "Checking environment..."
	@python3 -c "import sys; print(f'Python: {sys.version}')"
	@python3 -c "import ruff,pytest,mypy,bandit; print('ruff/pytest/mypy/bandit OK')" 2>/dev/null || true
	@echo "Environment check complete!"

# Help for specific commands
help-test:
	@echo "Test Command Options:"
	@echo "  make test         # run core tests in parallel"
	@echo "  make test-all     # run with coverage + XML"
