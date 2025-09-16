"""
Global Forest Watch (GFW) API client for deforestation data.

This module provides integration with GFW APIs to retrieve deforestation alerts,
tree cover loss data, and forest monitoring information for EUDR compliance screening.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd

from ..config.performance_config import get_request_timeout


@dataclass
class DeforestationAlert:
    """Represents a deforestation alert from GFW."""
    alert_id: str
    latitude: float
    longitude: float
    confidence: float
    date: datetime
    area_ha: float
    is_glad: bool = True
    source: str = "GFW"


@dataclass
class TreeCoverLoss:
    """Represents tree cover loss data."""
    latitude: float
    longitude: float
    loss_year: int
    area_ha: float
    threshold: int = 30


class GFWClient:
    """
    Client for Global Forest Watch API integration.

    Provides methods to query deforestation alerts, tree cover loss,
    and other forest monitoring data for risk assessment.
    """

    BASE_URL = "https://api.globalforestwatch.org"
    ALERTS_ENDPOINT = "/v2/glad-alerts"
    TREE_COVER_LOSS_ENDPOINT = "/v2/tree-cover-loss"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GFW client.

        Args:
            api_key: Optional API key for authenticated requests
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

    def get_deforestation_alerts(
        self,
        geometry: Polygon,
        start_date: datetime,
        end_date: datetime,
        confidence: int = 1
    ) -> List[DeforestationAlert]:
        """
        Retrieve deforestation alerts within a geographic area.

        Args:
            geometry: Shapely polygon defining the area of interest
            start_date: Start date for alerts
            end_date: End date for alerts
            confidence: Minimum confidence level (1-3)

        Returns:
            List of deforestation alerts
        """
        try:
            # Convert geometry to GeoJSON
            geojson = self._polygon_to_geojson(geometry)

            params = {
                'geostore': geojson,
                'period': f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}",
                'confidence': confidence,
                'format': 'json'
            }

            response = self._make_request('GET', self.ALERTS_ENDPOINT, params=params)
            alerts_data = response.json()

            alerts = []
            for alert in alerts_data.get('data', []):
                alert_obj = DeforestationAlert(
                    alert_id=alert.get('id', ''),
                    latitude=alert.get('attributes', {}).get('latitude', 0),
                    longitude=alert.get('attributes', {}).get('longitude', 0),
                    confidence=alert.get('attributes', {}).get('confidence', 0),
                    date=datetime.fromisoformat(alert.get('attributes', {}).get('date', '').replace('Z', '+00:00')),
                    area_ha=alert.get('attributes', {}).get('area_ha', 0),
                    is_glad=alert.get('attributes', {}).get('is_glad', True)
                )
                alerts.append(alert_obj)

            self.logger.info(f"Retrieved {len(alerts)} deforestation alerts")
            return alerts

        except Exception as e:
            self.logger.error(f"Error retrieving deforestation alerts: {str(e)}")
            return []

    def get_tree_cover_loss(
        self,
        geometry: Polygon,
        start_year: int,
        end_year: int,
        threshold: int = 30
    ) -> List[TreeCoverLoss]:
        """
        Retrieve tree cover loss data within a geographic area.

        Args:
            geometry: Shapely polygon defining the area of interest
            start_year: Start year for loss data
            end_year: End year for loss data
            threshold: Tree cover density threshold (10-100%)

        Returns:
            List of tree cover loss records
        """
        try:
            geojson = self._polygon_to_geojson(geometry)

            params = {
                'geostore': geojson,
                'period': f"{start_year},{end_year}",
                'threshold': threshold,
                'format': 'json'
            }

            response = self._make_request('GET', self.TREE_COVER_LOSS_ENDPOINT, params=params)
            loss_data = response.json()

            losses = []
            for loss in loss_data.get('data', []):
                loss_obj = TreeCoverLoss(
                    latitude=loss.get('attributes', {}).get('latitude', 0),
                    longitude=loss.get('attributes', {}).get('longitude', 0),
                    loss_year=loss.get('attributes', {}).get('loss_year', 0),
                    area_ha=loss.get('attributes', {}).get('area_ha', 0),
                    threshold=threshold
                )
                losses.append(loss_obj)

            self.logger.info(f"Retrieved {len(losses)} tree cover loss records")
            return losses

        except Exception as e:
            self.logger.error(f"Error retrieving tree cover loss data: {str(e)}")
            return []

    def get_forest_cover_stats(
        self,
        geometry: Polygon,
        year: int = 2020
    ) -> Dict[str, Any]:
        """
        Get forest cover statistics for a geographic area.

        Args:
            geometry: Shapely polygon defining the area of interest
            year: Year for forest cover data

        Returns:
            Dictionary with forest cover statistics
        """
        try:
            geojson = self._polygon_to_geojson(geometry)

            params = {
                'geostore': geojson,
                'year': year,
                'format': 'json'
            }

            response = self._make_request('GET', '/v2/tree-cover', params=params)
            stats = response.json()

            return {
                'total_area_ha': stats.get('data', {}).get('attributes', {}).get('total_area', 0),
                'tree_cover_area_ha': stats.get('data', {}).get('attributes', {}).get('tree_cover_area', 0),
                'tree_cover_extent_ha': stats.get('data', {}).get('attributes', {}).get('tree_cover_extent', 0),
                'year': year
            }

        except Exception as e:
            self.logger.error(f"Error retrieving forest cover stats: {str(e)}")
            return {}

    def screen_supply_chain_locations(
        self,
        locations: List[Tuple[float, float]],
        buffer_km: float = 50,
        lookback_years: int = 5
    ) -> Dict[str, Any]:
        """
        Screen supply chain locations for deforestation risk.

        Args:
            locations: List of (latitude, longitude) tuples
            buffer_km: Buffer distance around each location in km
            lookback_years: Number of years to look back for alerts

        Returns:
            Risk assessment results for each location
        """
        results = {}

        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_years * 365)

        for i, (lat, lon) in enumerate(locations):
            try:
                # Create buffer around location
                point = Point(lon, lat)
                buffer_geom = self._create_buffer(point, buffer_km)

                # Get deforestation alerts
                alerts = self.get_deforestation_alerts(buffer_geom, start_date, end_date)

                # Get tree cover loss
                current_year = datetime.now().year
                start_year = max(2001, current_year - lookback_years)
                losses = self.get_tree_cover_loss(buffer_geom, start_year, current_year)

                # Calculate risk score
                risk_score = self._calculate_location_risk(alerts, losses, buffer_km)

                results[f"location_{i}"] = {
                    'coordinates': (lat, lon),
                    'buffer_km': buffer_km,
                    'alerts_count': len(alerts),
                    'total_alert_area_ha': sum(alert.area_ha for alert in alerts),
                    'losses_count': len(losses),
                    'total_loss_area_ha': sum(loss.area_ha for loss in losses),
                    'risk_score': risk_score,
                    'risk_level': self._categorize_risk(risk_score)
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

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request to GFW API with retry logic."""
        url = f"{self.BASE_URL}{endpoint}"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    timeout=get_request_timeout()
                )
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("All request attempts failed")

    def _polygon_to_geojson(self, polygon: Polygon) -> str:
        """Convert Shapely polygon to GeoJSON string."""
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[list(coord) for coord in polygon.exterior.coords]]
                }
            }]
        }
        return str(geojson).replace("'", '"')

    def _create_buffer(self, point: Point, buffer_km: float) -> Polygon:
        """Create a buffer around a point."""
        # Approximate conversion: 1 degree ≈ 111 km
        buffer_degrees = buffer_km / 111.0
        return point.buffer(buffer_degrees)

    def _calculate_location_risk(
        self,
        alerts: List[DeforestationAlert],
        losses: List[TreeCoverLoss],
        buffer_km: float
    ) -> float:
        """Calculate risk score for a location based on alerts and losses."""
        if not alerts and not losses:
            return 0.0

        # Weight factors
        alert_weight = 0.6
        loss_weight = 0.4

        # Alert risk (based on count and area)
        alert_score = min(1.0, (len(alerts) * 0.1) + (sum(a.area_ha for a in alerts) / 1000))

        # Loss risk (based on count and area)
        loss_score = min(1.0, (len(losses) * 0.05) + (sum(l.area_ha for l in losses) / 500))

        # Buffer size adjustment (smaller buffers are more concerning)
        buffer_factor = max(0.5, 1.0 - (buffer_km / 100))

        risk_score = (alert_score * alert_weight + loss_score * loss_weight) * buffer_factor
        return min(1.0, risk_score)

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level based on score."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"