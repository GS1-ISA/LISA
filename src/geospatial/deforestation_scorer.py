"""
Deforestation risk scoring algorithm for EUDR compliance.

This module implements specialized algorithms for calculating deforestation risk
scores based on GFW and CORINE data, incorporating temporal, spatial, and
supply chain factors.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

from .gfw_client import DeforestationAlert, TreeCoverLoss
from .corine_client import LandCoverChange


@dataclass
class RiskScoreComponents:
    """Components that contribute to the final risk score."""
    temporal_risk: float  # Based on timing of deforestation events
    spatial_risk: float   # Based on proximity and clustering
    intensity_risk: float # Based on scale and frequency
    contextual_risk: float # Based on land use and environmental factors
    supply_chain_risk: float # Based on supply chain position and volume


@dataclass
class DeforestationRiskScore:
    """Comprehensive deforestation risk score."""
    overall_score: float
    risk_level: str
    components: RiskScoreComponents
    confidence: float
    factors: List[Dict[str, Any]]
    recommendations: List[str]


class DeforestationRiskScorer:
    """
    Advanced algorithm for scoring deforestation risk.

    Implements multi-factor risk scoring that considers temporal patterns,
    spatial distribution, deforestation intensity, and contextual factors.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Risk thresholds
        self.HIGH_RISK_THRESHOLD = 0.7
        self.MEDIUM_RISK_THRESHOLD = 0.3

        # Scoring weights
        self.WEIGHTS = {
            'temporal': 0.25,
            'spatial': 0.20,
            'intensity': 0.30,
            'contextual': 0.15,
            'supply_chain': 0.10
        }

    def calculate_risk_score(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        land_cover_changes: List[LandCoverChange],
        location_context: Dict[str, Any],
        supply_chain_data: Optional[Dict[str, Any]] = None
    ) -> DeforestationRiskScore:
        """
        Calculate comprehensive deforestation risk score.

        Args:
            alerts: List of deforestation alerts
            losses: List of tree cover losses
            land_cover_changes: List of land cover changes
            location_context: Contextual information about the location
            supply_chain_data: Supply chain position and volume data

        Returns:
            Comprehensive risk score with components and recommendations
        """
        try:
            # Calculate individual risk components
            temporal_risk = self._calculate_temporal_risk(alerts, losses)
            spatial_risk = self._calculate_spatial_risk(alerts, losses, location_context)
            intensity_risk = self._calculate_intensity_risk(alerts, losses, land_cover_changes)
            contextual_risk = self._calculate_contextual_risk(land_cover_changes, location_context)
            supply_chain_risk = self._calculate_supply_chain_risk(supply_chain_data)

            components = RiskScoreComponents(
                temporal_risk=temporal_risk,
                spatial_risk=spatial_risk,
                intensity_risk=intensity_risk,
                contextual_risk=contextual_risk,
                supply_chain_risk=supply_chain_risk
            )

            # Calculate overall score
            overall_score = self._combine_components(components)

            # Determine confidence based on data availability
            confidence = self._calculate_confidence(alerts, losses, land_cover_changes)

            # Identify key risk factors
            factors = self._identify_risk_factors(components, alerts, losses, land_cover_changes)

            # Generate recommendations
            recommendations = self._generate_risk_recommendations(overall_score, factors)

            risk_level = self._categorize_risk_level(overall_score)

            score = DeforestationRiskScore(
                overall_score=overall_score,
                risk_level=risk_level,
                components=components,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations
            )

            self.logger.info(f"Calculated risk score: {overall_score:.3f} ({risk_level}) with {confidence:.1%} confidence")
            return score

        except Exception as e:
            self.logger.error(f"Error calculating risk score: {str(e)}")
            return DeforestationRiskScore(
                overall_score=0.5,
                risk_level="unknown",
                components=RiskScoreComponents(0.5, 0.5, 0.5, 0.5, 0.5),
                confidence=0.0,
                factors=[{"type": "error", "description": str(e)}],
                recommendations=["Unable to calculate risk score due to error"]
            )

    def _calculate_temporal_risk(self, alerts: List[DeforestationAlert], losses: List[TreeCoverLoss]) -> float:
        """Calculate risk based on temporal patterns of deforestation."""
        if not alerts and not losses:
            return 0.0

        now = datetime.now()

        # Analyze alert recency
        recent_alerts = []
        for alert in alerts:
            days_since = (now - alert.date).days
            if days_since <= 365:  # Last year
                recent_alerts.append((alert, days_since))

        # Analyze loss recency
        recent_losses = []
        for loss in losses:
            years_since = now.year - loss.loss_year
            if years_since <= 2:  # Last 2 years
                recent_losses.append((loss, years_since))

        # Calculate recency score
        alert_recency_score = 0.0
        if recent_alerts:
            avg_days = sum(days for _, days in recent_alerts) / len(recent_alerts)
            # More recent = higher risk (exponential decay)
            alert_recency_score = math.exp(-avg_days / 180)  # Half-life of 6 months

        loss_recency_score = 0.0
        if recent_losses:
            avg_years = sum(years for _, years in recent_losses) / len(recent_losses)
            loss_recency_score = math.exp(-avg_years / 1)  # Half-life of 1 year

        # Trend analysis - increasing activity
        trend_score = self._analyze_deforestation_trend(alerts, losses)

        # Combine temporal factors
        temporal_score = (
            alert_recency_score * 0.4 +
            loss_recency_score * 0.3 +
            trend_score * 0.3
        )

        return min(1.0, temporal_score)

    def _calculate_spatial_risk(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        location_context: Dict[str, Any]
    ) -> float:
        """Calculate risk based on spatial distribution and proximity."""
        if not alerts and not losses:
            return 0.0

        # Calculate clustering of alerts
        alert_locations = [(a.latitude, a.longitude) for a in alerts]
        alert_clustering = self._calculate_clustering(alert_locations)

        # Calculate clustering of losses
        loss_locations = [(l.latitude, l.longitude) for l in losses]
        loss_clustering = self._calculate_clustering(loss_locations)

        # Proximity to protected areas or high-value forests
        proximity_risk = self._calculate_proximity_risk(alerts, losses, location_context)

        # Spatial density
        area_km2 = location_context.get('area_km2', 100)  # Default 100 km²
        alert_density = len(alerts) / area_km2 if area_km2 > 0 else 0
        loss_density = len(losses) / area_km2 if area_km2 > 0 else 0

        density_score = min(1.0, (alert_density * 0.1) + (loss_density * 0.05))

        # Combine spatial factors
        spatial_score = (
            alert_clustering * 0.3 +
            loss_clustering * 0.2 +
            proximity_risk * 0.3 +
            density_score * 0.2
        )

        return min(1.0, spatial_score)

    def _calculate_intensity_risk(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        land_cover_changes: List[LandCoverChange]
    ) -> float:
        """Calculate risk based on scale and intensity of deforestation."""
        if not alerts and not losses and not land_cover_changes:
            return 0.0

        # Scale of individual events
        alert_scales = [a.area_ha for a in alerts]
        loss_scales = [l.area_ha for l in losses]
        change_scales = [c.area_ha for c in land_cover_changes]

        # Calculate intensity metrics
        avg_alert_size = sum(alert_scales) / len(alert_scales) if alert_scales else 0
        avg_loss_size = sum(loss_scales) / len(loss_scales) if loss_scales else 0
        avg_change_size = sum(change_scales) / len(change_scales) if change_scales else 0

        # Frequency of events
        total_events = len(alerts) + len(losses) + len(land_cover_changes)
        event_frequency = min(1.0, total_events / 50)  # Normalize to 50 events

        # Total area affected
        total_alert_area = sum(alert_scales)
        total_loss_area = sum(loss_scales)
        total_change_area = sum(change_scales)

        total_affected_area = total_alert_area + total_loss_area + total_change_area
        area_intensity = min(1.0, total_affected_area / 1000)  # Normalize to 1000 ha

        # Rate of change
        time_span_years = 5  # Assume 5-year analysis window
        annual_rate = total_affected_area / time_span_years if time_span_years > 0 else 0
        rate_score = min(1.0, annual_rate / 200)  # Normalize to 200 ha/year

        # Combine intensity factors
        intensity_score = (
            (avg_alert_size / 50) * 0.2 +  # Normalize to 50 ha
            (avg_loss_size / 25) * 0.2 +   # Normalize to 25 ha
            event_frequency * 0.2 +
            area_intensity * 0.2 +
            rate_score * 0.2
        )

        return min(1.0, intensity_score)

    def _calculate_contextual_risk(
        self,
        land_cover_changes: List[LandCoverChange],
        location_context: Dict[str, Any]
    ) -> float:
        """Calculate risk based on contextual and environmental factors."""
        contextual_score = 0.0

        # Land cover change types
        deforestation_changes = [c for c in land_cover_changes if c.change_type == 'deforestation']
        if land_cover_changes:
            deforestation_ratio = len(deforestation_changes) / len(land_cover_changes)
            contextual_score += deforestation_ratio * 0.4

        # Biodiversity and conservation factors
        conservation_status = location_context.get('conservation_status', 'unknown')
        if conservation_status == 'protected':
            contextual_score += 0.3
        elif conservation_status == 'high_value':
            contextual_score += 0.2

        # Soil and terrain factors
        terrain_risk = location_context.get('terrain_risk', 0.0)  # 0-1 scale
        soil_risk = location_context.get('soil_risk', 0.0)      # 0-1 scale

        contextual_score += terrain_risk * 0.15
        contextual_score += soil_risk * 0.15

        # Climate and weather factors
        climate_risk = location_context.get('climate_risk', 0.0)  # 0-1 scale
        contextual_score += climate_risk * 0.1

        return min(1.0, contextual_score)

    def _calculate_supply_chain_risk(self, supply_chain_data: Optional[Dict[str, Any]]) -> float:
        """Calculate risk based on supply chain position and volume."""
        if not supply_chain_data:
            return 0.0

        risk_score = 0.0

        # Supply chain position (upstream = higher risk)
        position = supply_chain_data.get('position', 'unknown')
        position_risks = {
            'upstream': 0.8,
            'midstream': 0.5,
            'downstream': 0.2
        }
        risk_score += position_risks.get(position, 0.5) * 0.4

        # Volume and scale
        volume = supply_chain_data.get('annual_volume_mt', 0)  # Metric tons
        volume_risk = min(1.0, volume / 10000)  # Normalize to 10,000 MT
        risk_score += volume_risk * 0.3

        # Number of suppliers
        supplier_count = supply_chain_data.get('supplier_count', 1)
        concentration_risk = 1.0 / math.log(supplier_count + 1) if supplier_count > 0 else 1.0
        risk_score += concentration_risk * 0.3

        return min(1.0, risk_score)

    def _combine_components(self, components: RiskScoreComponents) -> float:
        """Combine individual risk components into overall score."""
        overall = (
            components.temporal_risk * self.WEIGHTS['temporal'] +
            components.spatial_risk * self.WEIGHTS['spatial'] +
            components.intensity_risk * self.WEIGHTS['intensity'] +
            components.contextual_risk * self.WEIGHTS['contextual'] +
            components.supply_chain_risk * self.WEIGHTS['supply_chain']
        )

        return min(1.0, overall)

    def _calculate_confidence(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        land_cover_changes: List[LandCoverChange]
    ) -> float:
        """Calculate confidence in the risk score based on data availability."""
        data_points = len(alerts) + len(losses) + len(land_cover_changes)

        # Base confidence on data volume
        if data_points == 0:
            return 0.0
        elif data_points < 5:
            base_confidence = 0.3
        elif data_points < 20:
            base_confidence = 0.6
        else:
            base_confidence = 0.9

        # Adjust for data recency and quality
        now = datetime.now()
        recent_data = sum(1 for a in alerts if (now - a.date).days <= 365)
        recency_bonus = min(0.2, recent_data / 10)

        return min(1.0, base_confidence + recency_bonus)

    def _identify_risk_factors(
        self,
        components: RiskScoreComponents,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        land_cover_changes: List[LandCoverChange]
    ) -> List[Dict[str, Any]]:
        """Identify key factors contributing to risk."""
        factors = []

        # High temporal risk
        if components.temporal_risk > 0.7:
            factors.append({
                'type': 'recent_activity',
                'severity': 'high',
                'description': 'Recent deforestation activity detected',
                'component': 'temporal'
            })

        # High spatial risk
        if components.spatial_risk > 0.7:
            factors.append({
                'type': 'clustered_activity',
                'severity': 'high',
                'description': 'Clustered deforestation activity',
                'component': 'spatial'
            })

        # High intensity risk
        if components.intensity_risk > 0.7:
            factors.append({
                'type': 'intensive_activity',
                'severity': 'high',
                'description': 'High-intensity deforestation activity',
                'component': 'intensity'
            })

        # Contextual factors
        if components.contextual_risk > 0.6:
            factors.append({
                'type': 'environmental_context',
                'severity': 'medium',
                'description': 'High-risk environmental context',
                'component': 'contextual'
            })

        return factors

    def _generate_risk_recommendations(self, overall_score: float, factors: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on risk score and factors."""
        recommendations = []

        if overall_score >= self.HIGH_RISK_THRESHOLD:
            recommendations.extend([
                "URGENT: Immediate cessation of sourcing from this location",
                "Conduct emergency supplier audit",
                "Implement alternative sourcing strategy",
                "Notify regulatory authorities if required"
            ])

        elif overall_score >= self.MEDIUM_RISK_THRESHOLD:
            recommendations.extend([
                "Enhanced monitoring and verification required",
                "Implement supplier improvement plan",
                "Conduct detailed risk assessment",
                "Consider supply chain diversification"
            ])

        else:
            recommendations.extend([
                "Continue standard monitoring",
                "Maintain supplier verification processes",
                "Regular risk assessments recommended"
            ])

        # Factor-specific recommendations
        for factor in factors:
            if factor['type'] == 'recent_activity':
                recommendations.append("Implement real-time deforestation monitoring")
            elif factor['type'] == 'clustered_activity':
                recommendations.append("Assess spatial patterns and potential hotspots")
            elif factor['type'] == 'intensive_activity':
                recommendations.append("Evaluate scale and impact of activities")

        return recommendations

    def _analyze_deforestation_trend(self, alerts: List[DeforestationAlert], losses: List[TreeCoverLoss]) -> float:
        """Analyze trend in deforestation activity."""
        if not alerts and not losses:
            return 0.0

        # Simple trend analysis - check if activity is increasing
        now = datetime.now()

        # Group alerts by year
        alert_years = {}
        for alert in alerts:
            year = alert.date.year
            alert_years[year] = alert_years.get(year, 0) + 1

        # Group losses by year
        loss_years = {}
        for loss in losses:
            year = loss.loss_year
            loss_years[year] = loss_years.get(year, 0) + 1

        # Calculate trend (simplified linear trend)
        years = sorted(set(list(alert_years.keys()) + list(loss_years.keys())))
        if len(years) < 2:
            return 0.0

        # Simple slope calculation
        total_activity = [alert_years.get(y, 0) + loss_years.get(y, 0) for y in years]

        if len(total_activity) >= 2:
            # Calculate if activity is increasing
            recent_avg = sum(total_activity[-2:]) / 2
            earlier_avg = sum(total_activity[:-2]) / max(1, len(total_activity) - 2)

            if earlier_avg > 0:
                trend_ratio = recent_avg / earlier_avg
                trend_score = min(1.0, max(0.0, (trend_ratio - 0.8) / 0.4))  # Normalize around 1.0
                return trend_score

        return 0.0

    def _calculate_clustering(self, locations: List[Tuple[float, float]]) -> float:
        """Calculate clustering coefficient for locations."""
        if len(locations) < 2:
            return 0.0

        # Simple clustering based on average distance
        total_distance = 0.0
        count = 0

        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                distance = self._haversine_distance(loc1[0], loc1[1], loc2[0], loc2[1])
                total_distance += distance
                count += 1

        avg_distance = total_distance / count if count > 0 else 0

        # Lower average distance = higher clustering = higher risk
        # Normalize: < 1km = high clustering, > 50km = low clustering
        clustering_score = max(0.0, 1.0 - (avg_distance / 50.0))

        return clustering_score

    def _calculate_proximity_risk(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        location_context: Dict[str, Any]
    ) -> float:
        """Calculate risk based on proximity to sensitive areas."""
        proximity_score = 0.0

        # Check proximity to protected areas
        protected_distance = location_context.get('distance_to_protected_area_km', 100)
        if protected_distance < 10:
            proximity_score += 0.5
        elif protected_distance < 50:
            proximity_score += 0.3

        # Check proximity to indigenous lands
        indigenous_distance = location_context.get('distance_to_indigenous_land_km', 100)
        if indigenous_distance < 10:
            proximity_score += 0.4
        elif indigenous_distance < 50:
            proximity_score += 0.2

        # Check proximity to high-value forests
        hvf_distance = location_context.get('distance_to_high_value_forest_km', 100)
        if hvf_distance < 5:
            proximity_score += 0.3
        elif hvf_distance < 25:
            proximity_score += 0.15

        return min(1.0, proximity_score)

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance between two points in kilometers."""
        R = 6371  # Earth's radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def _categorize_risk_level(self, score: float) -> str:
        """Categorize risk level based on score."""
        if score >= self.HIGH_RISK_THRESHOLD:
            return "high"
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            return "medium"
        else:
            return "low"