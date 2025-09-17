# ISA_D Naming Conventions

This document establishes consistent naming conventions across the ISA_D project to improve code readability, maintainability, and developer experience.

## 📋 General Principles

### Consistency
- Use the same naming patterns throughout the codebase
- Follow language-specific conventions
- Prefer descriptive names over abbreviations
- Use consistent casing

### Clarity
- Names should be self-documenting
- Avoid ambiguous abbreviations
- Use full words when possible
- Consider the context and scope

### Scope
- Local variables: short, clear names
- Global variables: descriptive, prefixed
- Functions: verb-based names
- Classes: noun-based names

## 🐍 Python Naming Conventions

### Files and Modules

```python
# Module files
snake_case.py              # Regular modules
test_module.py            # Test modules
__init__.py               # Package initialization

# Special cases
api_server.py            # Main application entry
database_manager.py       # Manager classes
gs1_parser.py            # Domain-specific parsers
```

### Classes and Types

```python
# Class names
class AgentCore:          # PascalCase
class DatabaseManager:    # PascalCase
class GS1Parser:         # PascalCase with abbreviations

# Type hints
from typing import Optional, List, Dict

def process_data(data: Dict[str, Any]) -> Optional[Result]:
    # Implementation

# Generic types
T = TypeVar('T')
ResultType = Union[Success, Error]
```

### Functions and Methods

```python
# Functions
def process_document(doc: Document) -> ProcessedDocument:
def validate_gs1_code(code: str) -> bool:
def get_agent_status(agent_id: str) -> AgentStatus:

# Private methods
def _validate_input(self, data: dict) -> bool:
def _process_batch(self, items: List[Item]) -> List[Result]:

# Async functions
async def fetch_research_data(query: str) -> ResearchData:
async def process_agent_task(task: Task) -> TaskResult:
```

### Variables and Constants

```python
# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_VERSION = "v1.0"

# Module-level variables
_logger = logging.getLogger(__name__)
_cache = {}

# Local variables
result = process_data(input_data)
items = []
total_count = 0

# Loop variables
for item in items:
for i, value in enumerate(values):
```

### Imports

```python
# Standard library
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import fastapi
from pydantic import BaseModel
import sqlalchemy as sa

# Local modules
from .agent_core import AgentCore
from ..utils import helper_function
from src.config import get_config
```

## ⚛️ JavaScript/TypeScript Naming Conventions

### Files and Modules

```typescript
// Component files
Button.tsx                // PascalCase
ChatInterface.tsx         // PascalCase
DocumentViewer.tsx        // PascalCase

// Utility files
apiClient.ts              // camelCase
validationUtils.ts        // camelCase
typeDefinitions.ts        // camelCase

// Test files
Button.test.tsx           // Same as component
apiClient.test.ts         // Same as module
```

### Components and Classes

```typescript
// React components
function Button({ children, onClick }: ButtonProps) {
  // Implementation
}

const ChatInterface: React.FC<ChatProps> = ({ messages }) => {
  // Implementation
}

// Class components (if used)
class DocumentViewer extends React.Component<DocumentProps> {
  // Implementation
}
```

### Functions and Methods

```typescript
// Regular functions
function validateEmail(email: string): boolean {
  // Implementation
}

const processDocument = (doc: Document): ProcessedDoc => {
  // Implementation
}

// Async functions
async function fetchUserData(userId: string): Promise<User> {
  // Implementation
}

const loadResearchData = async (query: string): Promise<Data[]> => {
  // Implementation
}
```

### Variables and Constants

```typescript
// Constants
const MAX_FILE_SIZE = 10 * 1024 * 1024
const API_BASE_URL = '/api/v1'
const DEFAULT_THEME = 'light'

// Component state
const [isLoading, setIsLoading] = useState(false)
const [userData, setUserData] = useState<User | null>(null)

// Local variables
let result = processData(input)
const items: Item[] = []
let totalCount = 0
```

### Types and Interfaces

```typescript
// Interfaces
interface User {
  id: string
  name: string
  email: string
}

interface ApiResponse<T> {
  data: T
  error?: string
  status: number
}

// Types
type UserRole = 'admin' | 'user' | 'guest'
type ApiResult<T> = Success<T> | Error

// Generic types
type Optional<T> = T | undefined
type Dictionary<T> = Record<string, T>
```

## 📁 Directory and File Naming

### Directory Structure

```
# Source directories
src/                      # Main source
├── agent_core/          # Agent architecture
├── api_server.py       # API server
├── config/              # Configuration
├── docs_provider/       # Document processing
└── utils/               # Utilities

# Test directories
tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── e2e/                # End-to-end tests

# Documentation
docs/
├── api/                 # API documentation
├── guides/              # User guides
└── architecture/        # Architecture docs
```

### File Naming Patterns

```
# Python files
module_name.py           # Regular modules
test_module.py          # Test files
__init__.py             # Package init
conftest.py             # Test configuration

# Configuration files
config.yaml             # YAML config
settings.json           # JSON config
.env.example            # Environment template

# Documentation
README.md               # Directory documentation
CHANGELOG.md            # Version history
CONTRIBUTING.md         # Contribution guide

# Scripts
deploy.sh               # Deployment scripts
build.py               # Build scripts
migrate.sql            # Database migrations
```

## 🏷️ Domain-Specific Naming

### Agent-Related

```python
# Agent classes
class ResearchAgent:
class ComplianceAgent:
class PlanningAgent:

# Agent methods
def plan_task(self, task: Task) -> Plan:
def execute_plan(self, plan: Plan) -> Result:
def review_result(self, result: Result) -> Feedback:

# Agent data
agent_config = {}
agent_memory = {}
agent_state = {}
```

### GS1 Standards

```python
# GS1 classes
class GS1Parser:
class GS1Validator:
class GS1Resolver:

# GS1 functions
def parse_gtin(gtin: str) -> GTIN:
def validate_sscc(sscc: str) -> bool:
def resolve_digital_link(url: str) -> Product:

# GS1 data
gtin_code = "12345678901234"
sscc_code = "123456789012345678"
gln_number = "1234567890123"
```

### API Endpoints

```python
# API routes
@app.get("/api/v1/agents")
@app.post("/api/v1/research")
@app.put("/api/v1/compliance/{id}")

# API functions
def get_agents() -> List[Agent]:
def create_research_task(task: Task) -> TaskId:
def update_compliance_rule(rule_id: str, rule: Rule) -> None:
```

## 🗄️ Database Naming

### Tables

```sql
-- Table names
agents
research_tasks
compliance_rules
documents
users

-- Join tables
agent_research_tasks
document_compliance_rules
```

### Columns

```sql
-- Column names
id (primary key)
created_at (timestamp)
updated_at (timestamp)
name (varchar)
description (text)
status (enum)
```

### Indexes

```sql
-- Index names
idx_agents_status
idx_research_tasks_created_at
idx_compliance_rules_type
```

## 🔧 Configuration Naming

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://localhost/isa
DATABASE_POOL_SIZE=10

# API
API_HOST=0.0.0.0
API_PORT=8001

# Security
SECRET_KEY=your-secret-key
JWT_EXPIRATION=3600

# External services
OPENROUTER_API_KEY=sk-...
REDIS_URL=redis://localhost:6379
```

### Configuration Files

```yaml
# config.yaml
app:
  name: isa-d
  version: "1.0.0"
  debug: false

database:
  url: "${DATABASE_URL}"
  pool_size: 10

api:
  host: "${API_HOST}"
  port: "${API_PORT}"

agents:
  research:
    enabled: true
    max_concurrent: 5
  compliance:
    enabled: true
    rules_path: "/config/rules"
```

## 📝 Documentation Naming

### Files

```
# README files
README.md                 # Project overview
docs/README.md           # Documentation index
src/README.md            # Source code guide

# Guide files
getting-started.md       # Setup guide
api-reference.md         # API documentation
troubleshooting.md       # Problem solving
```

### Sections

```markdown
# Main headings
# ISA_D Project

## Secondary headings
## Installation

### Tertiary headings
### Prerequisites

#### Code blocks
```bash
npm install
```

#### Lists
- Item 1
- Item 2

#### Links
[Link text](url)
```

## 🧪 Testing Naming

### Test Files

```python
# Unit tests
test_agent_core.py
test_gs1_parser.py
test_api_endpoints.py

# Integration tests
test_agent_workflow.py
test_database_integration.py

# E2E tests
test_full_workflow.py
```

### Test Functions

```python
def test_agent_initialization():
def test_gs1_parsing_valid_code():
def test_api_returns_agents_list():
def test_database_connection_pool():
```

### Test Data

```python
# Test fixtures
@pytest.fixture
def sample_agent():
    return Agent(id="test-123", name="Test Agent")

@pytest.fixture
def valid_gs1_code():
    return "12345678901234"

# Mock data
mock_response = {"status": "success", "data": []}
mock_agent = Agent(id="mock-123", capabilities=[])
```

## 🚀 Deployment Naming

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Container naming
LABEL maintainer="isa-team@company.com"
LABEL version="1.0.0"

# Image naming
# isa-d/api-server:latest
# isa-d/agent-core:v1.2.3
```

### Kubernetes

```yaml
# Resource naming
apiVersion: apps/v1
kind: Deployment
metadata:
  name: isa-api-server
  labels:
    app: isa-api-server
    component: api

---
apiVersion: v1
kind: Service
metadata:
  name: isa-api-service
  labels:
    app: isa-api-service
```

### Helm

```yaml
# Chart structure
isa-superapp/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl
```

## 📊 Monitoring and Logging

### Log Messages

```python
# Log levels
logger.debug("Processing document: %s", doc_id)
logger.info("Agent task completed: %s", task_id)
logger.warning("Rate limit approaching: %d/%d", current, limit)
logger.error("Failed to process document: %s", str(e))
logger.critical("System shutdown required")
```

### Metrics

```python
# Metric names
AGENT_TASKS_COMPLETED = Counter('agent_tasks_completed_total', 'Total tasks completed')
API_REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')
DATABASE_CONNECTIONS_ACTIVE = Gauge('db_connections_active', 'Active connections')
```

## 🔄 Implementation Guidelines

### Code Reviews

- [ ] Naming conventions followed
- [ ] Consistent with existing patterns
- [ ] Self-documenting names used
- [ ] Abbreviations explained

### Automated Checks

```python
# Add to CI/CD
- name: Check naming conventions
  run: |
    python scripts/check_naming_conventions.py

- name: Lint code
  run: |
    ruff check --select N  # pep8-naming
    mypy --strict
```

### Tool Configuration

```toml
# pyproject.toml
[tool.ruff]
select = ["E", "F", "N"]  # Include naming checks

[tool.mypy]
strict = true
disallow_any_untyped = true
```

This naming convention guide ensures consistency across the ISA_D project and improves code maintainability and developer productivity.