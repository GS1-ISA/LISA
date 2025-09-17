"""
RDF/SHACL Semantic Validation System for ISA_D

This module provides comprehensive semantic web validation capabilities using
RDF (Resource Description Framework) and SHACL (Shapes Constraint Language)
for validating GS1 standards, ESG data, and regulatory compliance schemas.

Key Features:
- Ontology validation and constraint checking
- GS1 standards compliance validation
- ESG data semantic validation
- Regulatory compliance schema validation
- Integration with ISA_D's existing data validation workflows
"""

from .converter import RDFConverter
from .engine import SHACLEngine
from .schemas import ESGSchemas, GS1Schemas, RegulatorySchemas
from .validator import SemanticValidator, ValidationResult

__all__ = [
    "SemanticValidator",
    "ValidationResult",
    "GS1Schemas",
    "ESGSchemas",
    "RegulatorySchemas",
    "RDFConverter",
    "SHACLEngine"
]
