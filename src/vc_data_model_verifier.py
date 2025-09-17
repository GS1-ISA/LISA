"""
VC Data Model Verifier for GS1 Verifiable Credentials

This module validates GS1 VC payloads against the official GS1 data models
defined in JSON-LD ontologies and context files.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception raised for VC validation errors."""
    pass

class VCType(Enum):
    """Supported GS1 VC types."""
    TRADE_ITEM = "trade-item"
    PARTY = "party"
    LICENCE = "licence"
    LICENSE = "license"  # Alternative spelling
    DECLARATION = "declaration"
    PLANOGRAM = "planogram"

@dataclass
class ValidationResult:
    """Result of VC validation."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    vc_type: VCType | None = None

@dataclass
class PropertyDefinition:
    """Definition of a property from the ontology."""
    id: str
    type: list[str]
    domain: str | None = None
    range: str | None = None
    comment: str | None = None
    label: str | None = None
    required: bool = False

@dataclass
class VCClassDefinition:
    """Definition of a VC class from the ontology."""
    id: str
    type: list[str]
    subClassOf: str | None = None
    comment: str | None = None
    label: str | None = None
    properties: dict[str, PropertyDefinition] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

class GS1VCDataModelVerifier:
    """Verifier for GS1 VC payloads against official data models."""

    def __init__(self, models_path: str = "gs1_research/VC-Data-Model"):
        self.models_path = Path(models_path)
        self.ontologies: dict[VCType, dict[str, Any]] = {}
        self.contexts: dict[VCType, dict[str, Any]] = {}
        self.class_definitions: dict[str, VCClassDefinition] = {}
        self.property_definitions: dict[str, PropertyDefinition] = {}
        self._loaded = False

    def load_data_models(self) -> bool:
        """Load all GS1 VC data models from JSON-LD files."""
        try:
            if not self.models_path.exists():
                logger.error(f"Models path not found: {self.models_path}")
                return False

            # Load ontologies and contexts for each VC type
            for vc_type in VCType:
                ontology_file = self.models_path / f"{vc_type.value}-ontology.jsonld"
                context_file = self.models_path / f"{vc_type.value}-context.jsonld"

                if ontology_file.exists():
                    with open(ontology_file, encoding="utf-8") as f:
                        self.ontologies[vc_type] = json.load(f)
                    logger.info(f"Loaded ontology for {vc_type.value}")

                if context_file.exists():
                    with open(context_file, encoding="utf-8") as f:
                        self.contexts[vc_type] = json.load(f)
                    logger.info(f"Loaded context for {vc_type.value}")

            self._parse_ontologies()
            self._loaded = True
            logger.info("Successfully loaded all GS1 VC data models")
            return True

        except Exception as e:
            logger.error(f"Failed to load data models: {e}")
            return False

    def _parse_ontologies(self):
        """Parse ontology definitions into structured data."""
        for _vc_type, ontology in self.ontologies.items():
            if "@graph" not in ontology:
                continue

            for item in ontology["@graph"]:
                item_id = item.get("@id", "")
                item_type = item.get("@type", [])

                if isinstance(item_type, str):
                    item_type = [item_type]

                # Parse VC classes
                if "owl:Class" in item_type or "rdfs:Class" in item_type:
                    class_def = VCClassDefinition(
                        id=item_id,
                        type=item_type,
                        subClassOf=item.get("rdfs:subClassOf", {}).get("@id"),
                        comment=self._extract_value(item.get("rdfs:comment")),
                        label=self._extract_value(item.get("rdfs:label"))
                    )
                    self.class_definitions[item_id] = class_def

                # Parse properties
                elif "owl:DatatypeProperty" in item_type or "rdf:Property" in item_type:
                    prop_def = PropertyDefinition(
                        id=item_id,
                        type=item_type,
                        domain=item.get("rdfs:domain", {}).get("@id"),
                        range=item.get("rdfs:range", {}).get("@id"),
                        comment=self._extract_value(item.get("rdfs:comment")),
                        label=self._extract_value(item.get("rdfs:label"))
                    )
                    self.property_definitions[item_id] = prop_def

                    # Associate property with its domain class
                    if prop_def.domain and prop_def.domain in self.class_definitions:
                        self.class_definitions[prop_def.domain].properties[item_id] = prop_def

    def _extract_value(self, value_obj: Any) -> str | None:
        """Extract string value from JSON-LD value object."""
        if isinstance(value_obj, str):
            return value_obj
        elif isinstance(value_obj, dict):
            return value_obj.get("@value")
        return None

    def validate_vc(self, vc_payload: dict[str, Any]) -> ValidationResult:
        """Validate a GS1 VC payload against the data models."""
        if not self._loaded:
            raise ValidationError("Data models not loaded. Call load_data_models() first.")

        errors = []
        warnings = []
        vc_type = None

        try:
            # Determine VC type from the credential type
            vc_type = self._determine_vc_type(vc_payload)
            if not vc_type:
                errors.append("Unable to determine GS1 VC type from credential")
                return ValidationResult(False, errors, warnings)

            # Validate basic VC structure
            self._validate_vc_structure(vc_payload, errors, warnings)

            # Validate credential subject against ontology
            if "credentialSubject" in vc_payload:
                self._validate_credential_subject(
                    vc_payload["credentialSubject"],
                    vc_type,
                    errors,
                    warnings
                )

            # Validate context if present
            if "@context" in vc_payload:
                self._validate_context(vc_payload["@context"], vc_type, warnings)

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, vc_type)

    def _determine_vc_type(self, vc_payload: dict[str, Any]) -> VCType | None:
        """Determine the GS1 VC type from the credential."""
        vc_types = vc_payload.get("type", [])
        if isinstance(vc_types, str):
            vc_types = [vc_types]

        # Map credential types to VC types
        type_mapping = {
            "GS1VerifiedByGS1TradeItemDataCredential": VCType.TRADE_ITEM,
            "GS1VerifiedByGS1PartyDataCredential": VCType.PARTY,
            "GS1LicenceCredential": VCType.LICENCE,
            "GS1LicenseCredential": VCType.LICENSE,
            "GS1DeclarationCredential": VCType.DECLARATION,
            "GS1PlanogramCredential": VCType.PLANOGRAM
        }

        for vc_type_str in vc_types:
            if vc_type_str in type_mapping:
                return type_mapping[vc_type_str]

        return None

    def _validate_vc_structure(self, vc_payload: dict[str, Any],
                              errors: list[str], warnings: list[str]):
        """Validate basic VC structure."""
        required_fields = ["@context", "type", "credentialSubject", "issuer", "issuanceDate"]

        for field in required_fields:
            if field not in vc_payload:
                errors.append(f"Missing required field: {field}")

        # Validate issuance date format
        if "issuanceDate" in vc_payload:
            try:
                # Basic ISO format check
                issuance_date = vc_payload["issuanceDate"]
                if not isinstance(issuance_date, str) or "T" not in issuance_date:
                    warnings.append("issuanceDate should be in ISO 8601 format")
            except Exception:
                warnings.append("Invalid issuanceDate format")

        # Validate expiration date if present
        if "expirationDate" in vc_payload:
            try:
                exp_date = vc_payload["expirationDate"]
                if not isinstance(exp_date, str) or "T" not in exp_date:
                    warnings.append("expirationDate should be in ISO 8601 format")
            except Exception:
                warnings.append("Invalid expirationDate format")

    def _validate_credential_subject(self, subject: dict[str, Any],
                                    vc_type: VCType, errors: list[str], warnings: list[str]):
        """Validate credential subject against ontology."""
        if not isinstance(subject, dict):
            errors.append("credentialSubject must be an object")
            return

        # Find the appropriate class definition
        class_def = None
        for class_id, class_def_candidate in self.class_definitions.items():
            if vc_type.value in class_id.lower():
                class_def = class_def_candidate
                break

        if not class_def:
            warnings.append(f"No ontology definition found for VC type: {vc_type.value}")
            return

        # Validate properties against the class definition
        for prop_id, prop_def in class_def.properties.items():
            prop_name = prop_id.split(":")[-1]  # Extract property name from IRI

            if prop_def.required and prop_name not in subject:
                errors.append(f"Missing required property: {prop_name}")
            elif prop_name in subject:
                self._validate_property_value(
                    subject[prop_name],
                    prop_def,
                    prop_name,
                    errors,
                    warnings
                )

    def _validate_property_value(self, value: Any, prop_def: PropertyDefinition,
                                prop_name: str, errors: list[str], warnings: list[str]):
        """Validate a property value against its definition."""
        # Validate range/type
        if prop_def.range:
            expected_type = self._get_expected_type(prop_def.range)

            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Property {prop_name} must be a string")
            elif expected_type == "uri" and not isinstance(value, str):
                errors.append(f"Property {prop_name} must be a valid URI")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"Property {prop_name} must be an integer")
            elif expected_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Property {prop_name} must be a boolean")

    def _get_expected_type(self, range_iri: str) -> str | None:
        """Get expected type from range IRI."""
        type_mapping = {
            "http://www.w3.org/2001/XMLSchema#string": "string",
            "http://www.w3.org/2001/XMLSchema#anyURI": "uri",
            "http://www.w3.org/2001/XMLSchema#integer": "integer",
            "http://www.w3.org/2001/XMLSchema#boolean": "boolean",
            "http://www.w3.org/2001/XMLSchema#dateTime": "datetime"
        }
        return type_mapping.get(range_iri)

    def _validate_context(self, context: str | list | dict,
                         vc_type: VCType, warnings: list[str]):
        """Validate JSON-LD context."""
        if vc_type not in self.contexts:
            warnings.append(f"No context definition available for {vc_type.value}")
            return

        self.contexts[vc_type]

        # Basic context validation - check if required GS1 terms are present
        if isinstance(context, list):
            gs1_context_found = False
            for ctx_item in context:
                if isinstance(ctx_item, str) and "gs1.org" in ctx_item:
                    gs1_context_found = True
                    break

            if not gs1_context_found:
                warnings.append("GS1 context not found in @context")

    def get_supported_vc_types(self) -> list[VCType]:
        """Get list of supported VC types."""
        return list(self.ontologies.keys())

    def get_class_definition(self, class_id: str) -> VCClassDefinition | None:
        """Get class definition by ID."""
        return self.class_definitions.get(class_id)

    def get_property_definition(self, property_id: str) -> PropertyDefinition | None:
        """Get property definition by ID."""
        return self.property_definitions.get(property_id)
