# RDF/SHACL Semantic Validation System

This module provides comprehensive semantic web validation capabilities for ISA_D using RDF (Resource Description Framework) and SHACL (Shapes Constraint Language).

## Overview

The semantic validation system enables advanced data validation for:
- **GS1 Standards**: Product, location, asset, and event data validation
- **ESG Data**: CSRD, SFDR, and TCFD framework compliance validation
- **Regulatory Compliance**: EUDR, GDPR, and other regulatory schema validation

## Architecture

### Core Components

1. **SemanticValidator**: Main validation orchestrator
2. **SHACLEngine**: SHACL constraint validation engine
3. **RDFConverter**: Data format conversion to RDF
4. **Schema Modules**: Domain-specific SHACL shape definitions

### Key Features

- **Ontology Validation**: Validates data against formal ontologies
- **Constraint Checking**: Enforces business rules and data integrity
- **Multi-format Support**: Converts various data formats to RDF
- **Integration Ready**: Seamlessly integrates with ISA_D's existing workflows

## Usage

### Basic Validation

```python
from semantic_validation import SemanticValidator

validator = SemanticValidator()

# Validate GS1 product data
gs1_data = {
    'gtin': '1234567890128',
    'brand': 'Test Brand',
    'name': 'Test Product'
}

result = validator.validate_gs1_data(gs1_data)
print(f"Validation result: {result.is_valid}")
```

### ESG Data Validation

```python
esg_data = {
    'lei': '5493001KJTIIGC14Q5',
    'name': 'Test Company',
    'environmental': {'scope1Emissions': 1000.0},
    'social': {'totalEmployees': 500},
    'governance': {'boardSize': 8}
}

result = validator.validate_esg_data(esg_data, framework='csrd')
```

### Regulatory Compliance Validation

```python
regulatory_data = {
    'operator_id': 'OP123456',
    'name': 'Test Operator',
    'country': 'Germany',
    'due_diligence': {
        'riskAssessment': 'low',
        'traceability': True
    }
}

result = validator.validate_regulatory_data(regulatory_data, regulation='eudr')
```

### Custom Schema Validation

```python
from rdflib import Graph

# Load your custom data and shapes
data_graph = Graph()
shapes_graph = Graph()

# Add your RDF data and SHACL shapes...

result = validator.validate_custom_schema(data_graph, shapes_graph)
```

## Pipeline Integration

The semantic validation system integrates with ISA_D's optimized regulatory pipeline:

```python
from src.optimized_pipeline import get_optimized_regulatory_pipeline

pipeline = get_optimized_regulatory_pipeline()

# Process documents with semantic validation
results = await pipeline.process_regulatory_documents(document_paths)
```

## Schema Definitions

### GS1 Schemas
- **Product Schema**: GTIN, brand, name, description validation
- **Location Schema**: GLN, coordinates, address validation
- **Asset Schema**: GRAI, asset type validation
- **Event Schema**: EPCIS event validation

### ESG Schemas
- **CSRD Schema**: Environmental, social, governance metrics
- **SFDR Schema**: PAI indicators, article compliance
- **TCFD Schema**: Climate-related disclosures

### Regulatory Schemas
- **EUDR Schema**: Due diligence, risk assessment
- **GDPR Schema**: Processing activities, data subject rights
- **CSRD Regulatory**: Reporting requirements, materiality

## Validation Results

Validation results include:
- **Conformance Status**: Whether data conforms to schema
- **Violation Details**: Specific constraint violations
- **Warning Information**: Non-critical issues
- **Performance Metrics**: Validation timing and statistics

## Error Handling

The system provides comprehensive error reporting:
- **Validation Errors**: Critical constraint violations
- **Warnings**: Recommended improvements
- **Info Messages**: Additional validation insights

## Testing

Run the test suite:

```bash
pytest src/semantic_validation/tests/
```

## Dependencies

- `rdflib>=7.0.0`: RDF processing
- `pyshacl>=0.25.0`: SHACL validation engine

## Configuration

Configure validation options:

```python
validator = SemanticValidator(
    enable_ontology_validation=True,
    enable_constraint_checking=True,
    strict_mode=False
)
```

## Performance Considerations

- **Caching**: Validation results are cached for repeated validations
- **Streaming**: Large datasets are processed in streams
- **Parallel Processing**: Multiple validations can run concurrently

## Future Enhancements

- **Ontology Reasoning**: Advanced OWL reasoning capabilities
- **Federated Validation**: Distributed validation across multiple systems
- **Machine Learning**: AI-powered validation rule discovery
- **Real-time Validation**: Streaming validation for live data