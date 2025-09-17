"""
SHACL schemas for ESG data validation.

This module contains SHACL shape definitions for validating ESG data
including CSRD, SFDR, and TCFD frameworks.
"""

import logging

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

logger = logging.getLogger(__name__)

# ESG namespace
ESG = URIRef("https://www.esg.org/voc/")
SH = Namespace("http://www.w3.org/ns/shacl#")


class ESGSchemas:
    """
    SHACL schemas for ESG data validation.

    Provides validation shapes for:
    - CSRD (Corporate Sustainability Reporting Directive)
    - SFDR (Sustainable Finance Disclosure Regulation)
    - TCFD (Task Force on Climate-related Financial Disclosures)
    """

    def __init__(self):
        self._schemas = {}
        self._load_schemas()

    def get_schema(self, framework: str) -> Graph:
        """
        Get SHACL schema for the specified ESG framework.

        Args:
            framework: ESG framework (csrd, sfdr, tcfd)

        Returns:
            RDF graph containing SHACL shapes
        """
        if framework not in self._schemas:
            raise ValueError(f"Unknown ESG framework: {framework}")

        return self._schemas[framework]

    def _load_schemas(self):
        """Load all ESG SHACL schemas."""
        self._schemas["csrd"] = self._create_csrd_schema()
        self._schemas["sfdr"] = self._create_sfdr_schema()
        self._schemas["tcfd"] = self._create_tcfd_schema()

        logger.info("Loaded ESG SHACL schemas")

    def _create_csrd_schema(self) -> Graph:
        """Create SHACL schema for CSRD validation."""
        g = Graph()
        g.bind("esg", ESG)
        g.bind("sh", SH)

        # Company shape
        company_shape = URIRef(f"{ESG}CompanyShape")

        g.add((company_shape, RDF.type, SH.NodeShape))
        g.add((company_shape, SH.targetClass, URIRef(f"{ESG}Company")))

        # LEI constraint
        lei_prop = BNode()
        g.add((company_shape, SH.property, lei_prop))
        g.add((lei_prop, SH.path, URIRef(f"{ESG}lei")))
        g.add((lei_prop, SH.minCount, Literal(1)))
        g.add((lei_prop, SH.maxCount, Literal(1)))
        g.add((lei_prop, SH.datatype, XSD.string))
        g.add((lei_prop, SH.pattern, Literal(r"^[A-Z0-9]{20}$")))  # LEI format

        # Company name constraint
        name_prop = BNode()
        g.add((company_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{ESG}companyName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Environmental metrics
        env_scope1_prop = BNode()
        g.add((company_shape, SH.property, env_scope1_prop))
        g.add((env_scope1_prop, SH.path, URIRef(f"{ESG}environmental_scope1Emissions")))
        g.add((env_scope1_prop, SH.datatype, XSD.decimal))
        g.add((env_scope1_prop, SH.minInclusive, Literal(0)))

        env_scope2_prop = BNode()
        g.add((company_shape, SH.property, env_scope2_prop))
        g.add((env_scope2_prop, SH.path, URIRef(f"{ESG}environmental_scope2Emissions")))
        g.add((env_scope2_prop, SH.datatype, XSD.decimal))
        g.add((env_scope2_prop, SH.minInclusive, Literal(0)))

        env_scope3_prop = BNode()
        g.add((company_shape, SH.property, env_scope3_prop))
        g.add((env_scope3_prop, SH.path, URIRef(f"{ESG}environmental_scope3Emissions")))
        g.add((env_scope3_prop, SH.datatype, XSD.decimal))
        g.add((env_scope3_prop, SH.minInclusive, Literal(0)))

        # Social metrics
        employees_prop = BNode()
        g.add((company_shape, SH.property, employees_prop))
        g.add((employees_prop, SH.path, URIRef(f"{ESG}social_totalEmployees")))
        g.add((employees_prop, SH.datatype, XSD.integer))
        g.add((employees_prop, SH.minInclusive, Literal(0)))

        # Governance metrics
        board_prop = BNode()
        g.add((company_shape, SH.property, board_prop))
        g.add((board_prop, SH.path, URIRef(f"{ESG}governance_boardSize")))
        g.add((board_prop, SH.datatype, XSD.integer))
        g.add((board_prop, SH.minInclusive, Literal(1)))

        return g

    def _create_sfdr_schema(self) -> Graph:
        """Create SHACL schema for SFDR validation."""
        g = Graph()
        g.bind("esg", ESG)
        g.bind("sh", SH)

        # Financial Entity shape
        entity_shape = URIRef(f"{ESG}FinancialEntityShape")

        g.add((entity_shape, RDF.type, SH.NodeShape))
        g.add((entity_shape, SH.targetClass, URIRef(f"{ESG}FinancialEntity")))

        # LEI constraint
        lei_prop = BNode()
        g.add((entity_shape, SH.property, lei_prop))
        g.add((lei_prop, SH.path, URIRef(f"{ESG}lei")))
        g.add((lei_prop, SH.minCount, Literal(1)))
        g.add((lei_prop, SH.maxCount, Literal(1)))
        g.add((lei_prop, SH.datatype, XSD.string))
        g.add((lei_prop, SH.pattern, Literal(r"^[A-Z0-9]{20}$")))

        # Entity name constraint
        name_prop = BNode()
        g.add((entity_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{ESG}entityName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # SFDR Article constraint
        article_prop = BNode()
        g.add((entity_shape, SH.property, article_prop))
        g.add((article_prop, SH.path, URIRef(f"{ESG}sfdrArticle")))
        g.add((article_prop, SH.datatype, XSD.string))

        # PAI metrics (Principal Adverse Impact)
        pai_ghg_prop = BNode()
        g.add((entity_shape, SH.property, pai_ghg_prop))
        g.add((pai_ghg_prop, SH.path, URIRef(f"{ESG}pai_ghgEmissions")))
        g.add((pai_ghg_prop, SH.datatype, XSD.decimal))

        pai_energy_prop = BNode()
        g.add((entity_shape, SH.property, pai_energy_prop))
        g.add((pai_energy_prop, SH.path, URIRef(f"{ESG}pai_energyConsumption")))
        g.add((pai_energy_prop, SH.datatype, XSD.decimal))

        pai_water_prop = BNode()
        g.add((entity_shape, SH.property, pai_water_prop))
        g.add((pai_water_prop, SH.path, URIRef(f"{ESG}pai_waterConsumption")))
        g.add((pai_water_prop, SH.datatype, XSD.decimal))

        return g

    def _create_tcfd_schema(self) -> Graph:
        """Create SHACL schema for TCFD validation."""
        g = Graph()
        g.bind("esg", ESG)
        g.bind("sh", SH)

        # Organization shape
        org_shape = URIRef(f"{ESG}OrganizationShape")

        g.add((org_shape, RDF.type, SH.NodeShape))
        g.add((org_shape, SH.targetClass, URIRef(f"{ESG}Organization")))

        # LEI constraint
        lei_prop = BNode()
        g.add((org_shape, SH.property, lei_prop))
        g.add((lei_prop, SH.path, URIRef(f"{ESG}lei")))
        g.add((lei_prop, SH.minCount, Literal(1)))
        g.add((lei_prop, SH.maxCount, Literal(1)))
        g.add((lei_prop, SH.datatype, XSD.string))
        g.add((lei_prop, SH.pattern, Literal(r"^[A-Z0-9]{20}$")))

        # Organization name constraint
        name_prop = BNode()
        g.add((org_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{ESG}organizationName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Climate-related metrics
        # Governance
        governance_prop = BNode()
        g.add((org_shape, SH.property, governance_prop))
        g.add((governance_prop, SH.path, URIRef(f"{ESG}climate_governance")))
        g.add((governance_prop, SH.datatype, XSD.string))

        # Strategy
        strategy_prop = BNode()
        g.add((org_shape, SH.property, strategy_prop))
        g.add((strategy_prop, SH.path, URIRef(f"{ESG}climate_strategy")))
        g.add((strategy_prop, SH.datatype, XSD.string))

        # Risk Management
        risk_prop = BNode()
        g.add((org_shape, SH.property, risk_prop))
        g.add((risk_prop, SH.path, URIRef(f"{ESG}climate_riskManagement")))
        g.add((risk_prop, SH.datatype, XSD.string))

        # Metrics and Targets
        metrics_prop = BNode()
        g.add((org_shape, SH.property, metrics_prop))
        g.add((metrics_prop, SH.path, URIRef(f"{ESG}climate_metricsTargets")))
        g.add((metrics_prop, SH.datatype, XSD.string))

        # Scope 1, 2, 3 emissions
        scope1_prop = BNode()
        g.add((org_shape, SH.property, scope1_prop))
        g.add((scope1_prop, SH.path, URIRef(f"{ESG}climate_scope1Emissions")))
        g.add((scope1_prop, SH.datatype, XSD.decimal))
        g.add((scope1_prop, SH.minInclusive, Literal(0)))

        scope2_prop = BNode()
        g.add((org_shape, SH.property, scope2_prop))
        g.add((scope2_prop, SH.path, URIRef(f"{ESG}climate_scope2Emissions")))
        g.add((scope2_prop, SH.datatype, XSD.decimal))
        g.add((scope2_prop, SH.minInclusive, Literal(0)))

        scope3_prop = BNode()
        g.add((org_shape, SH.property, scope3_prop))
        g.add((scope3_prop, SH.path, URIRef(f"{ESG}climate_scope3Emissions")))
        g.add((scope3_prop, SH.datatype, XSD.decimal))
        g.add((scope3_prop, SH.minInclusive, Literal(0)))

        return g
