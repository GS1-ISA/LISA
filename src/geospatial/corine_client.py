"""
CORINE Land Cover data client for land use analysis.

This module provides integration with CORINE Land Cover data to assess
land use types and changes for EUDR compliance screening.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

import requests
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd

from ..config.performance_config import get_request_timeout


@dataclass
class LandCoverClass:
    """Represents a CORINE land cover class."""
    code: int
    name: str
    level: int
    description: str


@dataclass
class LandCoverChange:
    """Represents land cover change between two periods."""
    from_class: LandCoverClass
    to_class: LandCoverClass
    area_ha: float
    change_type: str  # deforestation, afforestation, etc.


class CORINEClient:
    """
    Client for CORINE Land Cover data integration.

    Provides methods to query land cover classes, changes, and land use
    analysis for EUDR compliance screening.
    """

    # CORINE Land Cover classes relevant for deforestation risk
    FOREST_CLASSES = {
        311: "Broad-leaved forest",
        312: "Coniferous forest",
        313: "Mixed forest",
        321: "Natural grasslands",
        322: "Moors and heathland",
        323: "Sclerophyllous vegetation",
        324: "Transitional woodland-shrub"
    }

    DEFORESTATION_RISK_CLASSES = {
        111: "Continuous urban fabric",
        112: "Discontinuous urban fabric",
        121: "Industrial or commercial units",
        122: "Road and rail networks",
        123: "Port areas",
        124: "Airports",
        131: "Mineral extraction sites",
        132: "Dump sites",
        133: "Construction sites",
        141: "Green urban areas",
        142: "Sport and leisure facilities",
        211: "Non-irrigated arable land",
        212: "Permanently irrigated land",
        213: "Rice fields",
        221: "Vineyards",
        222: "Fruit trees and berry plantations",
        223: "Olive groves",
        231: "Pastures",
        241: "Annual crops associated with permanent crops",
        242: "Complex cultivation patterns",
        243: "Land principally occupied by agriculture",
        244: "Agro-forestry areas"
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CORINE client.

        Args:
            api_key: Optional API key for Copernicus/EEA services
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'ISA-D EUDR Compliance Tool/1.0',
            'Accept': 'application/json'
        })

        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def get_land_cover(
        self,
        geometry: Polygon,
        year: int = 2018
    ) -> Dict[str, Any]:
        """
        Get land cover composition for a geographic area.

        Args:
            geometry: Shapely polygon defining the area of interest
            year: CORINE dataset year (2000, 2006, 2012, 2018)

        Returns:
            Dictionary with land cover statistics
        """
        try:
            # For this implementation, we'll use a simplified approach
            # In production, this would integrate with Copernicus API or local data

            # Mock data based on typical CORINE analysis
            # In real implementation, query actual CORINE data
            land_cover_stats = self._analyze_land_cover(geometry, year)

            return {
                'year': year,
                'total_area_ha': land_cover_stats['total_area'],
                'forest_area_ha': land_cover_stats['forest_area'],
                'deforestation_risk_area_ha': land_cover_stats['risk_area'],
                'land_cover_classes': land_cover_stats['classes'],
                'forest_percentage': land_cover_stats['forest_percentage'],
                'risk_percentage': land_cover_stats['risk_percentage']
            }

        except Exception as e:
            self.logger.error(f"Error retrieving land cover data: {str(e)}")
            return {}

    def get_land_cover_changes(
        self,
        geometry: Polygon,
        start_year: int = 2012,
        end_year: int = 2018
    ) -> List[LandCoverChange]:
        """
        Get land cover changes between two periods.

        Args:
            geometry: Shapely polygon defining the area of interest
            start_year: Start year for change analysis
            end_year: End year for change analysis

        Returns:
            List of land cover changes
        """
        try:
            # Mock implementation - in production, query actual change data
            changes = self._analyze_land_cover_changes(geometry, start_year, end_year)

            return changes

        except Exception as e:
            self.logger.error(f"Error retrieving land cover changes: {str(e)}")
            return []

    def assess_deforestation_risk(
        self,
        geometry: Polygon,
        year: int = 2018
    ) -> Dict[str, Any]:
        """
        Assess deforestation risk based on land cover analysis.

        Args:
            geometry: Shapely polygon defining the area of interest
            year: Year for analysis

        Returns:
            Risk assessment results
        """
        try:
            land_cover = self.get_land_cover(geometry, year)

            if not land_cover:
                return {'risk_score': 1.0, 'risk_level': 'unknown'}

            # Calculate risk based on land cover composition
            forest_percentage = land_cover.get('forest_percentage', 0)
            risk_percentage = land_cover.get('risk_percentage', 0)

            # Risk factors:
            # - Low forest cover increases risk
            # - High agricultural/industrial land increases risk
            forest_risk = max(0, 1.0 - (forest_percentage / 50.0))  # Risk increases below 50% forest
            development_risk = min(1.0, risk_percentage / 30.0)  # Risk from development land use

            risk_score = (forest_risk * 0.6) + (development_risk * 0.4)

            return {
                'risk_score': min(1.0, risk_score),
                'risk_level': self._categorize_risk(risk_score),
                'forest_percentage': forest_percentage,
                'development_percentage': risk_percentage,
                'assessment_year': year,
                'risk_factors': {
                    'low_forest_cover': forest_risk > 0.5,
                    'high_development_pressure': development_risk > 0.5
                }
            }

        except Exception as e:
            self.logger.error(f"Error assessing deforestation risk: {str(e)}")
            return {'risk_score': 1.0, 'risk_level': 'unknown'}

    def screen_supply_chain_locations(
        self,
        locations: List[Tuple[float, float]],
        buffer_km: float = 10
    ) -> Dict[str, Any]:
        """
        Screen supply chain locations for land use risk.

        Args:
            locations: List of (latitude, longitude) tuples
            buffer_km: Buffer distance around each location in km

        Returns:
            Risk assessment results for each location
        """
        results = {}

        for i, (lat, lon) in enumerate(locations):
            try:
                # Create buffer around location
                point = Point(lon, lat)
                buffer_geom = self._create_buffer(point, buffer_km)

                # Assess deforestation risk
                risk_assessment = self.assess_deforestation_risk(buffer_geom)

                results[f"location_{i}"] = {
                    'coordinates': (lat, lon),
                    'buffer_km': buffer_km,
                    'risk_score': risk_assessment.get('risk_score', 1.0),
                    'risk_level': risk_assessment.get('risk_level', 'unknown'),
                    'forest_percentage': risk_assessment.get('forest_percentage', 0),
                    'development_percentage': risk_assessment.get('development_percentage', 0),
                    'risk_factors': risk_assessment.get('risk_factors', {})
                }

            except Exception as e:
                self.logger.error(f"Error screening location {lat},{lon}: {str(e)}")
                results[f"location_{i}"] = {
                    'coordinates': (lat, lon),
                    'error': str(e),
                    'risk_score': 1.0,
                    'risk_level': 'unknown'
                }

        return results

    def _analyze_land_cover(self, geometry: Polygon, year: int) -> Dict[str, Any]:
        """Analyze land cover within geometry (mock implementation)."""
        # In production, this would query actual CORINE data
        # For now, return mock data based on geometry size

        area_ha = geometry.area * 111 * 111  # Rough conversion to hectares

        # Mock land cover distribution
        forest_area = area_ha * 0.4  # Assume 40% forest
        risk_area = area_ha * 0.3    # Assume 30% high-risk land use

        return {
            'total_area': area_ha,
            'forest_area': forest_area,
            'risk_area': risk_area,
            'forest_percentage': (forest_area / area_ha) * 100,
            'risk_percentage': (risk_area / area_ha) * 100,
            'classes': {
                'forest': forest_area,
                'agriculture': area_ha * 0.3,
                'urban': area_ha * 0.2,
                'other': area_ha * 0.1
            }
        }

    def _analyze_land_cover_changes(
        self,
        geometry: Polygon,
        start_year: int,
        end_year: int
    ) -> List[LandCoverChange]:
        """Analyze land cover changes (mock implementation)."""
        # Mock some changes
        changes = []

        # Example: Forest to agriculture conversion
        forest_class = LandCoverClass(311, "Broad-leaved forest", 3, "Broad-leaved forest")
        agri_class = LandCoverClass(211, "Non-irrigated arable land", 2, "Non-irrigated arable land")

        change = LandCoverChange(
            from_class=forest_class,
            to_class=agri_class,
            area_ha=50.0,
            change_type="deforestation"
        )
        changes.append(change)

        return changes

    def _create_buffer(self, point: Point, buffer_km: float) -> Polygon:
        """Create a buffer around a point."""
        # Approximate conversion: 1 degree ≈ 111 km
        buffer_degrees = buffer_km / 111.0
        return point.buffer(buffer_degrees)

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level based on score."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"