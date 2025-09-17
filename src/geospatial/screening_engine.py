"""
EUDR Geospatial Screening Engine.

This module provides the main interface for EUDR compliance screening,
integrating GFW and CORINE data with supply chain analysis to provide
comprehensive deforestation risk assessments.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .corine_client import CORINEClient
from .deforestation_scorer import DeforestationRiskScorer
from .gfw_client import GFWClient
from .risk_assessment import (
    GeospatialRiskAssessor,
    LocationRiskAssessment,
)
from .supply_chain_analysis import SupplyChainGeospatialAnalyzer, SupplyChainNode


@dataclass
class EUDRScreeningResult:
    """Result of EUDR geospatial screening."""
    screening_id: str
    timestamp: datetime
    target_locations: list[tuple[float, float]]
    risk_assessments: list[LocationRiskAssessment]
    overall_compliance_score: float
    compliance_level: str
    high_risk_locations: list[dict[str, Any]]
    mitigation_actions: list[dict[str, Any]]
    data_sources: dict[str, Any]
    confidence_score: float


@dataclass
class ComplianceReport:
    """Comprehensive EUDR compliance report."""
    report_id: str
    generated_at: datetime
    screening_results: list[EUDRScreeningResult]
    supply_chain_analysis: dict[str, Any] | None
    regulatory_requirements: dict[str, Any]
    recommendations: list[str]
    next_review_date: datetime


class EUDRGeospatialScreeningEngine:
    """
    Main engine for EUDR geospatial compliance screening.

    Provides end-to-end screening capabilities combining deforestation data,
    land use analysis, and supply chain risk assessment for EUDR compliance.
    """

    def __init__(
        self,
        gfw_api_key: str | None = None,
        corine_api_key: str | None = None
    ):
        """
        Initialize the EUDR screening engine.

        Args:
            gfw_api_key: Optional API key for GFW
            corine_api_key: Optional API key for CORINE/Copernicus
        """
        self.gfw_client = GFWClient(gfw_api_key)
        self.corine_client = CORINEClient(corine_api_key)
        self.risk_assessor = GeospatialRiskAssessor(gfw_api_key, corine_api_key)
        self.supply_chain_analyzer = SupplyChainGeospatialAnalyzer(self.risk_assessor)
        self.deforestation_scorer = DeforestationRiskScorer()
        self.logger = logging.getLogger(__name__)

    def screen_supply_chain_locations(
        self,
        locations: list[tuple[float, float]],
        buffer_km: float = 50,
        lookback_years: int = 5,
        screening_id: str | None = None
    ) -> EUDRScreeningResult:
        """
        Screen supply chain locations for EUDR compliance.

        Args:
            locations: List of (latitude, longitude) tuples
            buffer_km: Analysis buffer in kilometers
            lookback_years: Years to look back for historical data
            screening_id: Optional custom screening identifier

        Returns:
            Comprehensive screening result
        """
        try:
            if not screening_id:
                screening_id = f"EUDR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.logger.info(f"Starting EUDR screening {screening_id} for {len(locations)} locations")

            # Assess risk for all locations
            risk_assessments = []
            for lat, lon in locations:
                assessment = self.risk_assessor.assess_location_risk(lat, lon, buffer_km, lookback_years)
                risk_assessments.append(assessment)

            # Calculate overall compliance metrics
            overall_score = self._calculate_overall_compliance_score(risk_assessments)
            compliance_level = self._determine_compliance_level(overall_score)

            # Identify high-risk locations
            high_risk_locations = self._identify_high_risk_locations(risk_assessments)

            # Generate mitigation actions
            mitigation_actions = self._generate_mitigation_actions(risk_assessments, high_risk_locations)

            # Calculate confidence score
            confidence_score = self._calculate_screening_confidence(risk_assessments)

            # Document data sources
            data_sources = {
                "gfw": {
                    "api_version": "v2",
                    "data_types": ["deforestation_alerts", "tree_cover_loss"],
                    "temporal_coverage": f"{lookback_years} years",
                    "spatial_resolution": f"{buffer_km}km buffer"
                },
                "corine": {
                    "dataset": "CLC 2018",
                    "data_types": ["land_cover_classes", "land_cover_changes"],
                    "spatial_resolution": f"{buffer_km}km buffer"
                }
            }

            result = EUDRScreeningResult(
                screening_id=screening_id,
                timestamp=datetime.now(),
                target_locations=locations,
                risk_assessments=risk_assessments,
                overall_compliance_score=overall_score,
                compliance_level=compliance_level,
                high_risk_locations=high_risk_locations,
                mitigation_actions=mitigation_actions,
                data_sources=data_sources,
                confidence_score=confidence_score
            )

            self.logger.info(f"Completed EUDR screening {screening_id}: {compliance_level} compliance ({overall_score:.2f})")
            return result

        except Exception as e:
            self.logger.error(f"Error in EUDR screening: {str(e)}")
            return EUDRScreeningResult(
                screening_id=screening_id or "ERROR",
                timestamp=datetime.now(),
                target_locations=locations,
                risk_assessments=[],
                overall_compliance_score=0.0,
                compliance_level="error",
                high_risk_locations=[],
                mitigation_actions=[{"type": "error", "description": str(e)}],
                data_sources={},
                confidence_score=0.0
            )

    def analyze_supply_chain_network(
        self,
        nodes: list[SupplyChainNode],
        connections: list[tuple[str, str]],
        buffer_km: float = 50,
        lookback_years: int = 5
    ) -> dict[str, Any]:
        """
        Perform comprehensive supply chain network analysis.

        Args:
            nodes: Supply chain nodes
            connections: Node connections
            buffer_km: Analysis buffer
            lookback_years: Historical data lookback

        Returns:
            Network analysis results
        """
        try:
            return self.supply_chain_analyzer.analyze_supply_chain_network(
                nodes, connections, buffer_km, lookback_years
            )
        except Exception as e:
            self.logger.error(f"Error in supply chain network analysis: {str(e)}")
            return {"error": str(e)}

    def generate_compliance_report(
        self,
        screening_results: list[EUDRScreeningResult],
        supply_chain_analysis: dict[str, Any] | None = None,
        company_info: dict[str, Any] | None = None
    ) -> ComplianceReport:
        """
        Generate comprehensive EUDR compliance report.

        Args:
            screening_results: Results from screening operations
            supply_chain_analysis: Optional supply chain analysis
            company_info: Optional company information

        Returns:
            Complete compliance report
        """
        try:
            report_id = f"EUDR_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Aggregate screening results
            all_assessments = []
            for result in screening_results:
                all_assessments.extend(result.risk_assessments)

            # Calculate aggregate metrics
            if all_assessments:
                sum(a.combined_risk_score for a in all_assessments) / len(all_assessments)
                sum(1 for a in all_assessments if a.risk_level == "high")
                len(all_assessments)
            else:
                pass

            # Generate recommendations
            recommendations = self._generate_report_recommendations(
                screening_results, supply_chain_analysis
            )

            # Set next review date (typically annual for EUDR)
            next_review = datetime.now().replace(year=datetime.now().year + 1)

            # Regulatory requirements summary
            regulatory_requirements = {
                "eudr_regulation": "EU 2023/1115",
                "effective_date": "2024-12-30",
                "reporting_requirements": [
                    "Due diligence statements",
                    "Supply chain geolocation data",
                    "Deforestation risk assessments"
                ],
                "high_risk_commodities": [
                    "Cattle", "Cocoa", "Coffee", "Oil palm", "Rubber", "Soy", "Wood"
                ],
                "compliance_thresholds": {
                    "maximum_risk_score": 0.3,
                    "minimum_forest_cover": 30,
                    "maximum_recent_deforestation": 50  # hectares
                }
            }

            report = ComplianceReport(
                report_id=report_id,
                generated_at=datetime.now(),
                screening_results=screening_results,
                supply_chain_analysis=supply_chain_analysis,
                regulatory_requirements=regulatory_requirements,
                recommendations=recommendations,
                next_review_date=next_review
            )

            self.logger.info(f"Generated EUDR compliance report {report_id}")
            return report

        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            return ComplianceReport(
                report_id="ERROR",
                generated_at=datetime.now(),
                screening_results=[],
                supply_chain_analysis=None,
                regulatory_requirements={},
                recommendations=[f"Error generating report: {str(e)}"],
                next_review_date=datetime.now()
            )

    def validate_due_diligence_data(
        self,
        due_diligence_statement: dict[str, Any],
        location_data: list[tuple[float, float]]
    ) -> dict[str, Any]:
        """
        Validate due diligence statement against geospatial data.

        Args:
            due_diligence_statement: Due diligence statement data
            location_data: Associated location coordinates

        Returns:
            Validation results
        """
        try:
            validation_results = {
                "statement_valid": True,
                "location_risks": [],
                "discrepancies": [],
                "recommendations": []
            }

            # Screen locations
            screening_result = self.screen_supply_chain_locations(location_data)

            # Check for high-risk locations not mentioned in statement
            high_risk_in_statement = due_diligence_statement.get("high_risk_areas", [])
            actual_high_risk = list(screening_result.high_risk_locations)

            for risk_loc in actual_high_risk:
                coords = risk_loc["coordinates"]
                if not any(self._coordinates_match(coords, stmt_loc) for stmt_loc in high_risk_in_statement):
                    validation_results["discrepancies"].append({
                        "type": "undisclosed_high_risk",
                        "location": coords,
                        "risk_score": risk_loc["risk_score"]
                    })

            # Validate risk mitigation measures
            mitigation_measures = due_diligence_statement.get("risk_mitigation", [])
            if screening_result.overall_compliance_score > 0.3 and not mitigation_measures:
                validation_results["discrepancies"].append({
                    "type": "missing_mitigation",
                    "description": "High risk identified but no mitigation measures specified"
                })

            # Overall validation
            validation_results["statement_valid"] = len(validation_results["discrepancies"]) == 0
            validation_results["recommendations"] = screening_result.mitigation_actions

            return validation_results

        except Exception as e:
            self.logger.error(f"Error validating due diligence data: {str(e)}")
            return {"statement_valid": False, "error": str(e)}

    def _calculate_overall_compliance_score(self, assessments: list[LocationRiskAssessment]) -> float:
        """Calculate overall compliance score from individual assessments."""
        if not assessments:
            return 1.0  # Default to compliant if no data

        # Weight assessments by risk level
        weights = []
        scores = []

        for assessment in assessments:
            score = assessment.combined_risk_score

            # Give higher weight to high-risk locations
            if assessment.risk_level == "high":
                weight = 3.0
            elif assessment.risk_level == "medium":
                weight = 2.0
            else:
                weight = 1.0

            weights.append(weight)
            scores.append(score)

        # Weighted average
        total_weight = sum(weights)
        if total_weight == 0:
            return sum(scores) / len(scores) if scores else 1.0

        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=False)) / total_weight

        # Convert to compliance score (lower risk = higher compliance)
        compliance_score = 1.0 - weighted_score

        return max(0.0, min(1.0, compliance_score))

    def _determine_compliance_level(self, compliance_score: float) -> str:
        """Determine compliance level based on score."""
        if compliance_score >= 0.8:
            return "compliant"
        elif compliance_score >= 0.6:
            return "moderate_risk"
        elif compliance_score >= 0.4:
            return "high_risk"
        else:
            return "non_compliant"

    def _identify_high_risk_locations(self, assessments: list[LocationRiskAssessment]) -> list[dict[str, Any]]:
        """Identify locations with high deforestation risk."""
        high_risk = []

        for assessment in assessments:
            if assessment.risk_level == "high" or assessment.combined_risk_score > 0.7:
                high_risk.append({
                    "coordinates": assessment.coordinates,
                    "risk_score": assessment.combined_risk_score,
                    "risk_factors": assessment.risk_factors,
                    "alerts_count": assessment.alerts_count,
                    "recent_deforestation_ha": assessment.recent_deforestation_ha,
                    "forest_cover_percentage": assessment.forest_cover_percentage
                })

        return high_risk

    def _generate_mitigation_actions(
        self,
        assessments: list[LocationRiskAssessment],
        high_risk_locations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate mitigation actions based on risk assessments."""
        actions = []

        # Actions for high-risk locations
        for location in high_risk_locations:
            actions.append({
                "type": "supplier_audit",
                "priority": "high",
                "description": f'Conduct immediate audit of supplier at {location["coordinates"]}',
                "location": location["coordinates"],
                "risk_score": location["risk_score"]
            })

        # General mitigation actions
        total_alerts = sum(a.alerts_count for a in assessments)
        if total_alerts > 20:
            actions.append({
                "type": "monitoring_system",
                "priority": "high",
                "description": "Implement real-time deforestation monitoring system",
                "rationale": f"{total_alerts} deforestation alerts detected across supply chain"
            })

        low_forest_count = sum(1 for a in assessments if a.forest_cover_percentage < 30)
        if low_forest_count > 0:
            actions.append({
                "type": "supplier_diversification",
                "priority": "medium",
                "description": f"Diversify suppliers in {low_forest_count} low-forest-cover regions",
                "rationale": "Reduce exposure to deforestation-vulnerable areas"
            })

        return actions

    def _calculate_screening_confidence(self, assessments: list[LocationRiskAssessment]) -> float:
        """Calculate confidence score for the screening results."""
        if not assessments:
            return 0.0

        # Base confidence on data completeness
        completeness_scores = []

        for assessment in assessments:
            score = 0.0
            if assessment.gfw_risk_score >= 0:  # Has GFW data
                score += 0.5
            if assessment.corine_risk_score >= 0:  # Has CORINE data
                score += 0.3
            if assessment.risk_factors:  # Has detailed factors
                score += 0.2

            completeness_scores.append(score)

        avg_completeness = sum(completeness_scores) / len(completeness_scores)

        # Adjust for number of locations (more locations = higher confidence)
        location_bonus = min(0.2, len(assessments) / 50)

        confidence = min(1.0, avg_completeness + location_bonus)
        return confidence

    def _generate_report_recommendations(
        self,
        screening_results: list[EUDRScreeningResult],
        supply_chain_analysis: dict[str, Any] | None
    ) -> list[str]:
        """Generate recommendations for the compliance report."""
        recommendations = []

        # Aggregate metrics
        total_high_risk = sum(len(r.high_risk_locations) for r in screening_results)
        avg_compliance = sum(r.overall_compliance_score for r in screening_results) / len(screening_results)

        if total_high_risk > 0:
            recommendations.append(
                f"URGENT: Address {total_high_risk} high-risk locations identified across screenings"
            )

        if avg_compliance < 0.7:
            recommendations.append(
                "Improve overall compliance: Implement comprehensive supplier verification program"
            )

        if supply_chain_analysis:
            network_risks = supply_chain_analysis.get("risk_hotspots", [])
            if network_risks:
                recommendations.append(
                    f"Strengthen supply chain resilience: {len(network_risks)} network vulnerabilities identified"
                )

        # Standard EUDR recommendations
        recommendations.extend([
            "Maintain geolocation data for all suppliers",
            "Implement annual EUDR compliance reviews",
            "Document risk mitigation measures",
            "Prepare for regulatory reporting requirements"
        ])

        return recommendations

    def _coordinates_match(self, coord1: tuple[float, float], coord2: tuple[float, float], tolerance: float = 0.01) -> bool:
        """Check if coordinates match within tolerance."""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        return abs(lat1 - lat2) < tolerance and abs(lon1 - lon2) < tolerance
