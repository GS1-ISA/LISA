"""
Tests for Neo4j GDS Supply Chain Analytics

This module contains comprehensive tests for the Neo4j Graph Data Science
integration with ISA's supply chain analytics system.

Tests cover:
- Graph schema and data model
- Data ingestion from GS1/EPCIS
- Risk analysis algorithms
- API endpoints
- Configuration management
- Error handling and edge cases
"""

import pytest
import unittest.mock as mock
from datetime import datetime, timezone
from typing import Dict, Any, List

from src.neo4j_gds_schema import (
    SupplyChainGraphSchema, NodeType, RelationshipType,
    GraphNode, GraphRelationship
)
from src.neo4j_gds_client import Neo4jGDSClient, Neo4jConfig, GDSConfig
from src.neo4j_gds_ingestion import (
    GS1EPCISGraphTransformer, Neo4jGDSDataIngestion
)
from src.neo4j_gds_analytics import SupplyChainRiskAnalyzer, RiskLevel
from src.epcis_tracker import EPCISEvent, EventType, Action, BizStep


class TestSupplyChainGraphSchema:
    """Test cases for graph schema definitions."""

    def test_node_types(self):
        """Test node type definitions."""
        assert NodeType.PRODUCT.value == "Product"
        assert NodeType.LOCATION.value == "Location"
        assert NodeType.ORGANIZATION.value == "Organization"
        assert NodeType.EVENT.value == "Event"

    def test_relationship_types(self):
        """Test relationship type definitions."""
        assert RelationshipType.SUPPLIES_TO.value == "SUPPLIES_TO"
        assert RelationshipType.CONTAINS.value == "CONTAINS"
        assert RelationshipType.TRANSFORMS_INTO.value == "TRANSFORMS_INTO"

    def test_create_product_node(self):
        """Test creating product nodes."""
        schema = SupplyChainGraphSchema()
        node = schema.create_product_node(
            epc="urn:epc:id:sgtin:123456789.012345.123456789",
            gtin="12345678901234",
            category="finished_product"
        )

        assert node.node_type == NodeType.PRODUCT
        assert node.properties["epc"] == "urn:epc:id:sgtin:123456789.012345.123456789"
        assert node.properties["gtin"] == "12345678901234"
        assert node.properties["category"] == "finished_product"
        assert "created_at" in node.properties

    def test_create_organization_node(self):
        """Test creating organization nodes."""
        schema = SupplyChainGraphSchema()
        node = schema.create_organization_node(
            org_id="urn:epc:id:sgln:123456789.0000.0",
            name="Test Manufacturer",
            org_type="manufacturer"
        )

        assert node.node_type == NodeType.ORGANIZATION
        assert node.properties["id"] == "urn:epc:id:sgln:123456789.0000.0"
        assert node.properties["name"] == "Test Manufacturer"
        assert node.properties["type"] == "manufacturer"

    def test_create_supply_chain_relationship(self):
        """Test creating supply chain relationships."""
        schema = SupplyChainGraphSchema()
        from_node = schema.create_organization_node("supplier_1", "Supplier A", "supplier")
        to_node = schema.create_organization_node("supplier_2", "Supplier B", "manufacturer")

        relationship = schema.create_supply_chain_relationship(
            from_node, to_node, criticality=0.8
        )

        assert relationship.relationship_type == RelationshipType.SUPPLIES_TO
        assert relationship.from_node == from_node
        assert relationship.to_node == to_node
        assert relationship.properties["criticality"] == 0.8


class TestGS1EPCISGraphTransformer:
    """Test cases for GS1/EPCIS to graph transformation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.transformer = GS1EPCISGraphTransformer()

    def test_transform_object_event(self):
        """Test transformation of Object Events."""
        event = EPCISEvent(
            eventID="test_event_1",
            type=EventType.OBJECT_EVENT,
            action=Action.OBSERVE,
            bizStep=BizStep.SHIPPING,
            epcList=["epc1", "epc2"],
            eventTime=datetime.now(timezone.utc).isoformat()
        )

        result = self.transformer.transform_epcis_event(event)

        assert "nodes" in result
        assert "relationships" in result
        assert len(result["nodes"]) == 3  # Event + 2 Products
        assert len(result["relationships"]) == 2  # 2 PARTICIPATES_IN relationships

    def test_transform_aggregation_event(self):
        """Test transformation of Aggregation Events."""
        event = EPCISEvent(
            eventID="test_agg_event",
            type=EventType.AGGREGATION_EVENT,
            action=Action.ADD,
            bizStep=BizStep.PACKING,
            parentID="parent_epc",
            childEPCs=["child1", "child2"],
            eventTime=datetime.now(timezone.utc).isoformat()
        )

        result = self.transformer.transform_epcis_event(event)

        assert len(result["nodes"]) == 4  # Event + Parent + 2 Children
        assert len(result["relationships"]) >= 3  # PARTICIPATES_IN + CONTAINS relationships

    def test_transform_transformation_event(self):
        """Test transformation of Transformation Events."""
        event = EPCISEvent(
            eventID="test_trans_event",
            type=EventType.TRANSFORMATION_EVENT,
            action=Action.OBSERVE,
            bizStep=BizStep.PACKING,
            inputEPCList=["input1", "input2"],
            outputEPCList=["output1"],
            eventTime=datetime.now(timezone.utc).isoformat()
        )

        result = self.transformer.transform_epcis_event(event)

        assert len(result["nodes"]) >= 4  # Event + 2 Inputs + 1 Output
        # Should have PARTICIPATES_IN and TRANSFORMS_INTO relationships

    def test_extract_gtin_from_epc(self):
        """Test GTIN extraction from EPC."""
        epc = "urn:epc:id:sgtin:123456789.012345.123456789"
        gtin = self.transformer._extract_gtin_from_epc(epc)

        assert gtin == "12345678901234"

    def test_invalid_epc_gtin_extraction(self):
        """Test GTIN extraction from invalid EPC."""
        invalid_epc = "invalid_epc_format"
        gtin = self.transformer._extract_gtin_from_epc(invalid_epc)

        assert gtin is None


class TestNeo4jGDSClient:
    """Test cases for Neo4j GDS client."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test_password",
            database="neo4j"
        )
        self.gds_config = GDSConfig(graph_name="test-graph")

    @mock.patch('src.neo4j_gds_client.GraphDatabase')
    @mock.patch('src.neo4j_gds_client.GraphDataScience')
    def test_client_initialization(self, mock_gds, mock_graph_db):
        """Test client initialization."""
        # Mock the driver and GDS
        mock_driver = mock.MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        mock_session = mock.MagicMock()
        mock_driver.session.return_value = mock_session
        mock_session.run.return_value = [{"message": "Neo4j connected"}]

        mock_gds_instance = mock.MagicMock()
        mock_gds.return_value = mock_gds_instance
        mock_gds_instance.version.return_value = "2.0.0"

        client = Neo4jGDSClient(self.config, self.gds_config)
        connected = client.connect()

        assert connected
        assert client._connected
        mock_graph_db.driver.assert_called_once()
        mock_gds.assert_called_once()

    def test_client_health_check(self):
        """Test client health check functionality."""
        with mock.patch('src.neo4j_gds_client.GraphDatabase') as mock_graph_db:
            mock_driver = mock.MagicMock()
            mock_graph_db.driver.return_value = mock_driver
            mock_session = mock.MagicMock()
            mock_driver.session.return_value = mock_session
            mock_session.run.return_value = [1]

            client = Neo4jGDSClient(self.config, self.gds_config)
            client._driver = mock_driver

            healthy = client.is_healthy()
            assert healthy

    def test_execute_query(self):
        """Test query execution."""
        with mock.patch('src.neo4j_gds_client.GraphDatabase') as mock_graph_db:
            mock_driver = mock.MagicMock()
            mock_graph_db.driver.return_value = mock_driver
            mock_session = mock.MagicMock()
            mock_driver.session.return_value = mock_session
            mock_session.run.return_value = [{"result": "test"}]

            client = Neo4jGDSClient(self.config, self.gds_config)
            client._driver = mock_driver

            result = client.execute_query("MATCH (n) RETURN n")
            assert result == [{"result": "test"}]


class TestSupplyChainRiskAnalyzer:
    """Test cases for supply chain risk analysis."""

    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = SupplyChainRiskAnalyzer()

    @mock.patch('src.neo4j_gds_analytics.Neo4jGDSClient')
    def test_risk_analysis_initialization(self, mock_client):
        """Test risk analyzer initialization."""
        mock_client_instance = mock.MagicMock()
        mock_client.return_value = mock_client_instance

        analyzer = SupplyChainRiskAnalyzer(mock_client_instance)
        assert analyzer.gds_client == mock_client_instance

    def test_risk_level_classification(self):
        """Test risk level classification."""
        assert self.analyzer._classify_risk_level(0.3) == RiskLevel.LOW
        assert self.analyzer._classify_risk_level(0.5) == RiskLevel.MEDIUM
        assert self.analyzer._classify_risk_level(0.7) == RiskLevel.HIGH
        assert self.analyzer._classify_risk_level(0.9) == RiskLevel.CRITICAL

    def test_centrality_risk_calculation(self):
        """Test centrality risk calculation."""
        centrality_df = mock.MagicMock()
        centrality_df.empty = False
        centrality_df.__getitem__.return_value.__getitem__.return_value.iloc = mock.MagicMock()
        centrality_df.__getitem__.return_value.__getitem__.return_value.iloc.__getitem__.return_value = 0.8

        # Mock the organization data
        org_data = mock.MagicMock()
        org_data.empty = False
        centrality_df.__getitem__.return_value.__getitem__.return_value = org_data

        risk = self.analyzer._calculate_centrality_risk(centrality_df, "test_org")
        assert isinstance(risk, float)
        assert 0.0 <= risk <= 1.0

    def test_empty_centrality_risk(self):
        """Test centrality risk with empty data."""
        centrality_df = mock.MagicMock()
        centrality_df.empty = True

        risk = self.analyzer._calculate_centrality_risk(centrality_df, "test_org")
        assert risk == 0.5  # Default medium risk

    def test_risk_recommendations_generation(self):
        """Test risk recommendations generation."""
        recommendations = self.analyzer._generate_risk_recommendations(
            centrality_risk=0.8,
            community_risk=0.3,
            path_risk=0.6,
            supplier_diversity_risk=0.2,
            geographic_risk=0.4,
            temporal_risk=0.1
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)


class TestDataIngestion:
    """Test cases for data ingestion functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.ingestion = Neo4jGDSDataIngestion()

    def test_ingestion_initialization(self):
        """Test ingestion initialization."""
        assert self.ingestion.gds_client is not None
        assert self.ingestion.transformer is not None
        assert self.ingestion.config is not None

    def test_batch_creation(self):
        """Test batch creation from events."""
        events = [mock.MagicMock() for _ in range(2500)]
        batches = self.ingestion._create_batches(events)

        assert len(batches) == 3  # 2500 / 1000 = 2.5 -> 3 batches
        assert len(batches[0]) == 1000
        assert len(batches[1]) == 1000
        assert len(batches[2]) == 500

    def test_event_validation(self):
        """Test EPCIS event validation."""
        # Valid event
        valid_event = EPCISEvent(
            eventID="valid_event",
            type=EventType.OBJECT_EVENT,
            action=Action.OBSERVE,
            bizStep=BizStep.SHIPPING,
            epcList=["epc1"],
            eventTime=datetime.now(timezone.utc).isoformat()
        )

        # Invalid event (missing required fields)
        invalid_event = EPCISEvent(
            eventID="",  # Invalid: empty eventID
            type=EventType.OBJECT_EVENT,
            action=Action.OBSERVE,
            bizStep=BizStep.SHIPPING
        )

        validation_result = self.ingestion.validate_ingestion_data([valid_event, invalid_event])

        assert validation_result["total_events"] == 2
        assert validation_result["valid_events"] == 1
        assert validation_result["invalid_events"] == 1
        assert len(validation_result["errors"]) == 1


class TestConfiguration:
    """Test cases for configuration management."""

    @mock.patch.dict('os.environ', {
        'NEO4J_URI': 'bolt://test:7687',
        'NEO4J_USERNAME': 'test_user',
        'NEO4J_PASSWORD': 'test_pass',
        'GDS_GRAPH_NAME': 'test_graph'
    })
    def test_configuration_from_environment(self):
        """Test loading configuration from environment variables."""
        from src.neo4j_gds_config import Neo4jGDSConfiguration

        config = Neo4jGDSConfiguration()

        neo4j_config = config.get_neo4j_config()
        assert neo4j_config.uri == 'bolt://test:7687'
        assert neo4j_config.username == 'test_user'
        assert neo4j_config.password == 'test_pass'

        gds_config = config.get_gds_config()
        assert gds_config.graph_name == 'test_graph'

    def test_default_configuration(self):
        """Test default configuration values."""
        from src.neo4j_gds_config import Neo4jGDSConfiguration

        config = Neo4jGDSConfiguration()

        neo4j_config = config.get_neo4j_config()
        assert neo4j_config.uri == 'bolt://localhost:7687'
        assert neo4j_config.username == 'neo4j'
        assert neo4j_config.database == 'neo4j'

        gds_config = config.get_gds_config()
        assert gds_config.graph_name == 'supply-chain-graph'
        assert gds_config.concurrency == 4


# Integration tests
class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.integration
    def test_full_workflow_simulation(self):
        """Test a simulated full workflow (requires Neo4j to be running)."""
        # This test would require a running Neo4j instance
        # For now, it's a placeholder for integration testing
        pytest.skip("Integration test requires running Neo4j instance")

        # Example workflow:
        # 1. Create sample EPCIS events
        # 2. Transform to graph format
        # 3. Ingest into Neo4j
        # 4. Run risk analysis
        # 5. Verify results

        # Sample implementation would go here
        pass

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test connection failures
        with mock.patch('src.neo4j_gds_client.GraphDatabase') as mock_graph_db:
            mock_graph_db.driver.side_effect = Exception("Connection failed")

            client = Neo4jGDSClient()
            connected = client.connect()

            assert not connected
            assert not client._connected

    def test_data_validation_edge_cases(self):
        """Test data validation with edge cases."""
        ingestion = Neo4jGDSDataIngestion()

        # Test with empty event list
        validation = ingestion.validate_ingestion_data([])
        assert validation["total_events"] == 0
        assert validation["valid_events"] == 0
        assert validation["invalid_events"] == 0

        # Test with malformed events
        malformed_event = mock.MagicMock()
        malformed_event.eventID = None
        validation = ingestion.validate_ingestion_data([malformed_event])
        assert validation["invalid_events"] == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])