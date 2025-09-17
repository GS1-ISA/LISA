# ISA_D Source Code

This directory contains the core source code for the ISA_D (Intelligent Standards Assistant) platform.

## 📁 Structure Overview

The source code is organized by functional domains and architectural layers:

### Core Application Files

| File | Purpose |
|------|---------|
| `api_server.py` | FastAPI server with Socket.io for real-time communication |
| `audit_logger.py` | Comprehensive audit logging system |
| `auth.py` | Authentication and authorization modules |
| `database_manager.py` | Database operations and connection management |
| `encryption.py` | Encryption utilities for data protection |
| `feature_flags.py` | Feature flag management for controlled rollouts |
| `performance_monitor.py` | System performance monitoring and metrics |

### Domain-Specific Modules

| Module | Purpose |
|--------|---------|
| `agent_core/` | Agent architecture with planner, builder, critic roles |
| `orchestrator/` | Workflow orchestration using LangGraph |
| `docs_provider/` | Document processing and knowledge extraction |
| `dmn/` | Decision Model and Notation for compliance rules |
| `llm/` | Multi-provider LLM runtime with caching |
| `cache/` | Multi-level caching system |
| `config/` | Configuration management modules |
| `geospatial/` | Location-based compliance and risk assessment |
| `privacy_preserving_ai/` | Federated learning and encryption |
| `semantic_validation/` | Semantic validation of standards |
| `taxonomy/` | Taxonomy management and classification |

### Integration Modules

| Module | Purpose |
|--------|---------|
| `gs1_*.py` | GS1 standards parsing and validation |
| `neo4j_*.py` | Graph database integration for knowledge graphs |
| `opa_integration.py` | Open Policy Agent for authorization |
| `vc_*.py` | Verifiable credentials for attestations |
| `epcis_tracker.py` | EPCIS event tracking for supply chains |
| `end_to_end_traceability.py` | Complete supply chain traceability |

## 🔧 Key Components

### Agent Core Architecture

The `agent_core/` module provides the foundation for intelligent agents:

- **Planner**: Plans execution steps and tool usage
- **Builder**: Applies patches and executes changes
- **Critic**: Provides structured review and feedback
- **Verifier**: Runs quality gates and validation
- **Reward**: Learning and optimization signals

### Orchestration Layer

The `orchestrator/` module manages complex workflows:

- Graph-based workflow definitions
- Async coordination between agents
- State management and persistence
- Error handling and recovery

### Research and Knowledge

The `docs_provider/` module handles document processing:

- PDF and text extraction
- Knowledge base construction
- Vector embeddings for retrieval
- Provenance tracking

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required dependencies (see `requirements.txt`)

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
python -m uvicorn api_server:socket_app --reload
```

### Key Entry Points
- **API Server**: `python api_server.py`
- **Agent Runner**: Import from `agent_core`
- **Orchestrator**: Import from `orchestrator`

## 📋 Code Organization Principles

### File Naming
- `snake_case.py` for utility modules
- `CamelCase.py` for class-focused files
- `*_integration.py` for external service integrations
- `test_*.py` for unit tests

### Module Structure
- `__init__.py` for package initialization
- Clear separation of concerns
- Dependency injection patterns
- Type hints throughout

### Error Handling
- Structured logging with context
- Graceful degradation
- Comprehensive error messages
- Recovery mechanisms

## 🔗 Dependencies

### Internal Dependencies
```
api_server.py
├── agent_core/ (agent orchestration)
├── orchestrator/ (workflow management)
├── llm/ (AI services)
├── cache/ (performance optimization)
└── config/ (configuration management)
```

### External Dependencies
- **FastAPI**: Web framework
- **LangGraph**: Workflow orchestration
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **Redis**: Caching and session storage
- **Neo4j**: Graph database

## 🧪 Testing

### Test Structure
- `tests/` directory at project root
- Unit tests for individual modules
- Integration tests for component interaction
- End-to-end tests for workflows

### Running Tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_agent_core/

# With coverage
pytest --cov=src --cov-report=html
```

## 📊 Performance Considerations

### Optimization Areas
- **Caching**: Multi-level cache in `cache/`
- **Async Processing**: Non-blocking operations
- **Memory Management**: Efficient data structures
- **Database Optimization**: Query optimization and indexing

### Monitoring
- Performance metrics collection
- Resource usage tracking
- Bottleneck identification
- Automated optimization suggestions

## 🤝 Contributing

### Code Standards
- Type hints required
- Docstrings for public APIs
- Unit tests for new features
- Integration with existing patterns

### Development Workflow
1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit pull request

## 📚 Related Documentation

- [Project Architecture](../docs/project-structure.md)
- [API Documentation](../docs/)
- [Agent Architecture](../docs/agents/AGENTS.md)
- [Orchestration Guide](../docs/agents/ORCHESTRATION_ARCHITECTURE.md)

This source code structure provides a solid foundation for the ISA_D platform's intelligent standards assistance capabilities.