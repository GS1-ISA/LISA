"""
SHACL schemas for regulatory compliance validation.

This module contains SHACL shape definitions for validating regulatory
compliance data including EUDR, CSRD, and GDPR.
"""

import logging
from typing import Dict, Any, Optional

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, XSD

logger = logging.getLogger(__name__)

# Regulatory namespace
REG = URIRef("https://www.regulatory.org/voc/")
SH = Namespace("http://www.w3.org/ns/shacl#")


class RegulatorySchemas:
    """
    SHACL schemas for regulatory compliance validation.

    Provides validation shapes for:
    - EUDR (EU Deforestation Regulation)
    - CSRD (Corporate Sustainability Reporting Directive)
    - GDPR (General Data Protection Regulation)
    """

    def __init__(self):
        self._schemas = {}
        self._load_schemas()

    def get_schema(self, regulation: str) -> Graph:
        """
        Get SHACL schema for the specified regulation.

        Args:
            regulation: Regulation type (eudr, csrd, gdpr)

        Returns:
            RDF graph containing SHACL shapes
        """
        if regulation not in self._schemas:
            raise ValueError(f"Unknown regulation: {regulation}")

        return self._schemas[regulation]

    def _load_schemas(self):
        """Load all regulatory SHACL schemas."""
        self._schemas['eudr'] = self._create_eudr_schema()
        self._schemas['csrd'] = self._create_csrd_regulatory_schema()
        self._schemas['gdpr'] = self._create_gdpr_schema()

        logger.info("Loaded regulatory SHACL schemas")

    def _create_eudr_schema(self) -> Graph:
        """Create SHACL schema for EUDR validation."""
        g = Graph()
        g.bind("reg", REG)
        g.bind("sh", SH)

        # EUDR Operator shape
        operator_shape = URIRef(f"{REG}EUDROperatorShape")

        g.add((operator_shape, RDF.type, SH.NodeShape))
        g.add((operator_shape, SH.targetClass, URIRef(f"{REG}EUDROperator")))

        # Operator ID constraint
        operator_id_prop = BNode()
        g.add((operator_shape, SH.property, operator_id_prop))
        g.add((operator_id_prop, SH.path, URIRef(f"{REG}operatorId")))
        g.add((operator_id_prop, SH.minCount, Literal(1)))
        g.add((operator_id_prop, SH.maxCount, Literal(1)))
        g.add((operator_id_prop, SH.datatype, XSD.string))

        # Operator name constraint
        name_prop = BNode()
        g.add((operator_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{REG}operatorName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Country constraint
        country_prop = BNode()
        g.add((operator_shape, SH.property, country_prop))
        g.add((country_prop, SH.path, URIRef(f"{REG}country")))
        g.add((country_prop, SH.minCount, Literal(1)))
        g.add((country_prop, SH.datatype, XSD.string))

        # Due diligence - Risk assessment
        risk_assessment_prop = BNode()
        g.add((operator_shape, SH.property, risk_assessment_prop))
        g.add((risk_assessment_prop, SH.path, URIRef(f"{REG}dueDiligence_riskAssessment")))
        g.add((risk_assessment_prop, SH.datatype, XSD.string))

        # Due diligence - Information traceability
        traceability_prop = BNode()
        g.add((operator_shape, SH.property, traceability_prop))
        g.add((traceability_prop, SH.path, URIRef(f"{REG}dueDiligence_traceability")))
        g.add((traceability_prop, SH.datatype, XSD.boolean))

        # Due diligence - Risk mitigation
        mitigation_prop = BNode()
        g.add((operator_shape, SH.property, mitigation_prop))
        g.add((mitigation_prop, SH.path, URIRef(f"{REG}dueDiligence_riskMitigation")))
        g.add((mitigation_prop, SH.datatype, XSD.string))

        # Product categories
        categories_prop = BNode()
        g.add((operator_shape, SH.property, categories_prop))
        g.add((categories_prop, SH.path, URIRef(f"{REG}dueDiligence_productCategories")))
        g.add((categories_prop, SH.datatype, XSD.string))

        return g

    def _create_csrd_regulatory_schema(self) -> Graph:
        """Create SHACL schema for CSRD regulatory validation."""
        g = Graph()
        g.bind("reg", REG)
        g.bind("sh", SH)

        # CSRD Entity shape
        entity_shape = URIRef(f"{REG}CSRDEntityShape")

        g.add((entity_shape, RDF.type, SH.NodeShape))
        g.add((entity_shape, SH.targetClass, URIRef(f"{REG}CSRDEntity")))

        # LEI constraint
        lei_prop = BNode()
        g.add((entity_shape, SH.property, lei_prop))
        g.add((lei_prop, SH.path, URIRef(f"{REG}lei")))
        g.add((lei_prop, SH.minCount, Literal(1)))
        g.add((lei_prop, SH.maxCount, Literal(1)))
        g.add((lei_prop, SH.datatype, XSD.string))
        g.add((lei_prop, SH.pattern, Literal(r"^[A-Z0-9]{20}$")))

        # Entity name constraint
        name_prop = BNode()
        g.add((entity_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{REG}entityName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Sector constraint
        sector_prop = BNode()
        g.add((entity_shape, SH.property, sector_prop))
        g.add((sector_prop, SH.path, URIRef(f"{REG}sector")))
        g.add((sector_prop, SH.datatype, XSD.string))

        # Reporting period
        reporting_period_prop = BNode()
        g.add((entity_shape, SH.property, reporting_period_prop))
        g.add((reporting_period_prop, SH.path, URIRef(f"{REG}reporting_reportingPeriod")))
        g.add((reporting_period_prop, SH.datatype, XSD.gYear))

        # Assurance level
        assurance_prop = BNode()
        g.add((entity_shape, SH.property, assurance_prop))
        g.add((assurance_prop, SH.path, URIRef(f"{REG}reporting_assuranceLevel")))
        g.add((assurance_prop, SH.datatype, XSD.string))

        # Double materiality assessment
        materiality_prop = BNode()
        g.add((entity_shape, SH.property, materiality_prop))
        g.add((materiality_prop, SH.path, URIRef(f"{REG}reporting_doubleMateriality")))
        g.add((materiality_prop, SH.datatype, XSD.boolean))

        return g

    def _create_gdpr_schema(self) -> Graph:
        """Create SHACL schema for GDPR validation."""
        g = Graph()
        g.bind("reg", REG)
        g.bind("sh", SH)

        # GDPR Controller shape
        controller_shape = URIRef(f"{REG}GDPRControllerShape")

        g.add((controller_shape, RDF.type, SH.NodeShape))
        g.add((controller_shape, SH.targetClass, URIRef(f"{REG}GDPRController")))

        # Controller ID constraint
        controller_id_prop = BNode()
        g.add((controller_shape, SH.property, controller_id_prop))
        g.add((controller_id_prop, SH.path, URIRef(f"{REG}controllerId")))
        g.add((controller_id_prop, SH.minCount, Literal(1)))
        g.add((controller_id_prop, SH.maxCount, Literal(1)))
        g.add((controller_id_prop, SH.datatype, XSD.string))

        # Controller name constraint
        name_prop = BNode()
        g.add((controller_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{REG}controllerName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Processing Activity shape
        activity_shape = URIRef(f"{REG}ProcessingActivityShape")
        g.add((activity_shape, RDF.type, SH.NodeShape))

        # Link processing activities to controller
        activities_prop = BNode()
        g.add((controller_shape, SH.property, activities_prop))
        g.add((activities_prop, SH.path, URIRef(f"{REG}processingActivity")))
        g.add((activities_prop, SH.node, activity_shape))

        # Processing activity properties
        purpose_prop = BNode()
        g.add((activity_shape, SH.property, purpose_prop))
        g.add((purpose_prop, SH.path, URIRef(f"{REG}purpose")))
        g.add((purpose_prop, SH.minCount, Literal(1)))
        g.add((purpose_prop, SH.datatype, XSD.string))

        legal_basis_prop = BNode()
        g.add((activity_shape, SH.property, legal_basis_prop))
        g.add((legal_basis_prop, SH.path, URIRef(f"{REG}legalBasis")))
        g.add((legal_basis_prop, SH.minCount, Literal(1)))
        g.add((legal_basis_prop, SH.datatype, XSD.string))

        data_categories_prop = BNode()
        g.add((activity_shape, SH.property, data_categories_prop))
        g.add((data_categories_prop, SH.path, URIRef(f"{REG}dataCategories")))
        g.add((data_categories_prop, SH.datatype, XSD.string))

        retention_period_prop = BNode()
        g.add((activity_shape, SH.property, retention_period_prop))
        g.add((retention_period_prop, SH.path, URIRef(f"{REG}retentionPeriod")))
        g.add((retention_period_prop, SH.datatype, XSD.duration))

        # Data subject rights
        rights_prop = BNode()
        g.add((activity_shape, SH.property, rights_prop))
        g.add((rights_prop, SH.path, URIRef(f"{REG}dataSubjectRights")))
        g.add((rights_prop, SH.datatype, XSD.string))

        # DPIA required
        dpia_prop = BNode()
        g.add((activity_shape, SH.property, dpia_prop))
        g.add((dpia_prop, SH.path, URIRef(f"{REG}dpiaRequired")))
        g.add((dpia_prop, SH.datatype, XSD.boolean))

        return g