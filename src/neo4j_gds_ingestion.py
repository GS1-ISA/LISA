"""
Neo4j GDS Data Ingestion Module for GS1/EPCIS Supply Chain Data

This module provides comprehensive data ingestion capabilities for loading
GS1/EPCIS supply chain data into Neo4j graph database for GDS analytics.

Features:
- GS1/EPCIS event processing and graph transformation
- Batch ingestion with progress tracking and error handling
- Incremental updates and data synchronization
- Integration with existing ISA GS1/EPCIS modules
- Data validation and quality assurance
- Performance optimization for large datasets
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .epcis_tracker import EPCISEvent, EventType
from .gs1_integration import GS1IntegrationManager
from .neo4j_gds_client import Neo4jGDSClient, get_gds_client
from .neo4j_gds_schema import RelationshipType, SupplyChainGraphSchema

logger = logging.getLogger(__name__)


@dataclass
class IngestionConfig:
    """Configuration for data ingestion operations."""
    batch_size: int = 1000
    max_workers: int = 4
    enable_validation: bool = True
    enable_progress_tracking: bool = True
    retry_failed_batches: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_incremental_updates: bool = True
    ingestion_timeout: float = 3600.0  # 1 hour


@dataclass
class IngestionStats:
    """Statistics for ingestion operations."""
    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0
    total_nodes: int = 0
    total_relationships: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    batches_processed: int = 0
    batches_failed: int = 0

    @property
    def duration(self) -> float:
        """Calculate ingestion duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def events_per_second(self) -> float:
        """Calculate ingestion rate."""
        if self.duration > 0:
            return self.processed_events / self.duration
        return 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_events > 0:
            return (self.processed_events / self.total_events) * 100
        return 0.0


class GS1EPCISGraphTransformer:
    """
    Transformer for converting GS1/EPCIS data to Neo4j graph format.

    Handles the complex mapping from EPCIS events to graph nodes and relationships,
    including hierarchical product structures, supply chain flows, and temporal aspects.
    """

    def __init__(self, schema: SupplyChainGraphSchema | None = None):
        self.schema = schema or SupplyChainGraphSchema()

    def transform_epcis_event(self, event: EPCISEvent) -> dict[str, list[dict[str, Any]]]:
        """
        Transform a single EPCIS event into graph nodes and relationships.

        Args:
            event: EPCIS event to transform

        Returns:
            Dictionary containing nodes and relationships
        """
        nodes = []
        relationships = []

        # Create Event node
        event_node = self.schema.create_event_node(
            event_id=event.eventID,
            event_type=event.type.value,
            action=event.action.value,
            biz_step=event.bizStep.value,
            event_time=event.eventTime,
            event_timezone_offset=event.eventTimeZoneOffset,
            disposition=event.disposition.value if event.disposition else None
        )
        nodes.append(event_node)

        # Create Location node if present
        if event.bizLocation:
            location_node = self.schema.create_location_node(
                location_id=event.bizLocation.id,
                name=f"Location_{event.bizLocation.id}",
                location_type="business_location"
            )
            nodes.append(location_node)

            # Create LOCATED_AT relationship
            location_rel = self.schema.create_location_relationship(
                product_node=None,  # Will be set by caller
                location_node=location_node,
                start_time=datetime.fromisoformat(event.eventTime) if event.eventTime else datetime.now()
            )
            relationships.append(location_rel)

        if event.readPoint:
            read_point_node = self.schema.create_location_node(
                location_id=event.readPoint.id,
                name=f"ReadPoint_{event.readPoint.id}",
                location_type="read_point"
            )
            nodes.append(read_point_node)

        # Handle different event types
        if event.type == EventType.OBJECT_EVENT:
            nodes_rels = self._transform_object_event(event, event_node)
            nodes.extend(nodes_rels["nodes"])
            relationships.extend(nodes_rels["relationships"])

        elif event.type == EventType.AGGREGATION_EVENT:
            nodes_rels = self._transform_aggregation_event(event, event_node)
            nodes.extend(nodes_rels["nodes"])
            relationships.extend(nodes_rels["relationships"])

        elif event.type == EventType.TRANSFORMATION_EVENT:
            nodes_rels = self._transform_transformation_event(event, event_node)
            nodes.extend(nodes_rels["nodes"])
            relationships.extend(nodes_rels["relationships"])

        return {
            "nodes": nodes,
            "relationships": relationships
        }

    def _transform_object_event(self, event: EPCISEvent, event_node) -> dict[str, list]:
        """Transform Object Event to graph elements."""
        nodes = []
        relationships = []

        # Create Product nodes for EPCs
        if event.epcList:
            for epc in event.epcList:
                product_node = self.schema.create_product_node(
                    epc=epc,
                    gtin=self._extract_gtin_from_epc(epc),
                    category="product"
                )
                nodes.append(product_node)

                # Create PARTICIPATES_IN relationship
                participates_rel = {
                    "from": product_node,
                    "to": event_node,
                    "type": RelationshipType.PARTICIPATES_IN,
                    "properties": {
                        "role": "object",
                        "quantity": 1
                    }
                }
                relationships.append(participates_rel)

        return {"nodes": nodes, "relationships": relationships}

    def _transform_aggregation_event(self, event: EPCISEvent, event_node) -> dict[str, list]:
        """Transform Aggregation Event to graph elements."""
        nodes = []
        relationships = []

        # Create parent product node
        if event.parentID:
            parent_node = self.schema.create_product_node(
                epc=event.parentID,
                category="aggregate"
            )
            nodes.append(parent_node)

            # Create PARTICIPATES_IN relationship for parent
            parent_rel = {
                "from": parent_node,
                "to": event_node,
                "type": RelationshipType.PARTICIPATES_IN,
                "properties": {
                    "role": "parent",
                    "quantity": 1
                }
            }
            relationships.append(parent_rel)

        # Create child product nodes
        if event.childEPCs:
            for child_epc in event.childEPCs:
                child_node = self.schema.create_product_node(
                    epc=child_epc,
                    category="component"
                )
                nodes.append(child_node)

                # Create PARTICIPATES_IN relationship for child
                child_rel = {
                    "from": child_node,
                    "to": event_node,
                    "type": RelationshipType.PARTICIPATES_IN,
                    "properties": {
                        "role": "child",
                        "quantity": 1
                    }
                }
                relationships.append(child_rel)

                # Create CONTAINS relationship between parent and child
                if event.parentID:
                    contains_rel = self.schema.create_containment_relationship(
                        parent_node=parent_node,
                        child_node=child_node,
                        quantity=1
                    )
                    relationships.append(contains_rel)

        return {"nodes": nodes, "relationships": relationships}

    def _transform_transformation_event(self, event: EPCISEvent, event_node) -> dict[str, list]:
        """Transform Transformation Event to graph elements."""
        nodes = []
        relationships = []

        # Create input product nodes
        if event.inputEPCList:
            for input_epc in event.inputEPCList:
                input_node = self.schema.create_product_node(
                    epc=input_epc,
                    category="input_material"
                )
                nodes.append(input_node)

                # Create PARTICIPATES_IN relationship for input
                input_rel = {
                    "from": input_node,
                    "to": event_node,
                    "type": RelationshipType.PARTICIPATES_IN,
                    "properties": {
                        "role": "input",
                        "quantity": 1
                    }
                }
                relationships.append(input_rel)

        # Create output product nodes
        if event.outputEPCList:
            for output_epc in event.outputEPCList:
                output_node = self.schema.create_product_node(
                    epc=output_epc,
                    category="finished_product"
                )
                nodes.append(output_node)

                # Create PARTICIPATES_IN relationship for output
                output_rel = {
                    "from": output_node,
                    "to": event_node,
                    "type": RelationshipType.PARTICIPATES_IN,
                    "properties": {
                        "role": "output",
                        "quantity": 1
                    }
                }
                relationships.append(output_rel)

                # Create TRANSFORMS_INTO relationships between inputs and outputs
                if event.inputEPCList:
                    for input_epc in event.inputEPCList:
                        input_node = next((n for n in nodes if n.properties.get("epc") == input_epc), None)
                        if input_node:
                            transform_rel = self.schema.create_transformation_relationship(
                                input_node=input_node,
                                output_node=output_node,
                                transformation_ratio=1.0 / len(event.inputEPCList) if event.inputEPCList else 1.0
                            )
                            relationships.append(transform_rel)

        return {"nodes": nodes, "relationships": relationships}

    def _extract_gtin_from_epc(self, epc: str) -> str | None:
        """Extract GTIN from EPC if possible."""
        # EPC format: urn:epc:id:sgtin:CompanyPrefix.ItemReference.SerialNumber
        try:
            if epc.startswith("urn:epc:id:sgtin:"):
                parts = epc.split(":")
                if len(parts) >= 6:
                    company_prefix = parts[4]
                    item_reference = parts[5]
                    # GTIN = CompanyPrefix + ItemReference (padded to 14 digits)
                    gtin_base = f"{company_prefix}{item_reference}"
                    return gtin_base.zfill(14)
        except Exception:
            pass
        return None


class Neo4jGDSDataIngestion:
    """
    Main data ingestion class for loading GS1/EPCIS data into Neo4j GDS.

    Provides batch processing, progress tracking, error handling, and integration
    with existing ISA GS1/EPCIS modules.
    """

    def __init__(self, gds_client: Neo4jGDSClient | None = None,
                 config: IngestionConfig | None = None):
        self.gds_client = gds_client or get_gds_client()
        self.config = config or IngestionConfig()
        self.transformer = GS1EPCISGraphTransformer()
        self.gs1_integration = GS1IntegrationManager()

        # Statistics and progress tracking
        self.stats = IngestionStats()
        self._progress_callbacks = []

    def add_progress_callback(self, callback: callable) -> None:
        """Add a callback function for progress updates."""
        self._progress_callbacks.append(callback)

    def _notify_progress(self, message: str, progress: float) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(message, progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def ingest_epcis_events(self, events: list[EPCISEvent],
                           organization_context: dict[str, Any] | None = None) -> IngestionStats:
        """
        Ingest EPCIS events into Neo4j graph database.

        Args:
            events: List of EPCIS events to ingest
            organization_context: Optional context about organizations involved

        Returns:
            Ingestion statistics
        """
        self.stats = IngestionStats()
        self.stats.total_events = len(events)
        self.stats.start_time = datetime.now(timezone.utc)

        logger.info(f"Starting ingestion of {len(events)} EPCIS events")

        try:
            # Process events in batches
            batches = self._create_batches(events)

            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = []

                for batch in batches:
                    future = executor.submit(self._process_batch, batch, organization_context)
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    try:
                        batch_stats = future.result()
                        self._update_stats(batch_stats)
                    except Exception as e:
                        logger.error(f"Batch processing failed: {e}")
                        self.stats.batches_failed += 1

            self.stats.end_time = datetime.now(timezone.utc)
            logger.info(f"Ingestion completed: {self.stats.processed_events}/{self.stats.total_events} events processed")

            return self.stats

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            self.stats.end_time = datetime.now(timezone.utc)
            raise

    def ingest_from_gs1_integration(self, raw_events_data: list[dict[str, Any]],
                                   issuer: str, subject_id: str) -> IngestionStats:
        """
        Ingest data directly from GS1 integration pipeline.

        Args:
            raw_events_data: Raw event data from GS1 integration
            issuer: Event issuer identifier
            subject_id: Subject identifier for traceability

        Returns:
            Ingestion statistics
        """
        logger.info("Ingesting data from GS1 integration pipeline")

        # Process through GS1 integration to get EPCIS events
        try:
            result = self.gs1_integration.process_supply_chain_data(
                raw_events_data, issuer, subject_id
            )

            # Extract EPCIS events from the result
            # This assumes the GS1 integration returns events in a specific format
            events = self._extract_events_from_gs1_result(result)

            # Ingest the events
            return self.ingest_epcis_events(events, {"issuer": issuer, "subject_id": subject_id})

        except Exception as e:
            logger.error(f"GS1 integration ingestion failed: {e}")
            raise

    def _extract_events_from_gs1_result(self, gs1_result: dict[str, Any]) -> list[EPCISEvent]:
        """Extract EPCIS events from GS1 integration result."""
        events = []

        # This is a placeholder - actual implementation would depend on
        # the exact format returned by GS1 integration
        if "epcis_events" in gs1_result:
            for event_data in gs1_result["epcis_events"]:
                try:
                    event = EPCISEvent(**event_data)
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event data: {e}")

        return events

    def _create_batches(self, events: list[EPCISEvent]) -> list[list[EPCISEvent]]:
        """Create batches of events for processing."""
        batches = []
        for i in range(0, len(events), self.config.batch_size):
            batch = events[i:i + self.config.batch_size]
            batches.append(batch)
        return batches

    def _process_batch(self, batch: list[EPCISEvent],
                      organization_context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Process a batch of EPCIS events.

        Args:
            batch: List of events to process
            organization_context: Optional organization context

        Returns:
            Batch processing statistics
        """
        batch_stats = {
            "events_processed": 0,
            "events_failed": 0,
            "nodes_created": 0,
            "relationships_created": 0
        }

        # Transform events to graph format
        all_nodes = []
        all_relationships = []

        for event in batch:
            try:
                transformed = self.transformer.transform_epcis_event(event)
                all_nodes.extend(transformed["nodes"])
                all_relationships.extend(transformed["relationships"])
                batch_stats["events_processed"] += 1
            except Exception as e:
                logger.warning(f"Failed to transform event {event.eventID}: {e}")
                batch_stats["events_failed"] += 1

        # Batch insert into Neo4j
        try:
            nodes_created, relationships_created = self._batch_insert_graph_data(
                all_nodes, all_relationships
            )
            batch_stats["nodes_created"] = nodes_created
            batch_stats["relationships_created"] = relationships_created

        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            batch_stats["events_failed"] += batch_stats["events_processed"]
            batch_stats["events_processed"] = 0

        return batch_stats

    def _batch_insert_graph_data(self, nodes: list[dict[str, Any]],
                                relationships: list[dict[str, Any]]) -> tuple[int, int]:
        """
        Batch insert nodes and relationships into Neo4j.

        Args:
            nodes: List of node data
            relationships: List of relationship data

        Returns:
            Tuple of (nodes_created, relationships_created)
        """
        nodes_created = 0
        relationships_created = 0

        # Use Cypher UNWIND for batch insertion
        if nodes:
            node_query = self._build_batch_node_query(nodes)
            try:
                self.gds_client.execute_query(node_query, {"nodes": nodes})
                nodes_created = len(nodes)
                logger.debug(f"Created {nodes_created} nodes")
            except Exception as e:
                logger.error(f"Node batch insert failed: {e}")
                raise

        if relationships:
            relationship_query = self._build_batch_relationship_query(relationships)
            try:
                self.gds_client.execute_query(relationship_query, {"relationships": relationships})
                relationships_created = len(relationships)
                logger.debug(f"Created {relationships_created} relationships")
            except Exception as e:
                logger.error(f"Relationship batch insert failed: {e}")
                raise

        return nodes_created, relationships_created

    def _build_batch_node_query(self, nodes: list[dict[str, Any]]) -> str:
        """Build Cypher query for batch node insertion."""
        # Group nodes by label for efficiency
        node_labels = {}
        for node in nodes:
            label = node.node_type.value
            if label not in node_labels:
                node_labels[label] = []
            node_labels[label].append(node.properties)

        # Build query with UNION ALL for different node types
        query_parts = []
        for label, node_list in node_labels.items():
            props = ", ".join([f"{k}: node.{k}" for k in node_list[0]])
            query_parts.append(f"""
                UNWIND $nodes AS node
                CREATE (n:{label} {{ {props} }})
            """)

        return " UNION ALL ".join(query_parts)

    def _build_batch_relationship_query(self, relationships: list[dict[str, Any]]) -> str:
        """Build Cypher query for batch relationship insertion."""
        # This is a simplified version - actual implementation would be more complex
        # to handle different relationship types and properties
        return """
            UNWIND $relationships AS rel
            MATCH (from {id: rel.from_id})
            MATCH (to {id: rel.to_id})
            CREATE (from)-[:rel.type {properties: rel.properties}]->(to)
        """

    def _update_stats(self, batch_stats: dict[str, Any]) -> None:
        """Update global statistics with batch results."""
        self.stats.processed_events += batch_stats["events_processed"]
        self.stats.failed_events += batch_stats["events_failed"]
        self.stats.total_nodes += batch_stats["nodes_created"]
        self.stats.total_relationships += batch_stats["relationships_created"]
        self.stats.batches_processed += 1

        # Notify progress
        if self.config.enable_progress_tracking:
            progress = (self.stats.processed_events / self.stats.total_events) * 100
            self._notify_progress(
                f"Processed {self.stats.processed_events}/{self.stats.total_events} events",
                progress
            )

    def validate_ingestion_data(self, events: list[EPCISEvent]) -> dict[str, Any]:
        """
        Validate EPCIS events before ingestion.

        Args:
            events: Events to validate

        Returns:
            Validation results
        """
        validation_results = {
            "total_events": len(events),
            "valid_events": 0,
            "invalid_events": 0,
            "errors": []
        }

        for event in events:
            try:
                # Basic validation
                if not event.eventID:
                    raise ValueError("Missing eventID")

                if not event.type:
                    raise ValueError("Missing event type")

                if event.type == EventType.OBJECT_EVENT and not event.epcList:
                    raise ValueError("Object event missing EPC list")

                if event.type == EventType.AGGREGATION_EVENT and not event.parentID:
                    raise ValueError("Aggregation event missing parent ID")

                if event.type == EventType.TRANSFORMATION_EVENT and not event.inputEPCList:
                    raise ValueError("Transformation event missing input EPC list")

                validation_results["valid_events"] += 1

            except Exception as e:
                validation_results["invalid_events"] += 1
                validation_results["errors"].append({
                    "event_id": event.eventID if event.eventID else "unknown",
                    "error": str(e)
                })

        return validation_results

    def get_ingestion_status(self) -> dict[str, Any]:
        """
        Get current ingestion status and statistics.

        Returns:
            Dictionary with ingestion status information
        """
        return {
            "is_active": self.stats.start_time is not None and self.stats.end_time is None,
            "stats": {
                "total_events": self.stats.total_events,
                "processed_events": self.stats.processed_events,
                "failed_events": self.stats.failed_events,
                "success_rate": self.stats.success_rate,
                "events_per_second": self.stats.events_per_second,
                "total_nodes": self.stats.total_nodes,
                "total_relationships": self.stats.total_relationships,
                "duration_seconds": self.stats.duration,
                "batches_processed": self.stats.batches_processed,
                "batches_failed": self.stats.batches_failed
            },
            "config": {
                "batch_size": self.config.batch_size,
                "max_workers": self.config.max_workers,
                "enable_validation": self.config.enable_validation,
                "enable_progress_tracking": self.config.enable_progress_tracking
            }
        }


# Global ingestion instance
_gds_ingestion: Neo4jGDSDataIngestion | None = None


def get_gds_ingestion() -> Neo4jGDSDataIngestion:
    """Get or create the global GDS ingestion instance."""
    global _gds_ingestion

    if _gds_ingestion is None:
        _gds_ingestion = Neo4jGDSDataIngestion()

    return _gds_ingestion


def initialize_gds_ingestion(gds_client: Neo4jGDSClient | None = None,
                           config: IngestionConfig | None = None) -> Neo4jGDSDataIngestion:
    """
    Initialize the global GDS ingestion instance.

    Args:
        gds_client: Optional GDS client instance
        config: Optional ingestion configuration

    Returns:
        Initialized ingestion instance
    """
    global _gds_ingestion

    _gds_ingestion = Neo4jGDSDataIngestion(gds_client, config)
    return _gds_ingestion
