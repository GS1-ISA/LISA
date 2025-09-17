"""
RDF Data Converter for transforming various data formats to RDF.

This module provides converters for transforming GS1 data, ESG data,
and regulatory compliance data into RDF graphs for SHACL validation.
"""

import logging
from datetime import datetime
from typing import Any

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, FOAF, RDF, RDFS, XSD

logger = logging.getLogger(__name__)

# Define custom namespaces
GS1 = Namespace("https://www.gs1.org/voc/")
ESG = Namespace("https://www.esg.org/voc/")
REG = Namespace("https://www.regulatory.org/voc/")
ISA = Namespace("https://www.isa-d.org/voc/")


class RDFConverter:
    """
    RDF converter for transforming various data formats to RDF graphs.

    Supports conversion of:
    - GS1 product/location/asset data
    - ESG disclosure data
    - Regulatory compliance data
    - Custom data structures
    """

    def __init__(self):
        self.namespaces = {
            "gs1": GS1,
            "esg": ESG,
            "reg": REG,
            "isa": ISA,
            "rdf": RDF,
            "rdfs": RDFS,
            "xsd": XSD,
            "foaf": FOAF,
            "dc": DC
        }

    def convert_gs1_data(self, data: dict[str, Any], data_type: str = "product") -> Graph:
        """
        Convert GS1 data to RDF graph.

        Args:
            data: GS1 data dictionary
            data_type: Type of GS1 data (product, location, asset, etc.)

        Returns:
            RDF graph representation of GS1 data
        """
        graph = Graph()
        self._bind_namespaces(graph)

        try:
            if data_type == "product":
                self._convert_gs1_product(graph, data)
            elif data_type == "location":
                self._convert_gs1_location(graph, data)
            elif data_type == "asset":
                self._convert_gs1_asset(graph, data)
            elif data_type == "event":
                self._convert_gs1_event(graph, data)
            else:
                raise ValueError(f"Unsupported GS1 data type: {data_type}")

            logger.debug(f"Converted GS1 {data_type} data to RDF graph with {len(graph)} triples")
            return graph

        except Exception as e:
            logger.error(f"Failed to convert GS1 data: {e}")
            raise

    def convert_esg_data(self, data: dict[str, Any], framework: str = "csrd") -> Graph:
        """
        Convert ESG data to RDF graph.

        Args:
            data: ESG data dictionary
            framework: ESG framework (csrd, sfdr, etc.)

        Returns:
            RDF graph representation of ESG data
        """
        graph = Graph()
        self._bind_namespaces(graph)

        try:
            if framework == "csrd":
                self._convert_esg_csrd(graph, data)
            elif framework == "sfdr":
                self._convert_esg_sfdr(graph, data)
            elif framework == "tcfd":
                self._convert_esg_tcfd(graph, data)
            else:
                raise ValueError(f"Unsupported ESG framework: {framework}")

            logger.debug(f"Converted ESG {framework} data to RDF graph with {len(graph)} triples")
            return graph

        except Exception as e:
            logger.error(f"Failed to convert ESG data: {e}")
            raise

    def convert_regulatory_data(self, data: dict[str, Any], regulation: str = "eudr") -> Graph:
        """
        Convert regulatory compliance data to RDF graph.

        Args:
            data: Regulatory data dictionary
            regulation: Regulation type (eudr, csrd, etc.)

        Returns:
            RDF graph representation of regulatory data
        """
        graph = Graph()
        self._bind_namespaces(graph)

        try:
            if regulation == "eudr":
                self._convert_regulatory_eudr(graph, data)
            elif regulation == "csrd":
                self._convert_regulatory_csrd(graph, data)
            elif regulation == "gdpr":
                self._convert_regulatory_gdpr(graph, data)
            else:
                raise ValueError(f"Unsupported regulation: {regulation}")

            logger.debug(f"Converted regulatory {regulation} data to RDF graph with {len(graph)} triples")
            return graph

        except Exception as e:
            logger.error(f"Failed to convert regulatory data: {e}")
            raise

    def convert_custom_data(self, data: dict[str, Any],
                           ontology_uri: str,
                           class_mapping: dict[str, str] | None = None) -> Graph:
        """
        Convert custom data structure to RDF using ontology mapping.

        Args:
            data: Custom data dictionary
            ontology_uri: Base URI for the ontology
            class_mapping: Optional mapping of data keys to ontology classes

        Returns:
            RDF graph representation of custom data
        """
        graph = Graph()
        self._bind_namespaces(graph)

        ontology_ns = Namespace(ontology_uri)
        graph.bind("onto", ontology_ns)

        try:
            # Create main entity
            entity_uri = URIRef(f"{ontology_uri}#entity_{hash(str(data))}")

            # Determine class
            entity_class = ontology_ns.Entity
            if class_mapping and "type" in data:
                class_name = class_mapping.get(data["type"], "Entity")
                entity_class = ontology_ns[class_name]

            graph.add((entity_uri, RDF.type, entity_class))

            # Add properties
            for key, value in data.items():
                if key == "type":
                    continue

                prop_uri = ontology_ns[key]
                self._add_property(graph, entity_uri, prop_uri, value)

            logger.debug(f"Converted custom data to RDF graph with {len(graph)} triples")
            return graph

        except Exception as e:
            logger.error(f"Failed to convert custom data: {e}")
            raise

    def _convert_gs1_product(self, graph: Graph, data: dict[str, Any]):
        """Convert GS1 product data to RDF."""
        product_uri = URIRef(f"{GS1}product/{data.get('gtin', 'unknown')}")

        graph.add((product_uri, RDF.type, GS1.Product))

        # Basic product properties
        self._add_property(graph, product_uri, GS1.gtin, data.get("gtin"))
        self._add_property(graph, product_uri, GS1.brandName, data.get("brand"))
        self._add_property(graph, product_uri, GS1.productName, data.get("name"))
        self._add_property(graph, product_uri, GS1.description, data.get("description"))

        # Additional GS1 properties
        if "category" in data:
            graph.add((product_uri, GS1.categoryCode, Literal(data["category"])))
        if "manufacturer" in data:
            manufacturer_uri = URIRef(f"{GS1}party/{data['manufacturer']}")
            graph.add((product_uri, GS1.manufacturer, manufacturer_uri))

    def _convert_gs1_location(self, graph: Graph, data: dict[str, Any]):
        """Convert GS1 location data to RDF."""
        location_uri = URIRef(f"{GS1}location/{data.get('gln', 'unknown')}")

        graph.add((location_uri, RDF.type, GS1.Location))

        # Basic location properties
        self._add_property(graph, location_uri, GS1.gln, data.get("gln"))
        self._add_property(graph, location_uri, GS1.locationName, data.get("name"))
        self._add_property(graph, location_uri, GS1.address, data.get("address"))

        # Geographic coordinates
        if "latitude" in data and "longitude" in data:
            geo_uri = BNode()
            graph.add((location_uri, GS1.geo, geo_uri))
            graph.add((geo_uri, RDF.type, GS1.GeoCoordinates))
            graph.add((geo_uri, GS1.latitude, Literal(data["latitude"], datatype=XSD.decimal)))
            graph.add((geo_uri, GS1.longitude, Literal(data["longitude"], datatype=XSD.decimal)))

    def _convert_gs1_asset(self, graph: Graph, data: dict[str, Any]):
        """Convert GS1 asset data to RDF."""
        asset_uri = URIRef(f"{GS1}asset/{data.get('grai', 'unknown')}")

        graph.add((asset_uri, RDF.type, GS1.Asset))

        # Basic asset properties
        self._add_property(graph, asset_uri, GS1.grai, data.get("grai"))
        self._add_property(graph, asset_uri, GS1.assetName, data.get("name"))
        self._add_property(graph, asset_uri, GS1.assetType, data.get("type"))

    def _convert_gs1_event(self, graph: Graph, data: dict[str, Any]):
        """Convert GS1 event data to RDF."""
        event_uri = URIRef(f"{GS1}event/{data.get('eventID', 'unknown')}")

        graph.add((event_uri, RDF.type, GS1.Event))

        # Basic event properties
        self._add_property(graph, event_uri, GS1.eventID, data.get("eventID"))
        self._add_property(graph, event_uri, GS1.eventType, data.get("eventType"))

        # Event time
        if "eventTime" in data:
            graph.add((event_uri, GS1.eventTime,
                      Literal(data["eventTime"], datatype=XSD.dateTime)))

        # Related objects
        if "epcList" in data:
            for epc in data["epcList"]:
                graph.add((event_uri, GS1.epc, Literal(epc)))

    def _convert_esg_csrd(self, graph: Graph, data: dict[str, Any]):
        """Convert CSRD ESG data to RDF."""
        company_uri = URIRef(f"{ESG}company/{data.get('lei', 'unknown')}")

        graph.add((company_uri, RDF.type, ESG.Company))

        # Basic company properties
        self._add_property(graph, company_uri, ESG.lei, data.get("lei"))
        self._add_property(graph, company_uri, ESG.companyName, data.get("name"))

        # ESG metrics
        if "environmental" in data:
            env_data = data["environmental"]
            for key, value in env_data.items():
                self._add_property(graph, company_uri, ESG[f"environmental_{key}"], value)

        if "social" in data:
            social_data = data["social"]
            for key, value in social_data.items():
                self._add_property(graph, company_uri, ESG[f"social_{key}"], value)

        if "governance" in data:
            gov_data = data["governance"]
            for key, value in gov_data.items():
                self._add_property(graph, company_uri, ESG[f"governance_{key}"], value)

    def _convert_esg_sfdr(self, graph: Graph, data: dict[str, Any]):
        """Convert SFDR ESG data to RDF."""
        entity_uri = URIRef(f"{ESG}entity/{data.get('lei', 'unknown')}")

        graph.add((entity_uri, RDF.type, ESG.FinancialEntity))

        # SFDR specific properties
        self._add_property(graph, entity_uri, ESG.lei, data.get("lei"))
        self._add_property(graph, entity_uri, ESG.entityName, data.get("name"))
        self._add_property(graph, entity_uri, ESG.sfdrArticle, data.get("article"))

        # PAI metrics
        if "pai" in data:
            pai_data = data["pai"]
            for key, value in pai_data.items():
                self._add_property(graph, entity_uri, ESG[f"pai_{key}"], value)

    def _convert_esg_tcfd(self, graph: Graph, data: dict[str, Any]):
        """Convert TCFD ESG data to RDF."""
        organization_uri = URIRef(f"{ESG}organization/{data.get('lei', 'unknown')}")

        graph.add((organization_uri, RDF.type, ESG.Organization))

        # TCFD specific properties
        self._add_property(graph, organization_uri, ESG.lei, data.get("lei"))
        self._add_property(graph, organization_uri, ESG.organizationName, data.get("name"))

        # Climate-related metrics
        if "climate" in data:
            climate_data = data["climate"]
            for key, value in climate_data.items():
                self._add_property(graph, organization_uri, ESG[f"climate_{key}"], value)

    def _convert_regulatory_eudr(self, graph: Graph, data: dict[str, Any]):
        """Convert EUDR regulatory data to RDF."""
        operator_uri = URIRef(f"{REG}eudr/operator/{data.get('operator_id', 'unknown')}")

        graph.add((operator_uri, RDF.type, REG.EUDROperator))

        # EUDR specific properties
        self._add_property(graph, operator_uri, REG.operatorId, data.get("operator_id"))
        self._add_property(graph, operator_uri, REG.operatorName, data.get("name"))
        self._add_property(graph, operator_uri, REG.country, data.get("country"))

        # Due diligence data
        if "due_diligence" in data:
            dd_data = data["due_diligence"]
            for key, value in dd_data.items():
                self._add_property(graph, operator_uri, REG[f"dueDiligence_{key}"], value)

    def _convert_regulatory_csrd(self, graph: Graph, data: dict[str, Any]):
        """Convert CSRD regulatory data to RDF."""
        entity_uri = URIRef(f"{REG}csrd/entity/{data.get('lei', 'unknown')}")

        graph.add((entity_uri, RDF.type, REG.CSRDEntity))

        # CSRD specific properties
        self._add_property(graph, entity_uri, REG.lei, data.get("lei"))
        self._add_property(graph, entity_uri, REG.entityName, data.get("name"))
        self._add_property(graph, entity_uri, REG.sector, data.get("sector"))

        # Reporting data
        if "reporting" in data:
            reporting_data = data["reporting"]
            for key, value in reporting_data.items():
                self._add_property(graph, entity_uri, REG[f"reporting_{key}"], value)

    def _convert_regulatory_gdpr(self, graph: Graph, data: dict[str, Any]):
        """Convert GDPR regulatory data to RDF."""
        controller_uri = URIRef(f"{REG}gdpr/controller/{data.get('controller_id', 'unknown')}")

        graph.add((controller_uri, RDF.type, REG.GDPRController))

        # GDPR specific properties
        self._add_property(graph, controller_uri, REG.controllerId, data.get("controller_id"))
        self._add_property(graph, controller_uri, REG.controllerName, data.get("name"))

        # Processing activities
        if "processing_activities" in data:
            for activity in data["processing_activities"]:
                activity_uri = BNode()
                graph.add((controller_uri, REG.processingActivity, activity_uri))
                graph.add((activity_uri, RDF.type, REG.ProcessingActivity))
                for key, value in activity.items():
                    self._add_property(graph, activity_uri, REG[key], value)

    def _add_property(self, graph: Graph, subject: URIRef, predicate: URIRef, value: Any):
        """Add a property to the RDF graph with appropriate typing."""
        if value is None:
            return

        if isinstance(value, str):
            graph.add((subject, predicate, Literal(value, datatype=XSD.string)))
        elif isinstance(value, int):
            graph.add((subject, predicate, Literal(value, datatype=XSD.integer)))
        elif isinstance(value, float):
            graph.add((subject, predicate, Literal(value, datatype=XSD.decimal)))
        elif isinstance(value, bool):
            graph.add((subject, predicate, Literal(value, datatype=XSD.boolean)))
        elif isinstance(value, datetime):
            graph.add((subject, predicate, Literal(value.isoformat(), datatype=XSD.dateTime)))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    # Create blank node for complex objects
                    obj_uri = BNode()
                    graph.add((subject, predicate, obj_uri))
                    for k, v in item.items():
                        self._add_property(graph, obj_uri, URIRef(f"{predicate}/{k}"), v)
                else:
                    graph.add((subject, predicate, Literal(str(item))))
        elif isinstance(value, dict):
            # Create blank node for nested objects
            obj_uri = BNode()
            graph.add((subject, predicate, obj_uri))
            for k, v in value.items():
                self._add_property(graph, obj_uri, URIRef(f"{predicate}/{k}"), v)
        else:
            graph.add((subject, predicate, Literal(str(value))))

    def _bind_namespaces(self, graph: Graph):
        """Bind common namespaces to the graph."""
        for prefix, namespace in self.namespaces.items():
            graph.bind(prefix, namespace)
