"""
Geospatial risk assessment engine for EUDR compliance.

This module combines GFW and CORINE data to assess deforestation risk
and provide comprehensive geospatial analysis for supply chain screening.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from shapely.geometry import Point, Polygon

from .corine_client import CORINEClient
from .gfw_client import DeforestationAlert, GFWClient, TreeCoverLoss


@dataclass
class LocationRiskAssessment:
    """Comprehensive risk assessment for a location."""
    coordinates: tuple[float, float]
    gfw_risk_score: float
    corine_risk_score: float
    combined_risk_score: float
    risk_level: str
    risk_factors: dict[str, Any]
    alerts_count: int
    recent_deforestation_ha: float
    forest_cover_percentage: float
    land_use_risk: float
    recommendations: list[str]


@dataclass
class SupplyChainRiskProfile:
    """Risk profile for an entire supply chain."""
    total_locations: int
    high_risk_locations: int
    medium_risk_locations: int
    low_risk_locations: int
    overall_risk_score: float
    risk_distribution: dict[str, int]
    critical_risk_factors: list[dict[str, Any]]
    mitigation_priorities: list[str]


class GeospatialRiskAssessor:
    """
    Engine for assessing geospatial risks using GFW and CORINE data.

    Combines deforestation alerts, tree cover loss, and land use data
    to provide comprehensive risk assessments for EUDR compliance.
    """

    def __init__(self, gfw_api_key: str | None = None, corine_api_key: str | None = None):
        """
        Initialize the geospatial risk assessor.

        Args:
            gfw_api_key: Optional API key for GFW
            corine_api_key: Optional API key for CORINE/Copernicus
        """
        self.gfw_client = GFWClient(gfw_api_key)
        self.corine_client = CORINEClient(corine_api_key)
        self.logger = logging.getLogger(__name__)

    def assess_location_risk(
        self,
        latitude: float,
        longitude: float,
        buffer_km: float = 50,
        lookback_years: int = 5
    ) -> LocationRiskAssessment:
        """
        Assess deforestation risk for a specific location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            buffer_km: Analysis buffer in kilometers
            lookback_years: Years to look back for historical data

        Returns:
            Comprehensive risk assessment
        """
        try:
            # Create analysis geometry
            point = Point(longitude, latitude)
            buffer_geom = self._create_buffer(point, buffer_km)

            # Get GFW data
            gfw_results = self._assess_gfw_risk(buffer_geom, lookback_years)

            # Get CORINE data
            corine_results = self._assess_corine_risk(buffer_geom)

            # Combine assessments
            combined_score = self._combine_risk_scores(
                gfw_results["risk_score"],
                corine_results["risk_score"]
            )

            risk_factors = self._identify_risk_factors(gfw_results, corine_results)
            recommendations = self._generate_recommendations(combined_score, risk_factors)

            assessment = LocationRiskAssessment(
                coordinates=(latitude, longitude),
                gfw_risk_score=gfw_results["risk_score"],
                corine_risk_score=corine_results["risk_score"],
                combined_risk_score=combined_score,
                risk_level=self._categorize_risk(combined_score),
                risk_factors=risk_factors,
                alerts_count=gfw_results.get("alerts_count", 0),
                recent_deforestation_ha=gfw_results.get("total_alert_area_ha", 0),
                forest_cover_percentage=corine_results.get("forest_percentage", 0),
                land_use_risk=corine_results.get("risk_score", 0),
                recommendations=recommendations
            )

            self.logger.info(f"Completed risk assessment for {latitude},{longitude}: {assessment.risk_level} risk")
            return assessment

        except Exception as e:
            self.logger.error(f"Error assessing location risk: {str(e)}")
            return LocationRiskAssessment(
                coordinates=(latitude, longitude),
                gfw_risk_score=1.0,
                corine_risk_score=1.0,
                combined_risk_score=1.0,
                risk_level="unknown",
                risk_factors={"error": str(e)},
                alerts_count=0,
                recent_deforestation_ha=0,
                forest_cover_percentage=0,
                land_use_risk=1.0,
                recommendations=["Unable to complete assessment due to error"]
            )

    def assess_supply_chain_risk(
        self,
        locations: list[tuple[float, float]],
        buffer_km: float = 50,
        lookback_years: int = 5
    ) -> SupplyChainRiskProfile:
        """
        Assess risk across an entire supply chain.

        Args:
            locations: List of (latitude, longitude) tuples
            buffer_km: Analysis buffer in kilometers
            lookback_years: Years to look back for historical data

        Returns:
            Supply chain risk profile
        """
        try:
            assessments = []
            for lat, lon in locations:
                assessment = self.assess_location_risk(lat, lon, buffer_km, lookback_years)
                assessments.append(assessment)

            # Calculate aggregate statistics
            risk_levels = [a.risk_level for a in assessments]
            high_risk = risk_levels.count("high")
            medium_risk = risk_levels.count("medium")
            low_risk = risk_levels.count("low")

            # Calculate overall risk score
            risk_scores = [a.combined_risk_score for a in assessments]
            overall_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0

            # Identify critical risk factors
            critical_factors = self._identify_critical_supply_chain_risks(assessments)

            # Generate mitigation priorities
            mitigation_priorities = self._prioritize_mitigations(assessments)

            profile = SupplyChainRiskProfile(
                total_locations=len(locations),
                high_risk_locations=high_risk,
                medium_risk_locations=medium_risk,
                low_risk_locations=low_risk,
                overall_risk_score=overall_score,
                risk_distribution={
                    "high": high_risk,
                    "medium": medium_risk,
                    "low": low_risk,
                    "unknown": risk_levels.count("unknown")
                },
                critical_risk_factors=critical_factors,
                mitigation_priorities=mitigation_priorities
            )

            self.logger.info(f"Completed supply chain assessment: {len(locations)} locations, overall risk: {profile.overall_risk_score:.2f}")
            return profile

        except Exception as e:
            self.logger.error(f"Error assessing supply chain risk: {str(e)}")
            return SupplyChainRiskProfile(
                total_locations=len(locations),
                high_risk_locations=0,
                medium_risk_locations=0,
                low_risk_locations=0,
                overall_risk_score=1.0,
                risk_distribution={"unknown": len(locations)},
                critical_risk_factors=[{"type": "error", "description": str(e)}],
                mitigation_priorities=["Unable to complete assessment"]
            )

    def _assess_gfw_risk(self, geometry: Polygon, lookback_years: int) -> dict[str, Any]:
        """Assess risk using GFW data."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_years * 365)

            # Get deforestation alerts
            alerts = self.gfw_client.get_deforestation_alerts(geometry, start_date, end_date)

            # Get tree cover loss
            current_year = datetime.now().year
            start_year = max(2001, current_year - lookback_years)
            losses = self.gfw_client.get_tree_cover_loss(geometry, start_year, current_year)

            # Calculate risk score
            risk_score = self._calculate_gfw_risk_score(alerts, losses, geometry.area)

            return {
                "risk_score": risk_score,
                "alerts_count": len(alerts),
                "total_alert_area_ha": sum(alert.area_ha for alert in alerts),
                "losses_count": len(losses),
                "total_loss_area_ha": sum(loss.area_ha for loss in losses),
                "recent_alerts": len([a for a in alerts if (end_date - a.date).days <= 365])
            }

        except Exception as e:
            self.logger.warning(f"GFW assessment failed: {str(e)}")
            return {"risk_score": 0.5, "error": str(e)}

    def _assess_corine_risk(self, geometry: Polygon) -> dict[str, Any]:
        """Assess risk using CORINE data."""
        try:
            # Get land cover analysis
            land_cover = self.corine_client.get_land_cover(geometry)

            if not land_cover:
                return {"risk_score": 0.5, "error": "No land cover data available"}

            # Assess deforestation risk
            risk_assessment = self.corine_client.assess_deforestation_risk(geometry)

            return {
                "risk_score": risk_assessment.get("risk_score", 0.5),
                "forest_percentage": risk_assessment.get("forest_percentage", 0),
                "development_percentage": risk_assessment.get("development_percentage", 0),
                "risk_factors": risk_assessment.get("risk_factors", {})
            }

        except Exception as e:
            self.logger.warning(f"CORINE assessment failed: {str(e)}")
            return {"risk_score": 0.5, "error": str(e)}

    def _combine_risk_scores(self, gfw_score: float, corine_score: float) -> float:
        """Combine GFW and CORINE risk scores."""
        # Weight GFW more heavily for recent deforestation activity
        # Weight CORINE for land use context
        gfw_weight = 0.7
        corine_weight = 0.3

        combined = (gfw_score * gfw_weight) + (corine_score * corine_weight)
        return min(1.0, combined)

    def _identify_risk_factors(self, gfw_results: dict, corine_results: dict) -> dict[str, Any]:
        """Identify specific risk factors from assessment results."""
        factors = {}

        # GFW-based factors
        if gfw_results.get("alerts_count", 0) > 0:
            factors["recent_deforestation"] = {
                "alerts": gfw_results["alerts_count"],
                "area_ha": gfw_results.get("total_alert_area_ha", 0),
                "severity": "high" if gfw_results["alerts_count"] > 5 else "medium"
            }

        if gfw_results.get("losses_count", 0) > 0:
            factors["historical_loss"] = {
                "losses": gfw_results["losses_count"],
                "area_ha": gfw_results.get("total_loss_area_ha", 0),
                "severity": "medium"
            }

        # CORINE-based factors
        forest_pct = corine_results.get("forest_percentage", 0)
        if forest_pct < 30:
            factors["low_forest_cover"] = {
                "percentage": forest_pct,
                "severity": "high" if forest_pct < 10 else "medium"
            }

        dev_pct = corine_results.get("development_percentage", 0)
        if dev_pct > 40:
            factors["high_development"] = {
                "percentage": dev_pct,
                "severity": "high" if dev_pct > 60 else "medium"
            }

        return factors

    def _generate_recommendations(self, risk_score: float, risk_factors: dict) -> list[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if risk_score >= 0.7:
            recommendations.append("URGENT: Immediate supply chain audit required")
            recommendations.append("Consider alternative sourcing from low-risk regions")
            recommendations.append("Implement enhanced monitoring and verification")

        elif risk_score >= 0.4:
            recommendations.append("Conduct detailed risk assessment of suppliers")
            recommendations.append("Implement supplier verification program")
            recommendations.append("Monitor deforestation alerts in the region")

        else:
            recommendations.append("Continue standard supplier monitoring")
            recommendations.append("Maintain documentation of low-risk sourcing")

        # Factor-specific recommendations
        if "recent_deforestation" in risk_factors:
            recommendations.append("Verify supplier sustainability certifications")
            recommendations.append("Request recent geolocation data from suppliers")

        if "low_forest_cover" in risk_factors:
            recommendations.append("Assess alternative sourcing options")
            recommendations.append("Implement forest conservation requirements in contracts")

        return recommendations

    def _identify_critical_supply_chain_risks(self, assessments: list[LocationRiskAssessment]) -> list[dict[str, Any]]:
        """Identify critical risks across the supply chain."""
        critical_factors = []

        # High-risk locations
        high_risk_locs = [a for a in assessments if a.risk_level == "high"]
        if high_risk_locs:
            critical_factors.append({
                "type": "high_risk_locations",
                "severity": "high",
                "description": f"{len(high_risk_locs)} locations with high deforestation risk",
                "affected_locations": len(high_risk_locs)
            })

        # Recent deforestation activity
        total_alerts = sum(a.alerts_count for a in assessments)
        if total_alerts > 10:
            critical_factors.append({
                "type": "widespread_deforestation",
                "severity": "high",
                "description": f"{total_alerts} deforestation alerts across supply chain",
                "total_alerts": total_alerts
            })

        # Low forest cover areas
        low_forest = [a for a in assessments if a.forest_cover_percentage < 20]
        if low_forest:
            critical_factors.append({
                "type": "deforestation_vulnerable_areas",
                "severity": "medium",
                "description": f"{len(low_forest)} locations in low forest cover areas",
                "affected_locations": len(low_forest)
            })

        return critical_factors

    def _prioritize_mitigations(self, assessments: list[LocationRiskAssessment]) -> list[str]:
        """Prioritize mitigation actions for the supply chain."""
        priorities = []

        high_risk_count = sum(1 for a in assessments if a.risk_level == "high")
        if high_risk_count > 0:
            priorities.append(f"Address {high_risk_count} high-risk locations immediately")

        total_alerts = sum(a.alerts_count for a in assessments)
        if total_alerts > 0:
            priorities.append("Implement real-time deforestation monitoring")

        low_forest_count = sum(1 for a in assessments if a.forest_cover_percentage < 30)
        if low_forest_count > 0:
            priorities.append(f"Develop contingency plans for {low_forest_count} vulnerable locations")

        priorities.append("Establish supplier geolocation verification process")
        priorities.append("Create deforestation risk assessment framework")

        return priorities

    def _calculate_gfw_risk_score(self, alerts: list[DeforestationAlert], losses: list[TreeCoverLoss], area_sq_degrees: float) -> float:
        """Calculate risk score from GFW data."""
        if not alerts and not losses:
            return 0.0

        # Convert area to approximate hectares (rough approximation)
        area_ha = area_sq_degrees * 111 * 111

        # Alert-based risk
        alert_density = len(alerts) / area_ha if area_ha > 0 else 0
        alert_area_ratio = sum(a.area_ha for a in alerts) / area_ha if area_ha > 0 else 0

        alert_score = min(1.0, (alert_density * 1000) + (alert_area_ratio * 10))

        # Loss-based risk
        loss_density = len(losses) / area_ha if area_ha > 0 else 0
        loss_area_ratio = sum(l.area_ha for l in losses) / area_ha if area_ha > 0 else 0

        loss_score = min(1.0, (loss_density * 500) + (loss_area_ratio * 5))

        # Combine with recency weighting
        recent_alerts = [a for a in alerts if (datetime.now() - a.date).days <= 365]
        recency_factor = len(recent_alerts) / len(alerts) if alerts else 0

        combined_score = (alert_score * 0.6) + (loss_score * 0.3) + (recency_factor * 0.1)
        return min(1.0, combined_score)

    def _create_buffer(self, point: Point, buffer_km: float) -> Polygon:
        """Create a buffer around a point."""
        buffer_degrees = buffer_km / 111.0
        return point.buffer(buffer_degrees)

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
