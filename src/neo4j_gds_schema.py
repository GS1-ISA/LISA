"""
Neo4j Graph Schema for GS1/EPCIS Supply Chain Analytics

This module defines the graph data model for modeling supply chain data
from GS1/EPCIS events in Neo4j, optimized for Graph Data Science (GDS) algorithms.

Graph Schema Design:
===================

Nodes:
------
- Product: Represents physical/digital products identified by EPC
- Location: Physical or logical locations in the supply chain
- Organization: Business partners, suppliers, manufacturers, distributors
- Event: EPCIS events (Object, Aggregation, Transformation)
- Document: EPCIS documents containing events
- BusinessTransaction: Commercial transactions

Relationships:
-------------
- LOCATED_AT: Product/Event -> Location (where product is/was)
- SUPPLIES_TO: Organization -> Organization (supply chain relationships)
- CONTAINS: AggregationEvent -> Product (parent-child relationships)
- TRANSFORMS_INTO: Product -> Product (transformation relationships)
- PARTICIPATES_IN: Product -> Event (product involvement in events)
- ISSUED_BY: Event -> Organization (event issuer)
- RECORDED_IN: Event -> Document (event containment)
- LINKED_TO: Event -> BusinessTransaction (business context)

Node Properties:
---------------
Product:
- epc: String (primary key)
- gtin: String (GS1 GTIN)
- lot_number: String
- serial_number: String
- product_class: String
- description: String
- category: String
- created_at: DateTime
- last_updated: DateTime

Location:
- id: String (primary key, GS1 GLN or custom)
- name: String
- address: String
- latitude: Float
- longitude: Float
- location_type: String (warehouse, factory, store, etc.)
- country: String
- region: String

Organization:
- id: String (primary key, GS1 GLN)
- name: String
- type: String (supplier, manufacturer, distributor, retailer)
- industry: String
- risk_score: Float (calculated)
- compliance_status: String

Event:
- event_id: String (primary key)
- event_type: String (ObjectEvent, AggregationEvent, TransformationEvent)
- action: String (ADD, OBSERVE, DELETE)
- biz_step: String
- disposition: String
- event_time: DateTime
- event_timezone_offset: String
- record_time: DateTime

Document:
- id: String (primary key)
- schema_version: String
- creation_date: DateTime
- event_count: Integer

BusinessTransaction:
- id: String (primary key)
- type: String
- transaction_id: String
- amount: Float (optional)
- currency: String (optional)

Relationship Properties:
----------------------
LOCATED_AT:
- start_time: DateTime
- end_time: DateTime
- confidence: Float

SUPPLIES_TO:
- contract_start: DateTime
- contract_end: DateTime
- volume: Float
- frequency: String
- criticality: Float (0-1, importance of relationship)

CONTAINS:
- quantity: Integer
- containment_type: String (physical, logical)

TRANSFORMS_INTO:
- transformation_ratio: Float
- yield_percentage: Float
- transformation_type: String

PARTICIPATES_IN:
- role: String (input, output, parent, child)
- quantity: Integer

ISSUED_BY:
- verification_status: String
- issuer_role: String

RECORDED_IN:
- sequence_number: Integer

LINKED_TO:
- transaction_role: String
- transaction_amount: Float

GDS-Optimized Schema Features:
=============================

1. Temporal Properties: All time-based relationships have start/end times
2. Weighted Relationships: Criticality, confidence, volume scores for algorithms
3. Hierarchical Structure: Product containment and transformation chains
4. Risk Propagation: Organization risk scores and relationship criticality
5. Path Analysis: Supply chain flow through SUPPLIES_TO and LOCATED_AT relationships
6. Centrality Analysis: Key suppliers, bottlenecks, single points of failure
7. Community Detection: Supply chain clusters and risk correlation groups
8. Similarity Analysis: Product similarity for substitution and risk assessment

Graph Algorithms for Risk Analysis:
==================================

1. Centrality Analysis:
   - Betweenness Centrality: Identify critical suppliers/nodes
   - Degree Centrality: Most connected organizations
   - PageRank: Influence in supply chain network

2. Path Finding:
   - Shortest Path: Direct supply chain routes
   - All Paths: Alternative supply routes
   - k-Shortest Paths: Multiple routing options

3. Community Detection:
   - Louvain: Supply chain clusters
   - Label Propagation: Risk propagation groups

4. Similarity Analysis:
   - Node Similarity: Similar products/suppliers
   - Cosine Similarity: Risk profile similarity

5. Link Prediction:
   - Predict potential supply chain disruptions
   - Identify hidden dependencies

6. Graph Embeddings:
   - Node2Vec: Vector representations for ML models
   - GraphSAGE: Inductive learning for new nodes
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NodeType(Enum):
    """Graph node types for supply chain modeling."""
    PRODUCT = "Product"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    EVENT = "Event"
    DOCUMENT = "Document"
    BUSINESS_TRANSACTION = "BusinessTransaction"


class RelationshipType(Enum):
    """Graph relationship types for supply chain connections."""
    LOCATED_AT = "LOCATED_AT"
    SUPPLIES_TO = "SUPPLIES_TO"
    CONTAINS = "CONTAINS"
    TRANSFORMS_INTO = "TRANSFORMS_INTO"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    ISSUED_BY = "ISSUED_BY"
    RECORDED_IN = "RECORDED_IN"
    LINKED_TO = "LINKED_TO"


@dataclass
class GraphNode:
    """Base class for graph nodes."""
    node_type: NodeType
    properties: Dict[str, Any]

    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this node."""
        labels = f":{self.node_type.value}"
        props = ", ".join([f"{k}: ${k}" for k in self.properties.keys()])
        return f"CREATE (n{labels} {{ {props} }})"


@dataclass
class GraphRelationship:
    """Graph relationship with properties."""
    relationship_type: RelationshipType
    from_node: GraphNode
    to_node: GraphNode
    properties: Dict[str, Any]

    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this relationship."""
        rel_type = self.relationship_type.value
        props = ""
        if self.properties:
            props = " {" + ", ".join([f"{k}: ${k}" for k in self.properties.keys()]) + "}"

        return f"CREATE (from)-[:{rel_type}{props}]->(to)"


class SupplyChainGraphSchema:
    """Neo4j graph schema definition for supply chain analytics."""

    @staticmethod
    def get_node_constraints() -> List[str]:
        """Get Cypher statements for node constraints."""
        return [
            "CREATE CONSTRAINT product_epc IF NOT EXISTS FOR (p:Product) REQUIRE p.epc IS UNIQUE",
            "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE",
            "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (bt:BusinessTransaction) REQUIRE bt.id IS UNIQUE"
        ]

    @staticmethod
    def get_indexes() -> List[str]:
        """Get Cypher statements for indexes."""
        return [
            "CREATE INDEX product_gtin IF NOT EXISTS FOR (p:Product) ON (p.gtin)",
            "CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category)",
            "CREATE INDEX location_country IF NOT EXISTS FOR (l:Location) ON (l.country)",
            "CREATE INDEX organization_type IF NOT EXISTS FOR (o:Organization) ON (o.type)",
            "CREATE INDEX event_type IF NOT EXISTS FOR (e:Event) ON (e.event_type)",
            "CREATE INDEX event_time IF NOT EXISTS FOR (e:Event) ON (e.event_time)"
        ]

    @staticmethod
    def get_schema_initialization() -> List[str]:
        """Get all Cypher statements for schema initialization."""
        statements = []
        statements.extend(SupplyChainGraphSchema.get_node_constraints())
        statements.extend(SupplyChainGraphSchema.get_indexes())
        return statements

    @staticmethod
    def create_product_node(epc: str, gtin: str = None, **properties) -> GraphNode:
        """Create a Product node."""
        node_props = {
            "epc": epc,
            "gtin": gtin,
            "created_at": datetime.now().isoformat(),
            **properties
        }
        return GraphNode(NodeType.PRODUCT, node_props)

    @staticmethod
    def create_location_node(location_id: str, name: str, **properties) -> GraphNode:
        """Create a Location node."""
        node_props = {
            "id": location_id,
            "name": name,
            **properties
        }
        return GraphNode(NodeType.LOCATION, node_props)

    @staticmethod
    def create_organization_node(org_id: str, name: str, org_type: str, **properties) -> GraphNode:
        """Create an Organization node."""
        node_props = {
            "id": org_id,
            "name": name,
            "type": org_type,
            **properties
        }
        return GraphNode(NodeType.ORGANIZATION, node_props)

    @staticmethod
    def create_event_node(event_id: str, event_type: str, **properties) -> GraphNode:
        """Create an Event node."""
        node_props = {
            "event_id": event_id,
            "event_type": event_type,
            **properties
        }
        return GraphNode(NodeType.EVENT, node_props)

    @staticmethod
    def create_supply_chain_relationship(from_node: GraphNode, to_node: GraphNode,
                                       criticality: float = 0.5, **properties) -> GraphRelationship:
        """Create a SUPPLIES_TO relationship."""
        rel_props = {
            "criticality": criticality,
            **properties
        }
        return GraphRelationship(RelationshipType.SUPPLIES_TO, from_node, to_node, rel_props)

    @staticmethod
    def create_location_relationship(product_node: GraphNode, location_node: GraphNode,
                                   start_time: datetime, **properties) -> GraphRelationship:
        """Create a LOCATED_AT relationship."""
        rel_props = {
            "start_time": start_time.isoformat(),
            **properties
        }
        return GraphRelationship(RelationshipType.LOCATED_AT, product_node, location_node, rel_props)

    @staticmethod
    def create_containment_relationship(parent_node: GraphNode, child_node: GraphNode,
                                      quantity: int = 1, **properties) -> GraphRelationship:
        """Create a CONTAINS relationship."""
        rel_props = {
            "quantity": quantity,
            **properties
        }
        return GraphRelationship(RelationshipType.CONTAINS, parent_node, child_node, rel_props)

    @staticmethod
    def create_transformation_relationship(input_node: GraphNode, output_node: GraphNode,
                                        transformation_ratio: float = 1.0, **properties) -> GraphRelationship:
        """Create a TRANSFORMS_INTO relationship."""
        rel_props = {
            "transformation_ratio": transformation_ratio,
            **properties
        }
        return GraphRelationship(RelationshipType.TRANSFORMS_INTO, input_node, output_node, rel_props)


# GDS Algorithm Configurations
GDS_ALGORITHMS = {
    "centrality": {
        "betweenness": {
            "query": """
            CALL gds.betweenness.stream('supply-chain-graph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC
            """,
            "description": "Identify critical nodes in supply chain"
        },
        "pagerank": {
            "query": """
            CALL gds.pageRank.stream('supply-chain-graph', {
                maxIterations: 20,
                dampingFactor: 0.85
            })
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS name, score
            ORDER BY score DESC
            """,
            "description": "Measure influence in supply chain network"
        }
    },
    "community": {
        "louvain": {
            "query": """
            CALL gds.louvain.stream('supply-chain-graph')
            YIELD nodeId, communityId, intermediateCommunityIds
            RETURN gds.util.asNode(nodeId).name AS name, communityId
            ORDER BY communityId
            """,
            "description": "Detect supply chain clusters"
        }
    },
    "pathfinding": {
        "shortest_path": {
            "query": """
            MATCH (source:Organization {name: $source_name})
            MATCH (target:Organization {name: $target_name})
            CALL gds.shortestPath.dijkstra.stream('supply-chain-graph', {
                sourceNode: source,
                targetNode: target,
                relationshipWeightProperty: 'criticality'
            })
            YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
            RETURN
                index,
                gds.util.asNode(sourceNode).name AS sourceNodeName,
                gds.util.asNode(targetNode).name AS targetNodeName,
                totalCost,
                [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
                costs,
                nodes(path) as path
            """,
            "description": "Find shortest supply chain paths"
        }
    },
    "similarity": {
        "node_similarity": {
            "query": """
            CALL gds.nodeSimilarity.stream('supply-chain-graph')
            YIELD node1, node2, similarity
            RETURN gds.util.asNode(node1).name AS node1, gds.util.asNode(node2).name AS node2, similarity
            ORDER BY similarity DESC
            """,
            "description": "Find similar nodes in supply chain"
        }
    }
}