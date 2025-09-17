"""
Supply chain geospatial analysis for EUDR compliance.

This module provides advanced geospatial analysis of supply chains,
integrating location data with deforestation risk assessments to
identify vulnerabilities and optimization opportunities.
"""

import logging
from dataclasses import dataclass
from typing import Any

import networkx as nx

from .risk_assessment import GeospatialRiskAssessor, LocationRiskAssessment


@dataclass
class SupplyChainNode:
    """Represents a node in the supply chain network."""
    id: str
    name: str
    latitude: float
    longitude: float
    node_type: str  # supplier, processor, distributor, etc.
    risk_assessment: LocationRiskAssessment | None = None
    connections: list[str] = None  # IDs of connected nodes

    def __post_init__(self):
        if self.connections is None:
            self.connections = []


@dataclass
class SupplyChainPath:
    """Represents a path through the supply chain."""
    nodes: list[SupplyChainNode]
    total_distance_km: float
    total_risk_score: float
    deforestation_exposure: float
    alternative_paths: list[list[str]]


@dataclass
class GeospatialOptimization:
    """Optimization recommendations for supply chain."""
    high_risk_segments: list[dict[str, Any]]
    alternative_routes: list[SupplyChainPath]
    risk_reduction_potential: float
    cost_benefit_analysis: dict[str, Any]


class SupplyChainGeospatialAnalyzer:
    """
    Advanced geospatial analysis for supply chain optimization.

    Analyzes supply chain networks spatially, identifies risk concentrations,
    and provides optimization recommendations for EUDR compliance.
    """

    def __init__(self, risk_assessor: GeospatialRiskAssessor | None = None):
        """
        Initialize the supply chain analyzer.

        Args:
            risk_assessor: Optional pre-configured risk assessor
        """
        self.risk_assessor = risk_assessor or GeospatialRiskAssessor()
        self.logger = logging.getLogger(__name__)

    def analyze_supply_chain_network(
        self,
        nodes: list[SupplyChainNode],
        connections: list[tuple[str, str]],
        buffer_km: float = 50,
        lookback_years: int = 5
    ) -> dict[str, Any]:
        """
        Perform comprehensive geospatial analysis of supply chain network.

        Args:
            nodes: List of supply chain nodes
            connections: List of (from_id, to_id) connections
            buffer_km: Analysis buffer in kilometers
            lookback_years: Years to look back for risk data

        Returns:
            Comprehensive network analysis results
        """
        try:
            # Build network graph
            network_graph = self._build_network_graph(nodes, connections)

            # Assess risk for all nodes
            risk_assessments = self._assess_network_risks(nodes, buffer_km, lookback_years)

            # Update nodes with risk data
            for node in nodes:
                node.risk_assessment = risk_assessments.get(node.id)

            # Analyze network topology
            topology_analysis = self._analyze_network_topology(network_graph, nodes)

            # Identify risk hotspots
            risk_hotspots = self._identify_risk_hotspots(nodes, network_graph)

            # Calculate network resilience
            resilience_metrics = self._calculate_network_resilience(network_graph, nodes)

            # Generate optimization recommendations
            optimizations = self._generate_network_optimizations(nodes, network_graph)

            analysis_result = {
                "network_overview": {
                    "total_nodes": len(nodes),
                    "total_connections": len(connections),
                    "node_types": self._categorize_nodes_by_type(nodes),
                    "geographic_spread": self._calculate_geographic_spread(nodes)
                },
                "risk_assessments": risk_assessments,
                "topology_analysis": topology_analysis,
                "risk_hotspots": risk_hotspots,
                "resilience_metrics": resilience_metrics,
                "optimizations": optimizations,
                "recommendations": self._generate_network_recommendations(
                    risk_hotspots, resilience_metrics, optimizations
                )
            }

            self.logger.info(f"Completed supply chain network analysis: {len(nodes)} nodes, {len(connections)} connections")
            return analysis_result

        except Exception as e:
            self.logger.error(f"Error analyzing supply chain network: {str(e)}")
            return {"error": str(e), "partial_results": {}}

    def optimize_supply_chain_routes(
        self,
        origin: SupplyChainNode,
        destination: SupplyChainNode,
        intermediate_nodes: list[SupplyChainNode],
        risk_tolerance: float = 0.3
    ) -> list[SupplyChainPath]:
        """
        Find optimal supply chain routes considering geospatial risks.

        Args:
            origin: Starting node
            destination: Ending node
            intermediate_nodes: Possible intermediate nodes
            risk_tolerance: Maximum acceptable risk score (0-1)

        Returns:
            List of optimized paths ranked by risk and efficiency
        """
        try:
            all_nodes = [origin] + intermediate_nodes + [destination]

            # Assess risks for all nodes if not already done
            for node in all_nodes:
                if not node.risk_assessment:
                    node.risk_assessment = self.risk_assessor.assess_location_risk(
                        node.latitude, node.longitude
                    )

            # Generate possible paths
            paths = self._generate_possible_paths(origin, destination, intermediate_nodes)

            # Evaluate each path
            evaluated_paths = []
            for path_nodes in paths:
                path_analysis = self._evaluate_supply_path(path_nodes, risk_tolerance)
                if path_analysis:
                    evaluated_paths.append(path_analysis)

            # Rank paths by combined score (risk + efficiency)
            ranked_paths = sorted(evaluated_paths, key=lambda x: x.total_risk_score)

            self.logger.info(f"Generated {len(ranked_paths)} optimized supply chain routes")
            return ranked_paths[:10]  # Return top 10 paths

        except Exception as e:
            self.logger.error(f"Error optimizing supply chain routes: {str(e)}")
            return []

    def identify_alternative_suppliers(
        self,
        target_location: tuple[float, float],
        search_radius_km: float = 500,
        max_alternatives: int = 5,
        risk_threshold: float = 0.3
    ) -> list[dict[str, Any]]:
        """
        Identify alternative suppliers in low-risk areas.

        Args:
            target_location: (latitude, longitude) of target area
            search_radius_km: Search radius in kilometers
            max_alternatives: Maximum number of alternatives to return
            risk_threshold: Maximum acceptable risk score

        Returns:
            List of alternative supplier locations with risk assessments
        """
        try:
            # Generate candidate locations in a grid pattern
            candidates = self._generate_candidate_locations(target_location, search_radius_km)

            alternatives = []
            for lat, lon in candidates:
                assessment = self.risk_assessor.assess_location_risk(lat, lon)

                if assessment.combined_risk_score <= risk_threshold:
                    distance = self._calculate_distance(target_location, (lat, lon))

                    alternative = {
                        "coordinates": (lat, lon),
                        "distance_km": distance,
                        "risk_score": assessment.combined_risk_score,
                        "risk_level": assessment.risk_level,
                        "forest_cover_percentage": assessment.forest_cover_percentage,
                        "recent_deforestation_alerts": assessment.alerts_count,
                        "recommendations": assessment.recommendations
                    }
                    alternatives.append(alternative)

            # Sort by distance and risk
            alternatives.sort(key=lambda x: (x["distance_km"], x["risk_score"]))

            self.logger.info(f"Identified {len(alternatives)} alternative suppliers within {search_radius_km}km")
            return alternatives[:max_alternatives]

        except Exception as e:
            self.logger.error(f"Error identifying alternative suppliers: {str(e)}")
            return []

    def _build_network_graph(
        self,
        nodes: list[SupplyChainNode],
        connections: list[tuple[str, str]]
    ) -> nx.DiGraph:
        """Build NetworkX graph from supply chain data."""
        graph = nx.DiGraph()

        # Add nodes
        for node in nodes:
            graph.add_node(
                node.id,
                name=node.name,
                type=node.node_type,
                latitude=node.latitude,
                longitude=node.longitude,
                risk_score=node.risk_assessment.combined_risk_score if node.risk_assessment else 0.5
            )

        # Add edges
        for from_id, to_id in connections:
            # Calculate distance and risk for edge
            from_node = next(n for n in nodes if n.id == from_id)
            to_node = next(n for n in nodes if n.id == to_id)

            distance = self._calculate_distance(
                (from_node.latitude, from_node.longitude),
                (to_node.latitude, to_node.longitude)
            )

            # Edge weight combines distance and risk
            from_risk = from_node.risk_assessment.combined_risk_score if from_node.risk_assessment else 0.5
            to_risk = to_node.risk_assessment.combined_risk_score if to_node.risk_assessment else 0.5
            avg_risk = (from_risk + to_risk) / 2

            weight = distance * (1 + avg_risk)  # Penalize high-risk connections

            graph.add_edge(from_id, to_id, weight=weight, distance=distance, risk=avg_risk)

        return graph

    def _assess_network_risks(
        self,
        nodes: list[SupplyChainNode],
        buffer_km: float,
        lookback_years: int
    ) -> dict[str, LocationRiskAssessment]:
        """Assess risks for all nodes in the network."""
        assessments = {}

        for node in nodes:
            try:
                assessment = self.risk_assessor.assess_location_risk(
                    node.latitude, node.longitude, buffer_km, lookback_years
                )
                assessments[node.id] = assessment
            except Exception as e:
                self.logger.warning(f"Failed to assess risk for node {node.id}: {str(e)}")
                # Create default assessment
                assessments[node.id] = LocationRiskAssessment(
                    coordinates=(node.latitude, node.longitude),
                    gfw_risk_score=0.5,
                    corine_risk_score=0.5,
                    combined_risk_score=0.5,
                    risk_level="medium",
                    risk_factors={},
                    alerts_count=0,
                    recent_deforestation_ha=0,
                    forest_cover_percentage=50,
                    land_use_risk=0.5,
                    recommendations=["Unable to complete risk assessment"]
                )

        return assessments

    def _analyze_network_topology(
        self,
        graph: nx.DiGraph,
        nodes: list[SupplyChainNode]
    ) -> dict[str, Any]:
        """Analyze the topological properties of the supply chain network."""
        try:
            # Basic network metrics
            num_nodes = graph.number_of_nodes()
            graph.number_of_edges()

            # Connectivity analysis
            is_connected = nx.is_weakly_connected(graph)
            connected_components = list(nx.weakly_connected_components(graph))

            # Centrality measures
            betweenness = nx.betweenness_centrality(graph, weight="weight")
            nx.degree_centrality(graph)

            # Risk distribution
            risk_scores = [n.risk_assessment.combined_risk_score for n in nodes if n.risk_assessment]
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

            # Critical nodes (high betweenness + high risk)
            critical_nodes = []
            for node_id, betweenness_score in betweenness.items():
                node = next(n for n in nodes if n.id == node_id)
                risk_score = node.risk_assessment.combined_risk_score if node.risk_assessment else 0
                criticality = betweenness_score * risk_score
                if criticality > 0.1:  # Threshold for criticality
                    critical_nodes.append({
                        "node_id": node_id,
                        "name": node.name,
                        "betweenness": betweenness_score,
                        "risk_score": risk_score,
                        "criticality": criticality
                    })

            return {
                "is_connected": is_connected,
                "connected_components": len(connected_components),
                "average_degree": sum(dict(graph.degree()).values()) / num_nodes if num_nodes > 0 else 0,
                "average_risk_score": avg_risk,
                "critical_nodes": sorted(critical_nodes, key=lambda x: x["criticality"], reverse=True),
                "network_density": nx.density(graph),
                "average_clustering": nx.average_clustering(graph.to_undirected())
            }

        except Exception as e:
            self.logger.error(f"Error analyzing network topology: {str(e)}")
            return {"error": str(e)}

    def _identify_risk_hotspots(
        self,
        nodes: list[SupplyChainNode],
        graph: nx.DiGraph
    ) -> list[dict[str, Any]]:
        """Identify geographic and network risk hotspots."""
        hotspots = []

        # Geographic clustering of high-risk nodes
        high_risk_nodes = [n for n in nodes if n.risk_assessment and n.risk_assessment.risk_level == "high"]

        if len(high_risk_nodes) >= 2:
            # Calculate distances between high-risk nodes
            distances = []
            for i, node1 in enumerate(high_risk_nodes):
                for node2 in high_risk_nodes[i+1:]:
                    dist = self._calculate_distance(
                        (node1.latitude, node1.longitude),
                        (node2.latitude, node2.longitude)
                    )
                    distances.append(dist)

            avg_distance = sum(distances) / len(distances) if distances else 0

            if avg_distance < 500:  # Within 500km
                hotspots.append({
                    "type": "geographic_cluster",
                    "description": f"Cluster of {len(high_risk_nodes)} high-risk nodes within {avg_distance:.1f}km average distance",
                    "nodes": [n.id for n in high_risk_nodes],
                    "severity": "high" if len(high_risk_nodes) > 3 else "medium"
                })

        # Network bottlenecks
        betweenness = nx.betweenness_centrality(graph, weight="weight")
        bottleneck_nodes = [
            node_id for node_id, score in betweenness.items()
            if score > 0.1  # High betweenness
        ]

        if bottleneck_nodes:
            hotspots.append({
                "type": "network_bottleneck",
                "description": f"{len(bottleneck_nodes)} critical network bottlenecks identified",
                "nodes": bottleneck_nodes,
                "severity": "medium"
            })

        return hotspots

    def _calculate_network_resilience(
        self,
        graph: nx.DiGraph,
        nodes: list[SupplyChainNode]
    ) -> dict[str, Any]:
        """Calculate network resilience metrics."""
        try:
            # Remove high-risk nodes and measure impact
            high_risk_nodes = [
                n.id for n in nodes
                if n.risk_assessment and n.risk_assessment.risk_level == "high"
            ]

            original_components = len(list(nx.weakly_connected_components(graph)))

            # Simulate removing high-risk nodes
            graph_without_high_risk = graph.copy()
            graph_without_high_risk.remove_nodes_from(high_risk_nodes)

            remaining_components = len(list(nx.weakly_connected_components(graph_without_high_risk)))
            remaining_nodes = graph_without_high_risk.number_of_nodes()

            fragmentation_risk = remaining_components - original_components
            node_loss_percentage = len(high_risk_nodes) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0

            # Calculate alternative path availability
            alternative_paths = 0
            total_possible_paths = 0

            for source in graph.nodes():
                for target in graph.nodes():
                    if source != target:
                        total_possible_paths += 1
                        try:
                            paths = list(nx.all_simple_paths(graph, source, target, cutoff=5))
                            if len(paths) > 1:
                                alternative_paths += 1
                        except:
                            pass

            path_resilience = alternative_paths / total_possible_paths if total_possible_paths > 0 else 0

            return {
                "fragmentation_risk": fragmentation_risk,
                "node_loss_impact": node_loss_percentage,
                "remaining_nodes_percentage": remaining_nodes / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
                "path_resilience": path_resilience,
                "vulnerability_score": (fragmentation_risk * 0.4) + (node_loss_percentage * 0.6)
            }

        except Exception as e:
            self.logger.error(f"Error calculating network resilience: {str(e)}")
            return {"error": str(e)}

    def _generate_network_optimizations(
        self,
        nodes: list[SupplyChainNode],
        graph: nx.DiGraph
    ) -> GeospatialOptimization:
        """Generate optimization recommendations for the network."""
        try:
            # Identify high-risk segments
            high_risk_segments = []
            for edge in graph.edges(data=True):
                from_node = next(n for n in nodes if n.id == edge[0])
                to_node = next(n for n in nodes if n.id == edge[1])

                from_risk = from_node.risk_assessment.combined_risk_score if from_node.risk_assessment else 0
                to_risk = to_node.risk_assessment.combined_risk_score if to_node.risk_assessment else 0

                avg_risk = (from_risk + to_risk) / 2
                if avg_risk > 0.6:
                    high_risk_segments.append({
                        "from_node": edge[0],
                        "to_node": edge[1],
                        "risk_score": avg_risk,
                        "distance": edge[2]["distance"]
                    })

            # Find alternative routes for high-risk paths
            alternative_routes = []
            for segment in high_risk_segments[:3]:  # Limit to top 3
                try:
                    paths = list(nx.all_simple_paths(
                        graph, segment["from_node"], segment["to_node"],
                        cutoff=4  # Limit path length
                    ))

                    if len(paths) > 1:
                        # Evaluate alternative paths
                        path_options = []
                        for path in paths[1:]:  # Skip the original path
                            path_risk = self._calculate_path_risk(path, nodes)
                            path_distance = self._calculate_path_distance(path, graph)
                            path_options.append(SupplyChainPath(
                                nodes=[next(n for n in nodes if n.id == node_id) for node_id in path],
                                total_distance_km=path_distance,
                                total_risk_score=path_risk,
                                deforestation_exposure=path_risk,  # Simplified
                                alternative_paths=[]
                            ))

                        alternative_routes.extend(path_options[:2])  # Top 2 alternatives

                except Exception as e:
                    self.logger.warning(f"Error finding alternatives for segment {segment}: {str(e)}")

            # Calculate potential risk reduction
            sum(
                n.risk_assessment.combined_risk_score for n in nodes
                if n.risk_assessment
            )
            potential_risk_reduction = len(high_risk_segments) * 0.3  # Estimate

            return GeospatialOptimization(
                high_risk_segments=high_risk_segments,
                alternative_routes=alternative_routes,
                risk_reduction_potential=potential_risk_reduction,
                cost_benefit_analysis={
                    "estimated_risk_reduction": potential_risk_reduction,
                    "high_risk_segments_count": len(high_risk_segments),
                    "alternative_routes_available": len(alternative_routes)
                }
            )

        except Exception as e:
            self.logger.error(f"Error generating network optimizations: {str(e)}")
            return GeospatialOptimization([], [], 0, {"error": str(e)})

    def _generate_possible_paths(
        self,
        origin: SupplyChainNode,
        destination: SupplyChainNode,
        intermediates: list[SupplyChainNode]
    ) -> list[list[SupplyChainNode]]:
        """Generate possible paths through the supply chain."""
        # Simple implementation - in practice, this would use more sophisticated routing
        paths = []

        # Direct path
        paths.append([origin, destination])

        # Paths through one intermediate
        for intermediate in intermediates:
            paths.append([origin, intermediate, destination])

        # Paths through two intermediates
        for i, inter1 in enumerate(intermediates):
            for inter2 in intermediates[i+1:]:
                paths.append([origin, inter1, inter2, destination])

        return paths

    def _evaluate_supply_path(
        self,
        path_nodes: list[SupplyChainNode],
        risk_tolerance: float
    ) -> SupplyChainPath | None:
        """Evaluate a supply chain path."""
        try:
            if not all(node.risk_assessment for node in path_nodes):
                return None

            # Calculate total metrics
            total_distance = 0
            total_risk = 0

            for i in range(len(path_nodes) - 1):
                current = path_nodes[i]
                next_node = path_nodes[i+1]

                # Calculate distance
                distance = self._calculate_distance(
                    (current.latitude, current.longitude),
                    (next_node.latitude, next_node.longitude)
                )
                total_distance += distance

                # Accumulate risk
                segment_risk = (current.risk_assessment.combined_risk_score +
                              next_node.risk_assessment.combined_risk_score) / 2
                total_risk += segment_risk * distance  # Weight by distance

            avg_risk = total_risk / total_distance if total_distance > 0 else 0

            if avg_risk > risk_tolerance:
                return None  # Path exceeds risk tolerance

            return SupplyChainPath(
                nodes=path_nodes,
                total_distance_km=total_distance,
                total_risk_score=avg_risk,
                deforestation_exposure=avg_risk,  # Simplified
                alternative_paths=[]
            )

        except Exception as e:
            self.logger.warning(f"Error evaluating path: {str(e)}")
            return None

    def _generate_candidate_locations(
        self,
        center: tuple[float, float],
        radius_km: float,
        grid_spacing_km: float = 50
    ) -> list[tuple[float, float]]:
        """Generate candidate locations in a grid pattern."""
        candidates = []

        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.0
        spacing_deg = grid_spacing_km / 111.0

        center_lat, center_lon = center

        # Generate grid
        lat_steps = int(radius_deg / spacing_deg)
        lon_steps = int(radius_deg / spacing_deg)

        for i in range(-lat_steps, lat_steps + 1):
            for j in range(-lon_steps, lon_steps + 1):
                lat = center_lat + i * spacing_deg
                lon = center_lon + j * spacing_deg

                # Check if within radius
                distance = self._calculate_distance(center, (lat, lon))
                if distance <= radius_km:
                    candidates.append((lat, lon))

        return candidates

    def _calculate_distance(self, point1: tuple[float, float], point2: tuple[float, float]) -> float:
        """Calculate distance between two points in kilometers."""
        return self._haversine_distance(point1[0], point1[1], point2[0], point2[1])

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance."""
        import math

        R = 6371  # Earth's radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def _categorize_nodes_by_type(self, nodes: list[SupplyChainNode]) -> dict[str, int]:
        """Categorize nodes by type."""
        categories = {}
        for node in nodes:
            categories[node.node_type] = categories.get(node.node_type, 0) + 1
        return categories

    def _calculate_geographic_spread(self, nodes: list[SupplyChainNode]) -> dict[str, Any]:
        """Calculate geographic spread of nodes."""
        if not nodes:
            return {}

        lats = [n.latitude for n in nodes]
        lons = [n.longitude for n in nodes]

        return {
            "latitude_range": max(lats) - min(lats),
            "longitude_range": max(lons) - min(lons),
            "center_lat": sum(lats) / len(lats),
            "center_lon": sum(lons) / len(lons)
        }

    def _calculate_path_risk(self, path: list[str], nodes: list[SupplyChainNode]) -> float:
        """Calculate risk score for a path."""
        path_nodes = [next(n for n in nodes if n.id == node_id) for node_id in path]
        risks = [n.risk_assessment.combined_risk_score for n in path_nodes if n.risk_assessment]
        return sum(risks) / len(risks) if risks else 0.5

    def _calculate_path_distance(self, path: list[str], graph: nx.DiGraph) -> float:
        """Calculate total distance for a path."""
        total_distance = 0
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                total_distance += edge_data.get("distance", 0)
        return total_distance

    def _generate_network_recommendations(
        self,
        risk_hotspots: list[dict[str, Any]],
        resilience_metrics: dict[str, Any],
        optimizations: GeospatialOptimization
    ) -> list[str]:
        """Generate recommendations for the supply chain network."""
        recommendations = []

        # Risk hotspot recommendations
        for hotspot in risk_hotspots:
            if hotspot["type"] == "geographic_cluster":
                recommendations.append(
                    f"Address geographic risk cluster: Consider diversifying suppliers outside the {hotspot['description'].split()[-2]}km radius"
                )
            elif hotspot["type"] == "network_bottleneck":
                recommendations.append(
                    f"Strengthen network resilience: Develop backup suppliers for {len(hotspot['nodes'])} critical nodes"
                )

        # Resilience recommendations
        vulnerability = resilience_metrics.get("vulnerability_score", 0)
        if vulnerability > 0.3:
            recommendations.append(
                "Improve network resilience: High vulnerability to node failures detected"
            )

        # Optimization recommendations
        if optimizations.high_risk_segments:
            recommendations.append(
                f"Optimize high-risk segments: {len(optimizations.high_risk_segments)} segments identified for rerouting"
            )

        if optimizations.alternative_routes:
            recommendations.append(
                f"Alternative routes available: {len(optimizations.alternative_routes)} lower-risk options identified"
            )

        return recommendations
