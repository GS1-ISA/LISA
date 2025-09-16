"""
SHACL schemas for GS1 standards validation.

This module contains SHACL shape definitions for validating GS1 data
including products, locations, assets, and events.
"""

import logging
from typing import Dict, Any, Optional

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, XSD

logger = logging.getLogger(__name__)

# GS1 namespace
GS1 = URIRef("https://www.gs1.org/voc/")
SH = Namespace("http://www.w3.org/ns/shacl#")


class GS1Schemas:
    """
    SHACL schemas for GS1 standards validation.

    Provides validation shapes for:
    - GS1 Product data
    - GS1 Location data
    - GS1 Asset data
    - GS1 Event data
    """

    def __init__(self):
        self._schemas = {}
        self._load_schemas()

    def get_schema(self, schema_type: str) -> Graph:
        """
        Get SHACL schema for the specified GS1 data type.

        Args:
            schema_type: Type of GS1 schema (product, location, asset, event)

        Returns:
            RDF graph containing SHACL shapes
        """
        if schema_type not in self._schemas:
            raise ValueError(f"Unknown GS1 schema type: {schema_type}")

        return self._schemas[schema_type]

    def _load_schemas(self):
        """Load all GS1 SHACL schemas."""
        self._schemas['product'] = self._create_product_schema()
        self._schemas['location'] = self._create_location_schema()
        self._schemas['asset'] = self._create_asset_schema()
        self._schemas['event'] = self._create_event_schema()

        logger.info("Loaded GS1 SHACL schemas")

    def _create_product_schema(self) -> Graph:
        """Create SHACL schema for GS1 Product validation."""
        g = Graph()
        g.bind("gs1", GS1)
        g.bind("sh", SH)

        # Product shape
        product_shape = URIRef(f"{GS1}ProductShape")

        g.add((product_shape, RDF.type, SH.NodeShape))
        g.add((product_shape, SH.targetClass, URIRef(f"{GS1}Product")))

        # GTIN property constraint
        gtin_prop = BNode()
        g.add((product_shape, SH.property, gtin_prop))
        g.add((gtin_prop, SH.path, URIRef(f"{GS1}gtin")))
        g.add((gtin_prop, SH.minCount, Literal(1)))
        g.add((gtin_prop, SH.maxCount, Literal(1)))
        g.add((gtin_prop, SH.datatype, XSD.string))
        g.add((gtin_prop, SH.pattern, Literal(r"^\d{8}|\d{12}|\d{13}|\d{14}$")))  # GTIN format

        # Product name constraint
        name_prop = BNode()
        g.add((product_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{GS1}productName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Brand name constraint (optional)
        brand_prop = BNode()
        g.add((product_shape, SH.property, brand_prop))
        g.add((brand_prop, SH.path, URIRef(f"{GS1}brandName")))
        g.add((brand_prop, SH.datatype, XSD.string))

        return g

    def _create_location_schema(self) -> Graph:
        """Create SHACL schema for GS1 Location validation."""
        g = Graph()
        g.bind("gs1", GS1)
        g.bind("sh", SH)

        # Location shape
        location_shape = URIRef(f"{GS1}LocationShape")

        g.add((location_shape, RDF.type, SH.NodeShape))
        g.add((location_shape, SH.targetClass, URIRef(f"{GS1}Location")))

        # GLN property constraint
        gln_prop = BNode()
        g.add((location_shape, SH.property, gln_prop))
        g.add((gln_prop, SH.path, URIRef(f"{GS1}gln")))
        g.add((gln_prop, SH.minCount, Literal(1)))
        g.add((gln_prop, SH.maxCount, Literal(1)))
        g.add((gln_prop, SH.datatype, XSD.string))
        g.add((gln_prop, SH.pattern, Literal(r"^\d{13}$")))  # GLN format

        # Location name constraint
        name_prop = BNode()
        g.add((location_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{GS1}locationName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Geographic coordinates constraint
        geo_prop = BNode()
        g.add((location_shape, SH.property, geo_prop))
        g.add((geo_prop, SH.path, URIRef(f"{GS1}geo")))
        g.add((geo_prop, SH.node, URIRef(f"{GS1}GeoCoordinatesShape")))

        # Geo coordinates shape
        geo_shape = URIRef(f"{GS1}GeoCoordinatesShape")
        g.add((geo_shape, RDF.type, SH.NodeShape))

        lat_prop = BNode()
        g.add((geo_shape, SH.property, lat_prop))
        g.add((lat_prop, SH.path, URIRef(f"{GS1}latitude")))
        g.add((lat_prop, SH.datatype, XSD.decimal))
        g.add((lat_prop, SH.minInclusive, Literal(-90)))
        g.add((lat_prop, SH.maxInclusive, Literal(90)))

        lon_prop = BNode()
        g.add((geo_shape, SH.property, lon_prop))
        g.add((lon_prop, SH.path, URIRef(f"{GS1}longitude")))
        g.add((lon_prop, SH.datatype, XSD.decimal))
        g.add((lon_prop, SH.minInclusive, Literal(-180)))
        g.add((lon_prop, SH.maxInclusive, Literal(180)))

        return g

    def _create_asset_schema(self) -> Graph:
        """Create SHACL schema for GS1 Asset validation."""
        g = Graph()
        g.bind("gs1", GS1)
        g.bind("sh", SH)

        # Asset shape
        asset_shape = URIRef(f"{GS1}AssetShape")

        g.add((asset_shape, RDF.type, SH.NodeShape))
        g.add((asset_shape, SH.targetClass, URIRef(f"{GS1}Asset")))

        # GRAI property constraint
        grai_prop = BNode()
        g.add((asset_shape, SH.property, grai_prop))
        g.add((grai_prop, SH.path, URIRef(f"{GS1}grai")))
        g.add((grai_prop, SH.minCount, Literal(1)))
        g.add((grai_prop, SH.maxCount, Literal(1)))
        g.add((grai_prop, SH.datatype, XSD.string))
        # GRAI format: (01)GTIN + (21)serial + (10)batch/lot + (17)expiry
        g.add((grai_prop, SH.pattern, Literal(r"^\d{14}\d{1,16}$")))

        # Asset name constraint
        name_prop = BNode()
        g.add((asset_shape, SH.property, name_prop))
        g.add((name_prop, SH.path, URIRef(f"{GS1}assetName")))
        g.add((name_prop, SH.minCount, Literal(1)))
        g.add((name_prop, SH.datatype, XSD.string))

        # Asset type constraint
        type_prop = BNode()
        g.add((asset_shape, SH.property, type_prop))
        g.add((type_prop, SH.path, URIRef(f"{GS1}assetType")))
        g.add((type_prop, SH.datatype, XSD.string))

        return g

    def _create_event_schema(self) -> Graph:
        """Create SHACL schema for GS1 Event validation."""
        g = Graph()
        g.bind("gs1", GS1)
        g.bind("sh", SH)

        # Event shape
        event_shape = URIRef(f"{GS1}EventShape")

        g.add((event_shape, RDF.type, SH.NodeShape))
        g.add((event_shape, SH.targetClass, URIRef(f"{GS1}Event")))

        # Event ID constraint
        event_id_prop = BNode()
        g.add((event_shape, SH.property, event_id_prop))
        g.add((event_id_prop, SH.path, URIRef(f"{GS1}eventID")))
        g.add((event_id_prop, SH.minCount, Literal(1)))
        g.add((event_id_prop, SH.maxCount, Literal(1)))
        g.add((event_id_prop, SH.datatype, XSD.string))

        # Event type constraint
        event_type_prop = BNode()
        g.add((event_shape, SH.property, event_type_prop))
        g.add((event_type_prop, SH.path, URIRef(f"{GS1}eventType")))
        g.add((event_type_prop, SH.minCount, Literal(1)))
        g.add((event_type_prop, SH.datatype, XSD.string))

        # Event time constraint
        event_time_prop = BNode()
        g.add((event_shape, SH.property, event_time_prop))
        g.add((event_time_prop, SH.path, URIRef(f"{GS1}eventTime")))
        g.add((event_time_prop, SH.minCount, Literal(1)))
        g.add((event_time_prop, SH.datatype, XSD.dateTime))

        # EPC list constraint (for Object Events)
        epc_prop = BNode()
        g.add((event_shape, SH.property, epc_prop))
        g.add((epc_prop, SH.path, URIRef(f"{GS1}epc")))
        g.add((epc_prop, SH.datatype, XSD.string))

        return g