"""
Neo4j Graph Data Science (GDS) Client for ISA Supply Chain Analytics

This module provides a comprehensive client for interacting with Neo4j GDS
for advanced supply chain graph analytics, including risk analysis algorithms.

Features:
- Connection management with automatic retry and health monitoring
- Graph projection and management
- Supply chain risk analysis algorithms (centrality, path finding, community detection)
- Integration with existing ISA architecture
- Comprehensive error handling and logging
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
from graphdatascience import GraphDataScience
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from .neo4j_gds_schema import GDS_ALGORITHMS, SupplyChainGraphSchema

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "neo4j_password"
    database: str = "neo4j"
    max_connection_pool_size: int = 50
    connection_timeout: float = 30.0
    max_retry_time: float = 30.0
    retry_delay: float = 1.0


@dataclass
class GDSConfig:
    """Configuration for GDS operations."""
    graph_name: str = "supply-chain-graph"
    concurrency: int = 4
    memory_limit: str = "4G"
    read_concurrency: int = 4
    write_concurrency: int = 4


class Neo4jGDSClient:
    """
    Neo4j Graph Data Science client for supply chain analytics.

    Provides high-level interface for graph operations, risk analysis algorithms,
    and integration with ISA's supply chain data.
    """

    def __init__(self, neo4j_config: Neo4jConfig | None = None,
                 gds_config: GDSConfig | None = None):
        self.neo4j_config = neo4j_config or Neo4jConfig()
        self.gds_config = gds_config or GDSConfig()

        self._driver: Driver | None = None
        self._gds: GraphDataScience | None = None
        self._connected = False

        # Initialize schema
        self.schema = SupplyChainGraphSchema()

        # Connection health monitoring
        self._last_health_check = 0
        self._health_check_interval = 60  # seconds
        self._connection_failures = 0
        self._max_failures = 3

    def connect(self) -> bool:
        """
        Establish connection to Neo4j database and initialize GDS.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to Neo4j database...")

            # Create Neo4j driver
            self._driver = GraphDatabase.driver(
                self.neo4j_config.uri,
                auth=(self.neo4j_config.username, self.neo4j_config.password),
                max_connection_pool_size=self.neo4j_config.max_connection_pool_size,
                connection_timeout=self.neo4j_config.connection_timeout
            )

            # Test connection
            with self._driver.session(database=self.neo4j_config.database) as session:
                result = session.run("RETURN 'Neo4j connected' as message")
                record = result.single()
                logger.info(f"Neo4j connection test: {record['message']}")

            # Initialize GDS
            self._gds = GraphDataScience(
                self.neo4j_config.uri,
                auth=(self.neo4j_config.username, self.neo4j_config.password),
                database=self.neo4j_config.database
            )

            # Test GDS
            gds_version = self._gds.version()
            logger.info(f"GDS version: {gds_version}")

            # Initialize schema
            self._initialize_schema()

            self._connected = True
            logger.info("Neo4j GDS client connected successfully")
            return True

        except AuthError as e:
            logger.error(f"Neo4j authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False

    def disconnect(self) -> None:
        """Close Neo4j connection and cleanup resources."""
        if self._driver:
            self._driver.close()
            self._driver = None

        self._gds = None
        self._connected = False
        logger.info("Neo4j GDS client disconnected")

    def _initialize_schema(self) -> None:
        """Initialize database schema with constraints and indexes."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j")

        logger.info("Initializing Neo4j schema...")

        with self._driver.session(database=self.neo4j_config.database) as session:
            # Create constraints
            for constraint in self.schema.get_node_constraints():
                try:
                    session.run(constraint)
                    logger.debug(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint creation failed (may already exist): {e}")

            # Create indexes
            for index in self.schema.get_indexes():
                try:
                    session.run(index)
                    logger.debug(f"Created index: {index}")
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")

        logger.info("Neo4j schema initialization completed")

    def is_healthy(self) -> bool:
        """Check if Neo4j connection is healthy."""
        if not self._driver:
            return False

        try:
            current_time = time.time()
            if current_time - self._last_health_check < self._health_check_interval:
                return self._connected

            with self._driver.session(database=self.neo4j_config.database) as session:
                result = session.run("MATCH () RETURN count(*) as node_count")
                record = result.single()
                record["node_count"]

            self._last_health_check = current_time
            self._connection_failures = 0
            return True

        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            self._connection_failures += 1

            if self._connection_failures >= self._max_failures:
                self._connected = False
                logger.error("Multiple health check failures, marking connection as unhealthy")

            return False

    @contextmanager
    def session(self):
        """Context manager for Neo4j sessions with automatic cleanup."""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j")

        session = self._driver.session(database=self.neo4j_config.database)
        try:
            yield session
        finally:
            session.close()

    def execute_query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j")

        with self.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_graph_projection(self, node_projection: dict[str, Any],
                              relationship_projection: dict[str, Any]) -> bool:
        """
        Create a graph projection for GDS algorithms.

        Args:
            node_projection: Node projection configuration
            relationship_projection: Relationship projection configuration

        Returns:
            bool: True if projection created successfully
        """
        if not self._gds:
            raise RuntimeError("GDS not initialized")

        try:
            logger.info(f"Creating graph projection: {self.gds_config.graph_name}")

            # Drop existing projection if it exists
            if self._gds.graph.exists(self.gds_config.graph_name).exists:
                self._gds.graph.drop(self.gds_config.graph_name)

            # Create new projection
            G = self._gds.graph.project(
                self.gds_config.graph_name,
                node_projection,
                relationship_projection
            )

            logger.info(f"Graph projection created with {G.node_count()} nodes and {G.relationship_count()} relationships")
            return True

        except Exception as e:
            logger.error(f"Failed to create graph projection: {e}")
            return False

    def run_centrality_analysis(self, algorithm: str = "betweenness") -> pd.DataFrame:
        """
        Run centrality analysis on the supply chain graph.

        Args:
            algorithm: Centrality algorithm ('betweenness', 'pagerank', 'degree')

        Returns:
            DataFrame with centrality scores
        """
        if not self._gds:
            raise RuntimeError("GDS not initialized")

        if algorithm not in GDS_ALGORITHMS["centrality"]:
            raise ValueError(f"Unsupported centrality algorithm: {algorithm}")

        try:
            logger.info(f"Running {algorithm} centrality analysis")

            query = GDS_ALGORITHMS["centrality"][algorithm]["query"]
            result = self.execute_query(query)

            df = pd.DataFrame(result)
            logger.info(f"Centrality analysis completed, found {len(df)} results")
            return df

        except Exception as e:
            logger.error(f"Centrality analysis failed: {e}")
            raise

    def run_path_analysis(self, source_name: str, target_name: str,
                         algorithm: str = "shortest_path") -> dict[str, Any]:
        """
        Run path analysis between two organizations in the supply chain.

        Args:
            source_name: Source organization name
            target_name: Target organization name
            algorithm: Path algorithm ('shortest_path', 'all_paths')

        Returns:
            Dictionary with path analysis results
        """
        if not self._gds:
            raise RuntimeError("GDS not initialized")

        if algorithm not in GDS_ALGORITHMS["pathfinding"]:
            raise ValueError(f"Unsupported path algorithm: {algorithm}")

        try:
            logger.info(f"Running {algorithm} analysis from {source_name} to {target_name}")

            query = GDS_ALGORITHMS["pathfinding"][algorithm]["query"]
            result = self.execute_query(query, {
                "source_name": source_name,
                "target_name": target_name
            })

            if result:
                logger.info(f"Path analysis completed, found {len(result)} paths")
                return result[0]  # Return first/best result
            else:
                logger.warning("No paths found between organizations")
                return {}

        except Exception as e:
            logger.error(f"Path analysis failed: {e}")
            raise

    def run_community_detection(self, algorithm: str = "louvain") -> pd.DataFrame:
        """
        Run community detection on the supply chain graph.

        Args:
            algorithm: Community detection algorithm ('louvain', 'label_propagation')

        Returns:
            DataFrame with community assignments
        """
        if not self._gds:
            raise RuntimeError("GDS not initialized")

        if algorithm not in GDS_ALGORITHMS["community"]:
            raise ValueError(f"Unsupported community algorithm: {algorithm}")

        try:
            logger.info(f"Running {algorithm} community detection")

            query = GDS_ALGORITHMS["community"][algorithm]["query"]
            result = self.execute_query(query)

            df = pd.DataFrame(result)
            logger.info(f"Community detection completed, found {len(df)} communities")
            return df

        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            raise

    def run_similarity_analysis(self, algorithm: str = "node_similarity") -> pd.DataFrame:
        """
        Run similarity analysis on the supply chain graph.

        Args:
            algorithm: Similarity algorithm ('node_similarity', 'cosine')

        Returns:
            DataFrame with similarity scores
        """
        if not self._gds:
            raise RuntimeError("GDS not initialized")

        if algorithm not in GDS_ALGORITHMS["similarity"]:
            raise ValueError(f"Unsupported similarity algorithm: {algorithm}")

        try:
            logger.info(f"Running {algorithm} similarity analysis")

            query = GDS_ALGORITHMS["similarity"][algorithm]["query"]
            result = self.execute_query(query)

            df = pd.DataFrame(result)
            logger.info(f"Similarity analysis completed, found {len(df)} similarity pairs")
            return df

        except Exception as e:
            logger.error(f"Similarity analysis failed: {e}")
            raise

    def calculate_supply_chain_risk_score(self, organization_name: str) -> dict[str, Any]:
        """
        Calculate comprehensive risk score for an organization in the supply chain.

        Args:
            organization_name: Name of the organization to analyze

        Returns:
            Dictionary with risk analysis results
        """
        try:
            logger.info(f"Calculating supply chain risk score for {organization_name}")

            # Run multiple algorithms
            centrality_df = self.run_centrality_analysis("betweenness")
            community_df = self.run_community_detection("louvain")

            # Calculate risk metrics
            risk_metrics = {
                "organization": organization_name,
                "timestamp": datetime.now().isoformat(),
                "centrality_risk": self._calculate_centrality_risk(centrality_df, organization_name),
                "community_risk": self._calculate_community_risk(community_df, organization_name),
                "overall_risk_score": 0.0,
                "recommendations": []
            }

            # Calculate overall risk score (weighted average)
            risk_metrics["overall_risk_score"] = (
                risk_metrics["centrality_risk"] * 0.6 +
                risk_metrics["community_risk"] * 0.4
            )

            # Generate recommendations
            risk_metrics["recommendations"] = self._generate_risk_recommendations(risk_metrics)

            logger.info(f"Risk analysis completed for {organization_name}: score {risk_metrics['overall_risk_score']:.2f}")
            return risk_metrics

        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            raise

    def _calculate_centrality_risk(self, centrality_df: pd.DataFrame, org_name: str) -> float:
        """Calculate risk based on centrality analysis."""
        if centrality_df.empty:
            return 0.5

        # Find organization's centrality score
        org_data = centrality_df[centrality_df["name"] == org_name]
        if org_data.empty:
            return 0.5

        score = org_data["score"].iloc[0]
        max_score = centrality_df["score"].max()

        # Higher centrality = higher risk (more critical in supply chain)
        if max_score > 0:
            return min(1.0, score / max_score)
        return 0.5

    def _calculate_community_risk(self, community_df: pd.DataFrame, org_name: str) -> float:
        """Calculate risk based on community analysis."""
        if community_df.empty:
            return 0.5

        # Count organizations per community
        community_sizes = community_df.groupby("communityId").size()

        # Find organization's community
        org_data = community_df[community_df["name"] == org_name]
        if org_data.empty:
            return 0.5

        org_community = org_data["communityId"].iloc[0]
        community_size = community_sizes[org_community]

        # Smaller communities = higher risk (less redundancy)
        max_size = community_sizes.max()
        if max_size > 0:
            return 1.0 - (community_size / max_size)
        return 0.5

    def _generate_risk_recommendations(self, risk_metrics: dict[str, Any]) -> list[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if risk_metrics["centrality_risk"] > 0.7:
            recommendations.append("High centrality risk: Consider diversifying suppliers to reduce dependency")

        if risk_metrics["community_risk"] > 0.7:
            recommendations.append("High community risk: Look for suppliers in different supply chain clusters")

        if risk_metrics["overall_risk_score"] > 0.8:
            recommendations.append("Critical risk level: Implement immediate contingency planning")

        if not recommendations:
            recommendations.append("Risk profile acceptable: Continue monitoring supply chain")

        return recommendations

    def get_graph_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics about the supply chain graph.

        Returns:
            Dictionary with graph statistics
        """
        try:
            logger.info("Collecting graph statistics")

            # Basic node and relationship counts
            node_query = "MATCH (n) RETURN labels(n) as labels, count(*) as count"
            relationship_query = "MATCH ()-[r]->() RETURN type(r) as type, count(*) as count"

            node_stats = self.execute_query(node_query)
            relationship_stats = self.execute_query(relationship_query)

            # GDS-specific statistics if projection exists
            gds_stats = {}
            if self._gds and self._gds.graph.exists(self.gds_config.graph_name).exists:
                G = self._gds.graph.get(self.gds_config.graph_name)
                gds_stats = {
                    "gds_node_count": G.node_count(),
                    "gds_relationship_count": G.relationship_count(),
                    "gds_graph_memory_usage": G.memory_usage()
                }

            stats = {
                "timestamp": datetime.now().isoformat(),
                "node_statistics": node_stats,
                "relationship_statistics": relationship_stats,
                "gds_statistics": gds_stats,
                "health_status": "healthy" if self.is_healthy() else "unhealthy"
            }

            logger.info(f"Graph statistics collected: {len(node_stats)} node types, {len(relationship_stats)} relationship types")
            return stats

        except Exception as e:
            logger.error(f"Failed to collect graph statistics: {e}")
            return {"error": str(e)}

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Global client instance
_gds_client: Neo4jGDSClient | None = None


def get_gds_client() -> Neo4jGDSClient:
    """Get or create the global GDS client instance."""
    global _gds_client

    if _gds_client is None:
        _gds_client = Neo4jGDSClient()

    return _gds_client


def initialize_gds_client(neo4j_config: Neo4jConfig | None = None,
                         gds_config: GDSConfig | None = None) -> bool:
    """
    Initialize the global GDS client.

    Args:
        neo4j_config: Neo4j connection configuration
        gds_config: GDS configuration

    Returns:
        bool: True if initialization successful
    """
    global _gds_client

    _gds_client = Neo4jGDSClient(neo4j_config, gds_config)
    return _gds_client.connect()
