# ISA_D Scripts Directory

This directory contains automation scripts, utilities, and tools for the ISA_D platform.

## 📁 Organization

Scripts are organized by function and purpose:

### Audit & Quality Assurance

| Script | Purpose |
|--------|---------|
| `audit_*.py` | Code and data auditing |
| `validate_*.py` | Validation and verification |
| `check_*.py` | Health checks and diagnostics |
| `meta_audit.py` | Meta-level auditing |

### Build & Deployment

| Script | Purpose |
|--------|---------|
| `deploy_*.sh` | Deployment automation |
| `build_*.sh` | Build processes |
| `setup_*.sh` | Environment setup |
| `configure_*.sh` | Configuration management |

### Data Processing

| Script | Purpose |
|--------|---------|
| `ingest_*.py` | Data ingestion pipelines |
| `process_*.py` | Data processing workflows |
| `evaluate_*.py` | Research evaluation |

### Monitoring & Operations

| Script | Purpose |
|--------|---------|
| `healthcheck.py` | System health monitoring |
| `performance_*.py` | Performance analysis |
| `backup_*.sh` | Backup operations |
| `rollback_*.sh` | Rollback procedures |

### Research & Development

| Script | Purpose |
|--------|---------|
| `research/` | Research-specific scripts |
| `bench_*.py` | Benchmarking tools |
| `test_*.py` | Testing utilities |
| `optimize_*.sh` | Optimization tools |

## 🚀 Usage

### Running Scripts

Most scripts can be executed directly:

```bash
# Python scripts
python scripts/audit_inventory.py

# Shell scripts
./scripts/deploy_orchestrator.sh

# With arguments
python scripts/validate_audit_mechanisms.py --verbose
```

### Common Patterns

#### Audit Scripts
```bash
# Run comprehensive audit
python scripts/meta_audit.py

# Validate audit mechanisms
python scripts/validate_audit_mechanisms.py
```

#### Deployment Scripts
```bash
# Deploy to development
./scripts/deploy_orchestrator.sh dev

# Setup environment
./scripts/setup-unified-cicd.sh
```

#### Data Processing
```bash
# Ingest research data
python scripts/ingest_pdfs.py

# Evaluate research results
python scripts/evaluate_research.py
```

## 📋 Script Categories

### 🔍 Audit Scripts

**Purpose**: Ensure code quality, data integrity, and system compliance

- `audit_coherence.py` - Check system coherence
- `audit_completeness.py` - Verify completeness
- `audit_gates.py` - Quality gate validation
- `audit_inventory.py` - System inventory
- `audit_md_rules.py` - Documentation rule checking
- `audit_rule_normalize.py` - Rule normalization
- `audit_synthesis.py` - Audit synthesis
- `audit_traceability.py` - Traceability verification

### 🏗️ Build & Deploy Scripts

**Purpose**: Automate build, test, and deployment processes

- `deploy_orchestrator.py` - Orchestrator deployment
- `deploy-docker.sh` - Docker deployment
- `deploy-ecs.sh` - AWS ECS deployment
- `deploy-kubernetes.sh` - Kubernetes deployment
- `deploy-with-gating.sh` - Gated deployment
- `setup-unified-cicd.sh` - CI/CD setup

### 📊 Data & Research Scripts

**Purpose**: Handle data processing and research workflows

- `ingest_pdfs.py` - PDF document ingestion
- `ingest_text.py` - Text data ingestion
- `evaluate_research.py` - Research evaluation
- `research/run_poc.py` - Proof of concept execution

### ⚡ Performance & Optimization

**Purpose**: Monitor and optimize system performance

- `bench_q11_orjson.py` - JSON processing benchmarks
- `bench_q12_validation.py` - Validation benchmarks
- `optimize-caching.sh` - Cache optimization
- `perf_budget_check.py` - Performance budget checking
- `perf_hist.py` - Performance history analysis

### 🛠️ Utility Scripts

**Purpose**: General utilities and maintenance

- `auto_doc_update.py` - Documentation updates
- `auto_git.sh` - Git automation
- `backup-validation.sh` - Backup validation
- `generate_ssl_cert.sh` - SSL certificate generation
- `prune_bloat.py` - Cleanup utilities
- `save_baselines.py` - Baseline saving

## ⚙️ Configuration

### Environment Variables

Many scripts use environment variables for configuration:

```bash
# Database connection
export DATABASE_URL="sqlite:///isa.db"

# API keys (secure storage recommended)
export OPENROUTER_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Logging level
export LOG_LEVEL="INFO"
```

### Configuration Files

Scripts may use configuration files:

- `.env` - Environment variables
- `config/` - Application configuration
- `pyproject.toml` - Python project settings

## 🔧 Development

### Adding New Scripts

1. **Choose appropriate category** based on function
2. **Follow naming conventions**:
   - `snake_case.py` for Python scripts
   - `kebab-case.sh` for shell scripts
   - `descriptive_name` for clarity

3. **Include documentation**:
   - Docstrings for Python functions
   - Comments for shell scripts
   - Usage examples

4. **Error handling**:
   - Graceful failure handling
   - Clear error messages
   - Logging integration

### Script Template

```python
#!/usr/bin/env python3
"""
Script Name: Brief description

Usage:
    python scripts/script_name.py [options]

Options:
    --help          Show this help
    --verbose, -v   Verbose output
    --dry-run       Show what would be done
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)

    # Script logic here
    if args.dry_run:
        print("DRY RUN: Would execute script logic")
        return

    # Actual execution
    print("Executing script...")

if __name__ == "__main__":
    main()
```

## 📊 Monitoring & Logging

### Logging Integration

Scripts integrate with the platform's logging system:

```python
import logging
from src.audit_logger import get_logger

logger = get_logger(__name__)
logger.info("Script started")
```

### Performance Tracking

Performance-critical scripts include timing:

```python
import time
start_time = time.time()

# Script execution

duration = time.time() - start_time
logger.info(f"Script completed in {duration:.2f}s")
```

## 🔒 Security Considerations

### API Key Handling
- Never hardcode API keys
- Use environment variables
- Implement secure key rotation

### File Permissions
- Scripts should have appropriate permissions
- Sensitive data handling
- Secure temporary file usage

### Network Security
- Validate SSL certificates
- Use secure protocols
- Implement rate limiting

## 📚 Related Documentation

- [Project Structure](../docs/project-structure.md)
- [Development Guide](../docs/)
- [Deployment Guide](../docs/)
- [Security Policy](../SECURITY.md)

These scripts provide essential automation and tooling for the ISA_D platform's operation, development, and maintenance.