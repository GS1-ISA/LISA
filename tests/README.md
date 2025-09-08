# ISA SuperApp Test Suite

This directory contains the comprehensive test suite for the ISA SuperApp project.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── requirements-test.txt    # Test dependencies
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_vector_store.py
│   ├── test_orchestrator.py
│   └── test_retrieval.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_vector_store_integration.py
│   └── test_orchestrator_integration.py
├── performance/             # Performance tests
│   ├── test_vector_performance.py
│   └── test_api_performance.py
└── fixtures/                # Test data and fixtures
    ├── sample_documents/
    └── test_data/
```

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
python run_tests.py all

# Run unit tests only
python run_tests.py unit

# Run integration tests only
python run_tests.py integration

# Run specific test file
python run_tests.py specific --test-file tests/unit/test_config.py

# Run specific test function
python run_tests.py specific --test-file tests/unit/test_config.py --test-function test_config_initialization
```

### Advanced Usage

```bash
# Generate comprehensive test report
python run_tests.py report

# Check test coverage (must be >= 80%)
python run_tests.py coverage

# Run tests in parallel
python run_tests.py all --parallel

# Run with verbose output
python run_tests.py all --verbose

# Run without coverage
python run_tests.py all --no-coverage
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual components in isolation
- Fast execution
- No external dependencies
- Mock external services

### Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- May use real external services
- Slower execution
- Test actual data flow

### Performance Tests (`@pytest.mark.performance`)
- Measure execution time
- Test scalability
- Memory usage monitoring
- Load testing

### Security Tests (`@pytest.mark.security`)
- Input validation
- Authentication/authorization
- Data sanitization
- Vulnerability scanning

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `test_config`: Test configuration instance
- `mock_vector_store`: Mock vector store for testing
- `mock_orchestrator`: Mock orchestrator for testing
- `sample_documents`: Sample documents for testing
- `mock_logger`: Mock logger for testing

## Test Data

Test data is organized in the `fixtures/` directory:

- `sample_documents/`: Sample documents for testing
- `test_data/`: Various test data files
- `configs/`: Test configuration files

## Coverage Requirements

- Minimum coverage: 80%
- Critical modules: 90%
- New code: 85%

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Main branch commits
- Nightly builds

## Writing Tests

### Basic Test Structure

```python
import pytest
from isa_superapp.core.config import Config

@pytest.mark.unit
def test_config_initialization(sample_config_data):
    """Test configuration initialization."""
    config = Config(sample_config_data)
    assert config.app_name == "ISA_SuperApp"
    assert config.debug is False
```

### Async Test Structure

```python
import pytest
from isa_superapp.vector_store.base import VectorStore

@pytest.mark.integration
@pytest.mark.asyncio
async def test_vector_store_operations(mock_vector_store):
    """Test vector store operations."""
    result = await mock_vector_store.search("test query")
    assert len(result) > 0
    assert all(hasattr(doc, 'score') for doc in result)
```

### Parametrized Tests

```python
import pytest

@pytest.mark.unit
@pytest.mark.parametrize("input_value,expected_output", [
    ("valid_input", True),
    ("invalid_input", False),
    ("", False),
    (None, False)
])
def test_input_validation(input_value, expected_output):
    """Test input validation with various inputs."""
    result = validate_input(input_value)
    assert result == expected_output
```

## Debugging Tests

### Using PDB

```bash
# Run tests with PDB debugger
pytest --pdb tests/unit/test_config.py

# Run tests with IPython debugger
pytest --ipdb tests/unit/test_config.py
```

### Verbose Output

```bash
# Run with verbose output
pytest -v tests/unit/test_config.py

# Run with debug logging
pytest --log-cli-level=DEBUG tests/unit/test_config.py
```

## Performance Testing

### Benchmarking

```bash
# Run performance tests
pytest tests/performance/ --benchmark-only

# Generate performance report
pytest tests/performance/ --benchmark-json=performance.json
```

### Memory Profiling

```bash
# Run with memory profiling
pytest tests/unit/test_vector_store.py --memory

# Generate memory usage report
mprof run pytest tests/unit/test_vector_store.py
mprof plot
```

## Security Testing

### Static Analysis

```bash
# Run security linting
bandit -r isa_superapp/

# Run dependency vulnerability scan
safety check

# Run comprehensive security scan
semgrep --config=auto isa_superapp/
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Async test failures**: Check `pytest-asyncio` configuration
3. **Mock issues**: Verify mock setup and expectations
4. **Database connection errors**: Check test database configuration
5. **Timeout errors**: Increase timeout values for slow tests

### Debug Mode

```bash
# Enable debug mode
export DEBUG=1
pytest tests/unit/test_config.py

# Enable detailed logging
export LOG_LEVEL=DEBUG
pytest tests/unit/test_config.py
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use appropriate markers (`@pytest.mark.unit`, etc.)
3. Add fixtures to `conftest.py` if reusable
4. Document test purpose and expected behavior
5. Ensure tests are deterministic and isolated
6. Maintain or improve coverage requirements

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Async Testing Guide](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)