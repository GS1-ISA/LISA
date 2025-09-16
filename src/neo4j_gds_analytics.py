"""
Neo4j GDS Analytics Module for Supply Chain Risk Analysis

This module implements advanced graph algorithms using Neo4j Graph Data Science (GDS)
for comprehensive supply chain risk analysis, including:

- Centrality analysis for identifying critical suppliers and bottlenecks
- Path analysis for supply chain route optimization and risk assessment
- Community detection for supply chain cluster analysis
- Risk propagation modeling and prediction
- Supply chain resilience analysis
- Predictive analytics for disruption scenarios

The module provides both individual algorithm implementations and comprehensive
risk assessment pipelines tailored for supply chain management.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

from .neo4j_gds_client import Neo4jGDSClient, get_gds_client
from .neo4j_gds_schema import SupplyChainGraphSchema, NodeType, RelationshipType

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlgorithmType(Enum):
    """Supported GDS algorithm types."""
    CENTRALITY = "centrality"
    PATHFINDING = "pathfinding"
    COMMUNITY = "community"
    SIMILARITY = "similarity"
    LINK_PREDICTION = "link_prediction"


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for supply chain analysis."""
    centrality_risk: float
    community_risk: float
    path_risk: float
    supplier_diversity_risk: float
    geographic_risk: float
    temporal_risk: float
    overall_risk_score: float
    risk_level: RiskLevel
    confidence_score: float
    recommendations: List[str]
    timestamp: datetime


@dataclass
class SupplyChainPath:
    """Represents a supply chain path with risk metrics."""
    nodes: List[str]
    relationships: List[str]
    total_cost: float
    total_distance: float
    risk_score: float
    reliability_score: float
    alternative_paths: int


@dataclass
class DisruptionScenario:
    """Models potential supply chain disruptions."""
    affected_nodes: List[str]
    disruption_type: str
    impact_probability: float
    impact_severity: float
    cascade_effects: List[str]
    mitigation_strategies: List[str]
    estimated_recovery_time: timedelta


class SupplyChainRiskAnalyzer:
    """
    Advanced supply chain risk analyzer using Neo4j GDS algorithms.

    Provides comprehensive risk assessment through multiple algorithmic approaches,
    including centrality analysis, community detection, path finding, and predictive modeling.
    """

    def __init__(self, gds_client: Optional[Neo4jGDSClient] = None):
        self.gds_client = gds_client or get_gds_client()
        self.schema = SupplyChainGraphSchema()

        # Algorithm configurations
        self._algorithm_configs = {
            "betweenness_centrality": {
                "query": """
                CALL gds.betweenness.stream('supply-chain-graph', {
                    samplingSize: 100,
                    samplingSeed: 42
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name,
                       gds.util.asNode(nodeId).id AS id,
                       score,
                       CASE
                         WHEN score > 0.8 THEN 'critical'
                         WHEN score > 0.5 THEN 'high'
                         WHEN score > 0.2 THEN 'medium'
                         ELSE 'low'
                       END AS risk_level
                ORDER BY score DESC
                """,
                "description": "Identify critical nodes in supply chain network"
            },
            "page_rank": {
                "query": """
                CALL gds.pageRank.stream('supply-chain-graph', {
                    maxIterations: 20,
                    dampingFactor: 0.85,
                    tolerance: 0.0001
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name,
                       gds.util.asNode(nodeId).id AS id,
                       score
                ORDER BY score DESC
                """,
                "description": "Measure influence and importance in supply chain"
            },
            "louvain_community": {
                "query": """
                CALL gds.louvain.stream('supply-chain-graph', {
                    maxIterations: 10,
                    tolerance: 0.0001
                })
                YIELD nodeId, communityId, intermediateCommunityIds
                RETURN gds.util.asNode(nodeId).name AS name,
                       gds.util.asNode(nodeId).id AS id,
                       communityId,
                       size(intermediateCommunityIds) AS community_hierarchy
                ORDER BY communityId
                """,
                "description": "Detect supply chain communities and clusters"
            },
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
                ORDER BY totalCost ASC
                """,
                "description": "Find optimal supply chain paths"
            }
        }

    def analyze_supply_chain_risks(self, organization_name: str,
                                  include_historical: bool = True) -> RiskMetrics:
        """
        Perform comprehensive supply chain risk analysis for an organization.

        Args:
            organization_name: Name of the organization to analyze
            include_historical: Whether to include historical data in analysis

        Returns:
            Comprehensive risk metrics
        """
        logger.info(f"Starting comprehensive risk analysis for {organization_name}")

        start_time = datetime.now()

        try:
            # Run multiple algorithms in parallel
            centrality_results = self._run_centrality_analysis()
            community_results = self._run_community_analysis()
            path_results = self._analyze_supply_paths(organization_name)

            # Calculate individual risk components
            centrality_risk = self._calculate_centrality_risk(
                centrality_results, organization_name
            )
            community_risk = self._calculate_community_risk(
                community_results, organization_name
            )
            path_risk = self._calculate_path_risk(path_results)
            supplier_diversity_risk = self._calculate_supplier_diversity_risk(organization_name)
            geographic_risk = self._calculate_geographic_risk(organization_name)
            temporal_risk = self._calculate_temporal_risk(organization_name)

            # Calculate overall risk score (weighted average)
            weights = {
                'centrality': 0.25,
                'community': 0.20,
                'path': 0.20,
                'supplier_diversity': 0.15,
                'geographic': 0.10,
                'temporal': 0.10
            }

            overall_risk_score = (
                centrality_risk * weights['centrality'] +
                community_risk * weights['community'] +
                path_risk * weights['path'] +
                supplier_diversity_risk * weights['supplier_diversity'] +
                geographic_risk * weights['geographic'] +
                temporal_risk * weights['temporal']
            )

            # Determine risk level
            risk_level = self._classify_risk_level(overall_risk_score)

            # Generate recommendations
            recommendations = self._generate_risk_recommendations(
                centrality_risk, community_risk, path_risk,
                supplier_diversity_risk, geographic_risk, temporal_risk
            )

            # Calculate confidence score based on data completeness
            confidence_score = self._calculate_confidence_score(
                centrality_results, community_results, path_results
            )

            risk_metrics = RiskMetrics(
                centrality_risk=centrality_risk,
                community_risk=community_risk,
                path_risk=path_risk,
                supplier_diversity_risk=supplier_diversity_risk,
                geographic_risk=geographic_risk,
                temporal_risk=temporal_risk,
                overall_risk_score=overall_risk_score,
                risk_level=risk_level,
                confidence_score=confidence_score,
                recommendations=recommendations,
                timestamp=start_time
            )

            logger.info(f"Risk analysis completed for {organization_name}: "
                       f"score {overall_risk_score:.3f}, level {risk_level.value}")

            return risk_metrics

        except Exception as e:
            logger.error(f"Risk analysis failed for {organization_name}: {e}")
            raise

    def _run_centrality_analysis(self) -> pd.DataFrame:
        """Run centrality analysis on the supply chain graph."""
        try:
            query = self._algorithm_configs["betweenness_centrality"]["query"]
            results = self.gds_client.execute_query(query)
            return pd.DataFrame(results)
        except Exception as e:
            logger.warning(f"Centrality analysis failed: {e}")
            return pd.DataFrame()

    def _run_community_analysis(self) -> pd.DataFrame:
        """Run community detection on the supply chain graph."""
        try:
            query = self._algorithm_configs["louvain_community"]["query"]
            results = self.gds_client.execute_query(query)
            return pd.DataFrame(results)
        except Exception as e:
            logger.warning(f"Community analysis failed: {e}")
            return pd.DataFrame()

    def _analyze_supply_paths(self, organization_name: str) -> List[SupplyChainPath]:
        """Analyze supply chain paths for the organization."""
        paths = []

        try:
            # Find suppliers and customers
            suppliers_query = """
            MATCH (org:Organization {name: $org_name})<-[:SUPPLIES_TO]-(supplier:Organization)
            RETURN supplier.name AS supplier_name, supplier.id AS supplier_id
            """

            customers_query = """
            MATCH (org:Organization {name: $org_name})-[:SUPPLIES_TO]->(customer:Organization)
            RETURN customer.name AS customer_name, customer.id AS customer_id
            """

            suppliers = self.gds_client.execute_query(suppliers_query, {"org_name": organization_name})
            customers = self.gds_client.execute_query(customers_query, {"org_name": organization_name})

            # Analyze paths to/from suppliers and customers
            for supplier in suppliers:
                path = self._calculate_path_metrics(organization_name, supplier["supplier_name"])
                if path:
                    paths.append(path)

            for customer in customers:
                path = self._calculate_path_metrics(customer["customer_name"], organization_name)
                if path:
                    paths.append(path)

        except Exception as e:
            logger.warning(f"Supply path analysis failed: {e}")

        return paths

    def _calculate_path_metrics(self, source: str, target: str) -> Optional[SupplyChainPath]:
        """Calculate metrics for a supply chain path."""
        try:
            query = self._algorithm_configs["shortest_path"]["query"]
            results = self.gds_client.execute_query(query, {
                "source_name": source,
                "target_name": target
            })

            if results:
                result = results[0]
                return SupplyChainPath(
                    nodes=result["nodeNames"],
                    relationships=[],  # Would need additional query to get relationships
                    total_cost=result["totalCost"],
                    total_distance=len(result["nodeNames"]) - 1,
                    risk_score=self._estimate_path_risk(result["nodeNames"]),
                    reliability_score=self._estimate_path_reliability(result["nodeNames"]),
                    alternative_paths=self._count_alternative_paths(source, target)
                )

        except Exception as e:
            logger.debug(f"Path calculation failed for {source} -> {target}: {e}")

        return None

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

    def _calculate_path_risk(self, paths: List[SupplyChainPath]) -> float:
        """Calculate risk based on supply chain path analysis."""
        if not paths:
            return 0.8  # High risk if no paths found

        # Average risk across all paths
        total_risk = sum(path.risk_score for path in paths)
        avg_risk = total_risk / len(paths)

        # Factor in path diversity
        unique_nodes = set()
        for path in paths:
            unique_nodes.update(path.nodes)

        diversity_factor = len(unique_nodes) / sum(len(path.nodes) for path in paths)
        diversity_factor = min(1.0, diversity_factor)

        # Lower diversity = higher risk
        return avg_risk * (2.0 - diversity_factor)

    def _calculate_supplier_diversity_risk(self, org_name: str) -> float:
        """Calculate risk based on supplier diversity."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})<-[:SUPPLIES_TO]-(supplier:Organization)
            RETURN count(DISTINCT supplier) AS supplier_count
            """

            result = self.gds_client.execute_query(query, {"org_name": org_name})
            if result:
                supplier_count = result[0]["supplier_count"]
                # Fewer suppliers = higher risk
                return max(0.0, 1.0 - (supplier_count / 10.0))
            return 1.0

        except Exception:
            return 0.5

    def _calculate_geographic_risk(self, org_name: str) -> float:
        """Calculate risk based on geographic distribution."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})-[:LOCATED_AT]->(loc:Location)
            RETURN count(DISTINCT loc.country) AS country_count
            """

            result = self.gds_client.execute_query(query, {"org_name": org_name})
            if result:
                country_count = result[0]["country_count"]
                # More countries = lower risk
                return max(0.0, 1.0 - (country_count / 5.0))
            return 1.0

        except Exception:
            return 0.5

    def _calculate_temporal_risk(self, org_name: str) -> float:
        """Calculate risk based on temporal patterns."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})-[r:SUPPLIES_TO]->()
            WHERE r.contract_end IS NOT NULL
            RETURN avg(duration.between(date(), date(r.contract_end)).days) AS avg_days_to_expiry
            """

            result = self.gds_client.execute_query(query, {"org_name": org_name})
            if result and result[0]["avg_days_to_expiry"]:
                avg_days = result[0]["avg_days_to_expiry"]
                # Shorter time to contract expiry = higher risk
                return max(0.0, 1.0 - (avg_days / 365.0))
            return 0.5

        except Exception:
            return 0.5

    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level based on overall score."""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_risk_recommendations(self, centrality_risk: float, community_risk: float,
                                      path_risk: float, supplier_diversity_risk: float,
                                      geographic_risk: float, temporal_risk: float) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if centrality_risk > 0.7:
            recommendations.append("High centrality risk: Diversify suppliers to reduce dependency on critical nodes")

        if community_risk > 0.7:
            recommendations.append("High community risk: Establish relationships with suppliers in different supply chain clusters")

        if path_risk > 0.7:
            recommendations.append("High path risk: Develop alternative supply routes and backup suppliers")

        if supplier_diversity_risk > 0.7:
            recommendations.append("Low supplier diversity: Increase number of suppliers and reduce dependency on single sources")

        if geographic_risk > 0.7:
            recommendations.append("High geographic risk: Diversify supplier locations across multiple regions/countries")

        if temporal_risk > 0.7:
            recommendations.append("High temporal risk: Renegotiate contracts with longer terms and automatic renewals")

        if not recommendations:
            recommendations.append("Risk profile acceptable: Continue monitoring and maintain current mitigation strategies")

        return recommendations

    def _calculate_confidence_score(self, centrality_df: pd.DataFrame,
                                  community_df: pd.DataFrame,
                                  paths: List[SupplyChainPath]) -> float:
        """Calculate confidence score based on data completeness."""
        confidence_factors = []

        # Centrality data completeness
        if not centrality_df.empty:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.3)

        # Community data completeness
        if not community_df.empty:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.3)

        # Path data completeness
        if paths:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.5)

        return sum(confidence_factors) / len(confidence_factors)

    def _estimate_path_risk(self, nodes: List[str]) -> float:
        """Estimate risk score for a supply chain path."""
        # Simplified risk estimation based on path length and node diversity
        path_length = len(nodes)
        unique_nodes = len(set(nodes))

        # Longer paths and less diversity = higher risk
        length_risk = min(1.0, path_length / 10.0)
        diversity_risk = 1.0 - (unique_nodes / path_length)

        return (length_risk + diversity_risk) / 2.0

    def _estimate_path_reliability(self, nodes: List[str]) -> float:
        """Estimate reliability score for a supply chain path."""
        # Simplified reliability based on path characteristics
        path_length = len(nodes)

        # Shorter paths generally more reliable
        return max(0.1, 1.0 - (path_length / 20.0))

    def _count_alternative_paths(self, source: str, target: str) -> int:
        """Count alternative paths between source and target."""
        try:
            query = """
            MATCH (source:Organization {name: $source_name})
            MATCH (target:Organization {name: $target_name})
            CALL gds.allShortestPaths.dijkstra.stream('supply-chain-graph', {
                sourceNode: source,
                targetNode: target,
                relationshipWeightProperty: 'criticality'
            })
            YIELD index, sourceNode, targetNode, nodeIds, totalCost
            RETURN count(*) AS path_count
            """

            result = self.gds_client.execute_query(query, {
                "source_name": source,
                "target_name": target
            })

            return result[0]["path_count"] if result else 0

        except Exception:
            return 0

    def predict_disruption_scenarios(self, organization_name: str,
                                   scenario_count: int = 5) -> List[DisruptionScenario]:
        """
        Predict potential disruption scenarios for an organization.

        Args:
            organization_name: Organization to analyze
            scenario_count: Number of scenarios to generate

        Returns:
            List of potential disruption scenarios
        """
        scenarios = []

        try:
            # Get critical suppliers
            critical_suppliers = self._identify_critical_suppliers(organization_name)

            # Get geographic concentrations
            geographic_risks = self._identify_geographic_concentrations(organization_name)

            # Get temporal risks
            temporal_risks = self._identify_temporal_risks(organization_name)

            # Generate scenarios based on identified risks
            for i in range(min(scenario_count, len(critical_suppliers) + len(geographic_risks) + len(temporal_risks))):
                if i < len(critical_suppliers):
                    scenario = self._create_supplier_disruption_scenario(critical_suppliers[i])
                    scenarios.append(scenario)
                elif i < len(critical_suppliers) + len(geographic_risks):
                    idx = i - len(critical_suppliers)
                    scenario = self._create_geographic_disruption_scenario(geographic_risks[idx])
                    scenarios.append(scenario)
                else:
                    idx = i - len(critical_suppliers) - len(geographic_risks)
                    scenario = self._create_temporal_disruption_scenario(temporal_risks[idx])
                    scenarios.append(scenario)

        except Exception as e:
            logger.error(f"Disruption scenario prediction failed: {e}")

        return scenarios

    def _identify_critical_suppliers(self, org_name: str) -> List[Dict[str, Any]]:
        """Identify critical suppliers based on centrality and dependency."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})<-[:SUPPLIES_TO]-(supplier:Organization)
            RETURN supplier.name AS name,
                   supplier.id AS id,
                   supplier.criticality AS criticality
            ORDER BY supplier.criticality DESC
            LIMIT 10
            """

            results = self.gds_client.execute_query(query, {"org_name": org_name})
            return results

        except Exception:
            return []

    def _identify_geographic_concentrations(self, org_name: str) -> List[Dict[str, Any]]:
        """Identify geographic concentrations that could cause regional disruptions."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})-[:LOCATED_AT]->(loc:Location)
            RETURN loc.country AS country,
                   count(*) AS supplier_count
            ORDER BY supplier_count DESC
            LIMIT 5
            """

            results = self.gds_client.execute_query(query, {"org_name": org_name})
            return results

        except Exception:
            return []

    def _identify_temporal_risks(self, org_name: str) -> List[Dict[str, Any]]:
        """Identify temporal risks from contract expirations."""
        try:
            query = """
            MATCH (org:Organization {name: $org_name})-[r:SUPPLIES_TO]->(supplier:Organization)
            WHERE r.contract_end IS NOT NULL
            AND duration.between(date(), date(r.contract_end)).days < 90
            RETURN supplier.name AS name,
                   r.contract_end AS expiry_date,
                   duration.between(date(), date(r.contract_end)).days AS days_to_expiry
            ORDER BY days_to_expiry ASC
            """

            results = self.gds_client.execute_query(query, {"org_name": org_name})
            return results

        except Exception:
            return []

    def _create_supplier_disruption_scenario(self, supplier: Dict[str, Any]) -> DisruptionScenario:
        """Create a disruption scenario based on supplier criticality."""
        return DisruptionScenario(
            affected_nodes=[supplier["name"]],
            disruption_type="supplier_failure",
            impact_probability=supplier.get("criticality", 0.5),
            impact_severity=supplier.get("criticality", 0.5),
            cascade_effects=self._calculate_cascade_effects(supplier["name"]),
            mitigation_strategies=[
                f"Develop backup supplier for {supplier['name']}",
                "Increase safety stock levels",
                "Implement dual sourcing strategy"
            ],
            estimated_recovery_time=timedelta(days=30)
        )

    def _create_geographic_disruption_scenario(self, geo_risk: Dict[str, Any]) -> DisruptionScenario:
        """Create a disruption scenario based on geographic concentration."""
        return DisruptionScenario(
            affected_nodes=[],  # Would need to query for affected suppliers
            disruption_type="regional_disruption",
            impact_probability=0.3,
            impact_severity=min(1.0, geo_risk.get("supplier_count", 1) / 10.0),
            cascade_effects=[f"Disruption in {geo_risk['country']}"],
            mitigation_strategies=[
                f"Diversify suppliers outside {geo_risk['country']}",
                "Establish regional warehouses",
                "Develop local supplier networks"
            ],
            estimated_recovery_time=timedelta(days=60)
        )

    def _create_temporal_disruption_scenario(self, temporal_risk: Dict[str, Any]) -> DisruptionScenario:
        """Create a disruption scenario based on contract expiration."""
        return DisruptionScenario(
            affected_nodes=[temporal_risk["name"]],
            disruption_type="contract_expiration",
            impact_probability=0.8,
            impact_severity=0.6,
            cascade_effects=[f"Loss of supply from {temporal_risk['name']}"],
            mitigation_strategies=[
                f"Renegotiate contract with {temporal_risk['name']}",
                f"Identify replacement supplier before {temporal_risk['expiry_date']}",
                "Implement supplier performance monitoring"
            ],
            estimated_recovery_time=timedelta(days=temporal_risk.get("days_to_expiry", 30))
        )

    def _calculate_cascade_effects(self, supplier_name: str) -> List[str]:
        """Calculate potential cascade effects of a supplier disruption."""
        try:
            query = """
            MATCH (supplier:Organization {name: $supplier_name})-[:SUPPLIES_TO*1..3]->(affected:Organization)
            RETURN DISTINCT affected.name AS affected_name
            LIMIT 10
            """

            results = self.gds_client.execute_query(query, {"supplier_name": supplier_name})
            return [result["affected_name"] for result in results]

        except Exception:
            return []


# Global analyzer instance
_supply_chain_analyzer: Optional[SupplyChainRiskAnalyzer] = None


def get_supply_chain_analyzer() -> SupplyChainRiskAnalyzer:
    """Get or create the global supply chain analyzer instance."""
    global _supply_chain_analyzer

    if _supply_chain_analyzer is None:
        _supply_chain_analyzer = SupplyChainRiskAnalyzer()

    return _supply_chain_analyzer


def initialize_supply_chain_analyzer(gds_client: Optional[Neo4jGDSClient] = None) -> SupplyChainRiskAnalyzer:
    """
    Initialize the global supply chain analyzer.

    Args:
        gds_client: Optional GDS client instance

    Returns:
        Initialized analyzer instance
    """
    global _supply_chain_analyzer

    _supply_chain_analyzer = SupplyChainRiskAnalyzer(gds_client)
    return _supply_chain_analyzer