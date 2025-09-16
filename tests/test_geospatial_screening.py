"""
Tests for EUDR geospatial screening functionality.

This module contains unit tests for the GFW, CORINE, and geospatial risk assessment
components used in EUDR compliance screening.
"""

import pytest
import unittest.mock as mock
from datetime import datetime, timedelta
from shapely.geometry import Point, Polygon

from src.geospatial.gfw_client import GFWClient, DeforestationAlert, TreeCoverLoss
from src.geospatial.corine_client import CORINEClient
from src.geospatial.risk_assessment import GeospatialRiskAssessor, LocationRiskAssessment
from src.geospatial.screening_engine import EUDRGeospatialScreeningEngine, EUDRScreeningResult
from src.geospatial.deforestation_scorer import DeforestationRiskScorer
from src.config.geospatial_config import GeospatialConfig


class TestGFWClient:
    """Test cases for GFW API client."""

    @pytest.fixture
    def gfw_client(self):
        """Create GFW client for testing."""
        return GFWClient()

    def test_initialization(self, gfw_client):
        """Test GFW client initialization."""
        assert gfw_client.api_key is None
        assert gfw_client.session is not None
        assert "ISA-D EUDR Compliance Tool" in gfw_client.session.headers["User-Agent"]

    @mock.patch('src.geospatial.gfw_client.requests.Session.request')
    def test_get_deforestation_alerts(self, mock_request, gfw_client):
        """Test retrieving deforestation alerts."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            'data': [{
                'id': 'alert_1',
                'attributes': {
                    'latitude': 10.0,
                    'longitude': 20.0,
                    'confidence': 2,
                    'date': '2023-01-15T00:00:00Z',
                    'area_ha': 5.5,
                    'is_glad': True
                }
            }]
        }
        mock_request.return_value = mock_response

        # Create test geometry
        geometry = Point(20.0, 10.0).buffer(1)

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        alerts = gfw_client.get_deforestation_alerts(geometry, start_date, end_date)

        assert len(alerts) == 1
        assert alerts[0].alert_id == 'alert_1'
        assert alerts[0].latitude == 10.0
        assert alerts[0].longitude == 20.0
        assert alerts[0].area_ha == 5.5

    def test_calculate_location_risk(self, gfw_client):
        """Test location risk calculation."""
        alerts = [
            DeforestationAlert('1', 10.0, 20.0, 2, datetime.now(), 10.0),
            DeforestationAlert('2', 10.1, 20.1, 3, datetime.now(), 5.0)
        ]
        losses = [
            TreeCoverLoss(10.0, 20.0, 2022, 15.0),
        ]

        geometry = Point(20.0, 10.0).buffer(1)
        area_sq_degrees = geometry.area

        risk_score = gfw_client._calculate_gfw_risk_score(alerts, losses, area_sq_degrees)

        assert 0 <= risk_score <= 1
        assert risk_score > 0  # Should have some risk with alerts and losses


class TestCORINEClient:
    """Test cases for CORINE data client."""

    @pytest.fixture
    def corine_client(self):
        """Create CORINE client for testing."""
        return CORINEClient()

    def test_initialization(self, corine_client):
        """Test CORINE client initialization."""
        assert corine_client.api_key is None
        assert corine_client.session is not None

    def test_assess_deforestation_risk(self, corine_client):
        """Test deforestation risk assessment."""
        geometry = Point(10.0, 20.0).buffer(1)

        risk_assessment = corine_client.assess_deforestation_risk(geometry)

        # Should return a dict with risk_score
        assert isinstance(risk_assessment, dict)
        assert 'risk_score' in risk_assessment
        assert 0 <= risk_assessment['risk_score'] <= 1

    def test_forest_classes_defined(self, corine_client):
        """Test that forest classes are properly defined."""
        assert len(corine_client.FOREST_CLASSES) > 0
        assert 311 in corine_client.FOREST_CLASSES  # Broad-leaved forest
        assert 312 in corine_client.FOREST_CLASSES  # Coniferous forest


class TestGeospatialRiskAssessor:
    """Test cases for geospatial risk assessor."""

    @pytest.fixture
    def risk_assessor(self):
        """Create risk assessor for testing."""
        return GeospatialRiskAssessor()

    def test_initialization(self, risk_assessor):
        """Test risk assessor initialization."""
        assert risk_assessor.gfw_client is not None
        assert risk_assessor.corine_client is not None
        assert risk_assessor.logger is not None

    @mock.patch('src.geospatial.risk_assessment.GeospatialRiskAssessor._assess_gfw_risk')
    @mock.patch('src.geospatial.risk_assessment.GeospatialRiskAssessor._assess_corine_risk')
    def test_assess_location_risk(self, mock_corine, mock_gfw, risk_assessor):
        """Test location risk assessment."""
        # Mock the assessment methods
        mock_gfw.return_value = {'risk_score': 0.3, 'alerts_count': 2}
        mock_corine.return_value = {'risk_score': 0.2, 'forest_percentage': 60}

        assessment = risk_assessor.assess_location_risk(10.0, 20.0)

        assert isinstance(assessment, LocationRiskAssessment)
        assert assessment.coordinates == (10.0, 20.0)
        assert assessment.gfw_risk_score == 0.3
        assert assessment.corine_risk_score == 0.2
        assert assessment.combined_risk_score > 0
        assert assessment.risk_level in ['low', 'medium', 'high']

    def test_combine_risk_scores(self, risk_assessor):
        """Test risk score combination."""
        combined = risk_assessor._combine_risk_scores(0.4, 0.3)
        assert 0 <= combined <= 1

        # Test edge cases
        combined_zero = risk_assessor._combine_risk_scores(0.0, 0.0)
        assert combined_zero == 0.0

        combined_max = risk_assessor._combine_risk_scores(1.0, 1.0)
        assert combined_max <= 1.0


class TestDeforestationRiskScorer:
    """Test cases for deforestation risk scorer."""

    @pytest.fixture
    def risk_scorer(self):
        """Create risk scorer for testing."""
        return DeforestationRiskScorer()

    def test_initialization(self, risk_scorer):
        """Test risk scorer initialization."""
        assert risk_scorer.logger is not None
        assert hasattr(risk_scorer, 'HIGH_RISK_THRESHOLD')
        assert hasattr(risk_scorer, 'MEDIUM_RISK_THRESHOLD')

    def test_calculate_temporal_risk(self, risk_scorer):
        """Test temporal risk calculation."""
        # Recent alerts should have higher risk
        recent_alerts = [
            DeforestationAlert('1', 0, 0, 1, datetime.now(), 10),
            DeforestationAlert('2', 0, 0, 1, datetime.now() - timedelta(days=30), 5)
        ]

        temporal_risk = risk_scorer._calculate_temporal_risk(recent_alerts, 100)
        assert 0 <= temporal_risk <= 1

        # Old alerts should have lower risk
        old_alerts = [
            DeforestationAlert('1', 0, 0, 1, datetime.now() - timedelta(days=400), 10)
        ]

        old_temporal_risk = risk_scorer._calculate_temporal_risk(old_alerts, 100)
        assert old_temporal_risk < temporal_risk

    def test_categorize_risk_level(self, risk_scorer):
        """Test risk level categorization."""
        assert risk_scorer._categorize_risk_level(0.8) == "high"
        assert risk_scorer._categorize_risk_level(0.5) == "medium"
        assert risk_scorer._categorize_risk_level(0.2) == "low"


class TestEUDRGeospatialScreeningEngine:
    """Test cases for EUDR screening engine."""

    @pytest.fixture
    def screening_engine(self):
        """Create screening engine for testing."""
        return EUDRGeospatialScreeningEngine()

    def test_initialization(self, screening_engine):
        """Test screening engine initialization."""
        assert screening_engine.gfw_client is not None
        assert screening_engine.corine_client is not None
        assert screening_engine.risk_assessor is not None
        assert screening_engine.supply_chain_analyzer is not None
        assert screening_engine.deforestation_scorer is not None

    @mock.patch('src.geospatial.screening_engine.EUDRGeospatialScreeningEngine.risk_assessor')
    def test_screen_supply_chain_locations(self, mock_risk_assessor, screening_engine):
        """Test supply chain location screening."""
        # Mock risk assessment
        mock_assessment = LocationRiskAssessment(
            coordinates=(10.0, 20.0),
            gfw_risk_score=0.3,
            corine_risk_score=0.2,
            combined_risk_score=0.25,
            risk_level="medium",
            risk_factors={},
            alerts_count=1,
            recent_deforestation_ha=5.0,
            forest_cover_percentage=70,
            land_use_risk=0.2,
            recommendations=["Monitor deforestation alerts"]
        )

        mock_risk_assessor.assess_location_risk.return_value = mock_assessment

        locations = [(10.0, 20.0), (11.0, 21.0)]
        result = screening_engine.screen_supply_chain_locations(locations)

        assert isinstance(result, EUDRScreeningResult)
        assert result.screening_id.startswith("EUDR_")
        assert len(result.risk_assessments) == 2
        assert result.overall_compliance_score > 0
        assert result.compliance_level in ["compliant", "moderate_risk", "high_risk", "non_compliant"]


class TestGeospatialConfig:
    """Test cases for geospatial configuration."""

    def test_config_validation(self):
        """Test configuration validation."""
        validation = GeospatialConfig.validate_config()

        assert isinstance(validation, dict)
        assert 'valid' in validation
        assert 'issues' in validation
        assert 'config_summary' in validation

    def test_config_values(self):
        """Test configuration values are reasonable."""
        assert GeospatialConfig.DEFAULT_BUFFER_KM > 0
        assert GeospatialConfig.DEFAULT_LOOKBACK_YEARS > 0
        assert 0 < GeospatialConfig.MEDIUM_RISK_THRESHOLD < GeospatialConfig.HIGH_RISK_THRESHOLD < 1

        # Test weights sum to 1
        total_weight = sum(GeospatialConfig.RISK_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001

    def test_get_gfw_config(self):
        """Test GFW config retrieval."""
        config = GeospatialConfig.get_gfw_config()
        assert 'base_url' in config
        assert 'confidence_level' in config
        assert 'timeout' in config

    def test_get_corine_config(self):
        """Test CORINE config retrieval."""
        config = GeospatialConfig.get_corine_config()
        assert 'base_url' in config
        assert 'forest_classes' in config
        assert 'risk_classes' in config


if __name__ == '__main__':
    pytest.main([__file__])