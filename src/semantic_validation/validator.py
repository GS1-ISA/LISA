"""
Main Semantic Validator for RDF/SHACL validation system.

This module provides the core validation functionality for semantic web data
validation using RDF and SHACL constraints.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from rdflib import Graph

from .converter import RDFConverter
from .engine import SHACLEngine
from .schemas import ESGSchemas, GS1Schemas, RegulatorySchemas

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error with detailed information."""
    error_type: str
    message: str
    focus_node: str | None = None
    result_path: str | None = None
    value: Any | None = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Comprehensive validation result with detailed reporting."""
    is_valid: bool
    conforms: bool
    validation_time: float
    total_violations: int
    total_warnings: int
    total_info: int
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    info_messages: list[ValidationError] = field(default_factory=list)
    validated_graph: Graph | None = None
    shapes_graph: Graph | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert validation result to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "conforms": self.conforms,
            "validation_time": self.validation_time,
            "total_violations": self.total_violations,
            "total_warnings": self.total_warnings,
            "total_info": self.total_info,
            "errors": [vars(e) for e in self.errors],
            "warnings": [vars(e) for e in self.warnings],
            "info_messages": [vars(e) for e in self.info_messages],
            "timestamp": self.timestamp.isoformat()
        }


class SemanticValidator:
    """
    Main semantic validator for RDF/SHACL validation.

    Provides comprehensive validation capabilities for:
    - GS1 standards compliance
    - ESG data validation
    - Regulatory compliance schemas
    - Ontology validation
    - Custom SHACL constraints
    """

    def __init__(self,
                 enable_ontology_validation: bool = True,
                 enable_constraint_checking: bool = True,
                 strict_mode: bool = False):
        self.enable_ontology_validation = enable_ontology_validation
        self.enable_constraint_checking = enable_constraint_checking
        self.strict_mode = strict_mode

        # Initialize components
        self.engine = SHACLEngine()
        self.converter = RDFConverter()
        self.schemas = {
            "gs1": GS1Schemas(),
            "esg": ESGSchemas(),
            "regulatory": RegulatorySchemas()
        }

        logger.info("Initialized SemanticValidator with ontology validation: %s, constraint checking: %s",
                   enable_ontology_validation, enable_constraint_checking)

    def validate_gs1_data(self, data: dict[str, Any],
                         schema_type: str = "product") -> ValidationResult:
        """
        Validate GS1 data against GS1 SHACL schemas.

        Args:
            data: GS1 data to validate
            schema_type: Type of GS1 schema (product, location, etc.)

        Returns:
            ValidationResult with detailed validation information
        """
        try:
            start_time = datetime.now()

            # Convert data to RDF
            rdf_graph = self.converter.convert_gs1_data(data, schema_type)

            # Get appropriate SHACL schema
            shapes_graph = self.schemas["gs1"].get_schema(schema_type)

            # Perform validation
            result = self.engine.validate(rdf_graph, shapes_graph)

            validation_time = (datetime.now() - start_time).total_seconds()

            return ValidationResult(
                is_valid=result.conforms,
                conforms=result.conforms,
                validation_time=validation_time,
                total_violations=len(result.violations) if hasattr(result, "violations") else 0,
                total_warnings=len(result.warnings) if hasattr(result, "warnings") else 0,
                total_info=len(result.info) if hasattr(result, "info") else 0,
                errors=self._parse_validation_errors(result, "error"),
                warnings=self._parse_validation_errors(result, "warning"),
                info_messages=self._parse_validation_errors(result, "info"),
                validated_graph=rdf_graph,
                shapes_graph=shapes_graph
            )

        except Exception as e:
            logger.error(f"GS1 validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                conforms=False,
                validation_time=0.0,
                total_violations=1,
                total_warnings=0,
                total_info=0,
                errors=[ValidationError(
                    error_type="validation_error",
                    message=f"GS1 validation failed: {str(e)}",
                    severity="error"
                )]
            )

    def validate_esg_data(self, data: dict[str, Any],
                         framework: str = "csrd") -> ValidationResult:
        """
        Validate ESG data against ESG SHACL schemas.

        Args:
            data: ESG data to validate
            framework: ESG framework (csrd, sfdr, etc.)

        Returns:
            ValidationResult with detailed validation information
        """
        try:
            start_time = datetime.now()

            # Convert data to RDF
            rdf_graph = self.converter.convert_esg_data(data, framework)

            # Get appropriate SHACL schema
            shapes_graph = self.schemas["esg"].get_schema(framework)

            # Perform validation
            result = self.engine.validate(rdf_graph, shapes_graph)

            validation_time = (datetime.now() - start_time).total_seconds()

            return ValidationResult(
                is_valid=result.conforms,
                conforms=result.conforms,
                validation_time=validation_time,
                total_violations=len(result.violations) if hasattr(result, "violations") else 0,
                total_warnings=len(result.warnings) if hasattr(result, "warnings") else 0,
                total_info=len(result.info) if hasattr(result, "info") else 0,
                errors=self._parse_validation_errors(result, "error"),
                warnings=self._parse_validation_errors(result, "warning"),
                info_messages=self._parse_validation_errors(result, "info"),
                validated_graph=rdf_graph,
                shapes_graph=shapes_graph
            )

        except Exception as e:
            logger.error(f"ESG validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                conforms=False,
                validation_time=0.0,
                total_violations=1,
                total_warnings=0,
                total_info=0,
                errors=[ValidationError(
                    error_type="validation_error",
                    message=f"ESG validation failed: {str(e)}",
                    severity="error"
                )]
            )

    def validate_regulatory_data(self, data: dict[str, Any],
                               regulation: str = "eudr") -> ValidationResult:
        """
        Validate regulatory compliance data against regulatory SHACL schemas.

        Args:
            data: Regulatory data to validate
            regulation: Regulation type (eudr, csrd, etc.)

        Returns:
            ValidationResult with detailed validation information
        """
        try:
            start_time = datetime.now()

            # Convert data to RDF
            rdf_graph = self.converter.convert_regulatory_data(data, regulation)

            # Get appropriate SHACL schema
            shapes_graph = self.schemas["regulatory"].get_schema(regulation)

            # Perform validation
            result = self.engine.validate(rdf_graph, shapes_graph)

            validation_time = (datetime.now() - start_time).total_seconds()

            return ValidationResult(
                is_valid=result.conforms,
                conforms=result.conforms,
                validation_time=validation_time,
                total_violations=len(result.violations) if hasattr(result, "violations") else 0,
                total_warnings=len(result.warnings) if hasattr(result, "warnings") else 0,
                total_info=len(result.info) if hasattr(result, "info") else 0,
                errors=self._parse_validation_errors(result, "error"),
                warnings=self._parse_validation_errors(result, "warning"),
                info_messages=self._parse_validation_errors(result, "info"),
                validated_graph=rdf_graph,
                shapes_graph=shapes_graph
            )

        except Exception as e:
            logger.error(f"Regulatory validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                conforms=False,
                validation_time=0.0,
                total_violations=1,
                total_warnings=0,
                total_info=0,
                errors=[ValidationError(
                    error_type="validation_error",
                    message=f"Regulatory validation failed: {str(e)}",
                    severity="error"
                )]
            )

    def validate_custom_schema(self, data_graph: Graph,
                              shapes_graph: Graph) -> ValidationResult:
        """
        Validate RDF data against custom SHACL shapes.

        Args:
            data_graph: RDF graph containing data to validate
            shapes_graph: RDF graph containing SHACL shapes

        Returns:
            ValidationResult with detailed validation information
        """
        try:
            start_time = datetime.now()

            # Perform validation
            result = self.engine.validate(data_graph, shapes_graph)

            validation_time = (datetime.now() - start_time).total_seconds()

            return ValidationResult(
                is_valid=result.conforms,
                conforms=result.conforms,
                validation_time=validation_time,
                total_violations=len(result.violations) if hasattr(result, "violations") else 0,
                total_warnings=len(result.warnings) if hasattr(result, "warnings") else 0,
                total_info=len(result.info) if hasattr(result, "info") else 0,
                errors=self._parse_validation_errors(result, "error"),
                warnings=self._parse_validation_errors(result, "warning"),
                info_messages=self._parse_validation_errors(result, "info"),
                validated_graph=data_graph,
                shapes_graph=shapes_graph
            )

        except Exception as e:
            logger.error(f"Custom schema validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                conforms=False,
                validation_time=0.0,
                total_violations=1,
                total_warnings=0,
                total_info=0,
                errors=[ValidationError(
                    error_type="validation_error",
                    message=f"Custom schema validation failed: {str(e)}",
                    severity="error"
                )]
            )

    def _parse_validation_errors(self, result: Any, severity: str) -> list[ValidationError]:
        """Parse validation errors from SHACL validation result."""
        errors = []

        # This is a simplified parsing - actual implementation would depend on pyshacl result structure
        if hasattr(result, "violations") and severity == "error":
            for violation in result.violations:
                errors.append(ValidationError(
                    error_type=getattr(violation, "constraint", "unknown"),
                    message=getattr(violation, "message", "Validation violation"),
                    focus_node=str(getattr(violation, "focus_node", "")),
                    result_path=str(getattr(violation, "result_path", "")),
                    value=getattr(violation, "value", None),
                    severity=severity
                ))

        if hasattr(result, "warnings") and severity == "warning":
            for warning in result.warnings:
                errors.append(ValidationError(
                    error_type=getattr(warning, "constraint", "unknown"),
                    message=getattr(warning, "message", "Validation warning"),
                    focus_node=str(getattr(warning, "focus_node", "")),
                    result_path=str(getattr(warning, "result_path", "")),
                    value=getattr(warning, "value", None),
                    severity=severity
                ))

        if hasattr(result, "info") and severity == "info":
            for info in result.info:
                errors.append(ValidationError(
                    error_type=getattr(info, "constraint", "unknown"),
                    message=getattr(info, "message", "Validation info"),
                    focus_node=str(getattr(info, "focus_node", "")),
                    result_path=str(getattr(info, "result_path", "")),
                    value=getattr(info, "value", None),
                    severity=severity
                ))

        return errors
