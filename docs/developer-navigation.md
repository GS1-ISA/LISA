# ISA_D Developer Navigation Guide

This guide helps developers navigate the ISA_D codebase, understand common workflows, and find relevant files efficiently.

## 🗺️ Quick Navigation Map

### By Function

| What you want to do | Where to look |
|---------------------|---------------|
| **Add new API endpoint** | `src/api_server.py`, `src/` modules |
| **Implement agent logic** | `src/agent_core/`, `agent/` |
| **Add compliance rule** | `src/dmn/`, `src/gs1_*` |
| **Process documents** | `src/docs_provider/` |
| **Database operations** | `src/database_manager.py` |
| **Frontend component** | `frontend/src/components/` |
| **Infrastructure change** | `infra/`, `helm/`, `k8s/` |
| **Add automation script** | `scripts/` |
| **Research experiment** | `experiments/`, `data/` |

### By Technology

| Technology | Primary Location |
|------------|------------------|
| **Python/FastAPI** | `src/`, `scripts/` |
| **React/Next.js** | `frontend/` |
| **Kubernetes** | `k8s/`, `helm/` |
| **Terraform/Ansible** | `infra/` |
| **Docker** | `Dockerfile`, `docker-compose.yml` |
| **Configuration** | `.env`, `config/`, `data/` |

## 🔍 Finding Files by Purpose

### Core Application Logic

```
# Main entry points
src/api_server.py          # FastAPI application
src/main.py                 # Alternative entry point

# Agent system
src/agent_core/             # Agent architecture
├── planner.py             # Task planning
├── builder.py             # Execution building
├── critic.py              # Quality assessment
└── verifier.py            # Validation

# Domain modules
src/gs1_*.py               # GS1 standards
src/dmn/                   # Decision modeling
src/docs_provider/         # Document processing
src/llm/                   # LLM integration
```

### Configuration and Settings

```
# Application config
.env                        # Environment variables
.env.example               # Config template
src/config/               # App configuration
data/data_catalog.yaml    # Data assets

# Infrastructure
helm/isa-superapp/values.yaml    # Helm values
k8s/                        # K8s manifests
infra/                     # Infrastructure code

# Development
pyproject.toml            # Python project
package.json              # Node.js dependencies
Makefile                  # Build automation
```

### Testing and Quality

```
# Test suites
tests/                     # Main test directory
src/*/tests/              # Module-specific tests
frontend/__tests__/       # Frontend tests

# Quality tools
scripts/audit_*.py        # Audit scripts
scripts/validate_*.py     # Validation tools
scripts/test_*.py         # Testing utilities

# CI/CD
.github/workflows/        # GitHub Actions
scripts/deploy_*.sh       # Deployment scripts
```

## 🚀 Common Development Workflows

### 1. Adding a New Feature

```bash
# 1. Understand requirements
# Check existing similar features
grep -r "feature_name" src/ docs/

# 2. Plan implementation
# Review architecture docs
cat docs/project-structure.md

# 3. Implement backend
# Add to appropriate module
vim src/feature_module.py

# 4. Add API endpoint
vim src/api_server.py

# 5. Update frontend
cd frontend/
npm run dev
vim src/components/FeatureComponent.tsx

# 6. Add tests
vim tests/test_feature.py

# 7. Update documentation
vim docs/feature_guide.md
```

### 2. Fixing a Bug

```bash
# 1. Reproduce the issue
# Check logs and error messages
tail -f logs/application.log

# 2. Find relevant code
# Search for error keywords
grep -r "error_message" src/

# 3. Understand the flow
# Check function calls and data flow
grep -r "function_name" src/

# 4. Implement fix
vim src/buggy_module.py

# 5. Add test case
vim tests/test_bug_fix.py

# 6. Verify fix
python -m pytest tests/test_bug_fix.py
```

### 3. Database Schema Change

```bash
# 1. Review current schema
# Check existing models
grep -r "class.*Model" src/

# 2. Plan migration
# Understand dependencies
grep -r "database_table" src/

# 3. Update models
vim src/database_manager.py

# 4. Create migration script
vim scripts/migrate_database.py

# 5. Test migration
python scripts/migrate_database.py --dry-run

# 6. Update documentation
vim docs/database_schema.md
```

### 4. Performance Optimization

```bash
# 1. Identify bottleneck
# Check performance logs
grep -r "performance\|slow" logs/

# 2. Profile code
python -m cProfile src/performance_issue.py

# 3. Review caching
# Check existing cache usage
grep -r "cache\|redis" src/

# 4. Implement optimization
vim src/optimized_module.py

# 5. Add benchmarks
vim scripts/bench_optimization.py

# 6. Update monitoring
vim infra/monitoring/prometheus.yml
```

## 📋 Code Patterns and Conventions

### Python Code Structure

```python
# Standard module structure
"""
Module docstring describing purpose and usage.
"""

import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ModuleClass:
    """Class docstring."""

    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def public_method(self, param: str) -> dict:
        """Public method with type hints."""
        try:
            # Implementation
            result = self._private_method(param)
            return result
        except Exception as e:
            self.logger.error(f"Error in public_method: {e}")
            raise

    def _private_method(self, param: str) -> dict:
        """Private helper method."""
        # Implementation
        return {"result": param}
```

### API Endpoint Pattern

```python
# src/api_server.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    """Request data model."""
    name: str
    value: Optional[int] = None

class ResponseModel(BaseModel):
    """Response data model."""
    id: int
    result: str
    timestamp: str

@router.post("/endpoint", response_model=ResponseModel)
async def endpoint_handler(request: RequestModel):
    """Endpoint docstring."""
    try:
        # Business logic
        result = await process_request(request)
        return ResponseModel(
            id=generate_id(),
            result=result,
            timestamp=get_timestamp()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### React Component Pattern

```typescript
// frontend/src/components/Component.tsx
import React, { useState, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'

interface ComponentProps {
  title: string
  onAction?: (data: any) => void
}

export default function Component({ title, onAction }: ComponentProps) {
  const { state, dispatch } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/data')
      const data = await response.json()
      dispatch({ type: 'SET_DATA', payload: data })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleAction = () => {
    if (onAction) {
      onAction({ type: 'action', payload: state.data })
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="component">
      <h2>{title}</h2>
      <button onClick={handleAction}>Action</button>
    </div>
  )
}
```

## 🔧 Development Tools

### Local Development

```bash
# Start full stack
docker-compose up

# Run backend only
cd src/
python -m uvicorn api_server:socket_app --reload

# Run frontend only
cd frontend/
npm run dev

# Run tests
pytest

# Check code quality
ruff check .
mypy .
```

### Debugging

```bash
# Debug API requests
curl -v http://localhost:8001/api/debug

# Check logs
tail -f logs/application.log

# Debug database
python scripts/debug_database.py

# Profile performance
python -m cProfile -s cumtime src/profile_target.py
```

### Database Operations

```bash
# Check database status
python scripts/check_db_status.py

# Run migrations
python scripts/migrate_database.py

# Backup database
python scripts/backup_database.py

# Restore database
python scripts/restore_database.py
```

## 📊 Monitoring and Observability

### Application Metrics

```bash
# Check application health
curl http://localhost:8001/health

# View metrics
curl http://localhost:8001/metrics

# Check agent status
curl http://localhost:8001/api/agents/status
```

### System Monitoring

```bash
# Check system resources
python scripts/check_system_resources.py

# Monitor performance
python scripts/performance_monitor.py

# View logs
tail -f logs/*.log
```

### Error Tracking

```bash
# Search for errors
grep -r "ERROR" logs/

# Check recent errors
tail -n 100 logs/application.log | grep ERROR

# Debug specific error
python scripts/debug_error.py --error-id 12345
```

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **API not responding** | Check `src/api_server.py`, verify port 8001 |
| **Database connection failed** | Check `.env` DATABASE_URL, verify DB running |
| **Frontend not loading** | Check `frontend/` build, verify port 3000 |
| **Agent not responding** | Check `agent/` logs, verify agent configuration |
| **Build failing** | Check dependencies, clear cache, rebuild |

### Getting Help

1. **Check documentation**: `docs/` directory
2. **Search codebase**: `grep -r "keyword" .`
3. **Check logs**: `logs/` directory
4. **Review tests**: `tests/` directory
5. **Ask team**: Create issue or discussion

## 📚 Advanced Navigation

### Cross-References

```bash
# Find all references to a function
grep -r "function_name" .

# Find all imports of a module
grep -r "from module import" .

# Find all API endpoints
grep -r "@router\." src/

# Find all database models
grep -r "class.*Model" src/
```

### Dependency Analysis

```bash
# Check Python dependencies
pip list

# Check Node.js dependencies
cd frontend/
npm list

# Find circular imports
python scripts/check_circular_imports.py
```

### Code Search Patterns

```bash
# Find TODO comments
grep -r "TODO\|FIXME" .

# Find hardcoded values
grep -r "http://localhost" .

# Find security issues
grep -r "password\|secret\|key" .

# Find performance issues
grep -r "sleep\|time.sleep" .
```

## 🎯 Best Practices

### Code Organization
- Keep related code together
- Use clear module boundaries
- Follow single responsibility principle
- Document complex logic

### Development Workflow
- Write tests first
- Use feature branches
- Review code changes
- Deploy incrementally

### Performance
- Profile before optimizing
- Cache expensive operations
- Use async where appropriate
- Monitor resource usage

### Security
- Validate all inputs
- Use secure defaults
- Rotate secrets regularly
- Log security events

This navigation guide should help you efficiently work with the ISA_D codebase and understand its structure and workflows.