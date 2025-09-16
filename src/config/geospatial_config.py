"""
Configuration for geospatial analysis modules.

This module provides configuration settings for GFW, CORINE, and geospatial
risk assessment components used in EUDR compliance screening.
"""

import os
from typing import Dict, Any, Optional


class GeospatialConfig:
    """Configuration class for geospatial analysis components."""

    # GFW API Configuration
    GFW_BASE_URL = "https://api.globalforestwatch.org"
    GFW_API_KEY = os.getenv("GFW_API_KEY")  # Optional API key for authenticated requests

    # CORINE Data Configuration
    CORINE_BASE_URL = "https://land.copernicus.eu"  # Copernicus Land Service
    CORINE_API_KEY = os.getenv("COPERNICUS_API_KEY")  # Optional API key

    # Risk Assessment Configuration
    DEFAULT_BUFFER_KM = 50
    DEFAULT_LOOKBACK_YEARS = 5
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.3

    # Scoring Weights
    RISK_WEIGHTS = {
        'temporal': 0.25,
        'spatial': 0.20,
        'intensity': 0.30,
        'contextual': 0.15,
        'supply_chain': 0.10
    }

    # GFW Data Parameters
    GFW_CONFIDENCE_LEVEL = 1  # Minimum confidence for alerts (1-3)
    GFW_TREE_COVER_THRESHOLD = 30  # Minimum tree cover density (10-100%)

    # CORINE Land Cover Classes (relevant for deforestation risk)
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

    # EUDR Compliance Thresholds
    EUDR_THRESHOLDS = {
        'maximum_risk_score': 0.3,
        'minimum_forest_cover': 30,  # percentage
        'maximum_recent_deforestation': 50,  # hectares in analysis period
        'minimum_traceability_depth': 3,  # supply chain levels
        'compliance_review_frequency_days': 365  # annual reviews
    }

    # Data Source Priorities (higher = more reliable)
    DATA_SOURCE_PRIORITIES = {
        'gfw_alerts': 0.9,
        'gfw_tree_cover_loss': 0.8,
        'corine_land_cover': 0.7,
        'corine_changes': 0.6,
        'supply_chain_data': 0.5
    }

    # Caching Configuration
    CACHE_TTL_SECONDS = {
        'gfw_data': 86400,  # 24 hours
        'corine_data': 604800,  # 7 days
        'risk_assessments': 3600,  # 1 hour
        'screening_results': 1800  # 30 minutes
    }

    # Performance Limits
    MAX_LOCATIONS_PER_SCREENING = 100
    MAX_BUFFER_KM = 500
    MAX_LOOKBACK_YEARS = 10

    # Error Handling
    MAX_RETRY_ATTEMPTS = 3
    REQUEST_TIMEOUT_SECONDS = 30

    @classmethod
    def get_gfw_config(cls) -> Dict[str, Any]:
        """Get GFW-specific configuration."""
        return {
            'base_url': cls.GFW_BASE_URL,
            'api_key': cls.GFW_API_KEY,
            'confidence_level': cls.GFW_CONFIDENCE_LEVEL,
            'tree_cover_threshold': cls.GFW_TREE_COVER_THRESHOLD,
            'timeout': cls.REQUEST_TIMEOUT_SECONDS,
            'max_retries': cls.MAX_RETRY_ATTEMPTS
        }

    @classmethod
    def get_corine_config(cls) -> Dict[str, Any]:
        """Get CORINE-specific configuration."""
        return {
            'base_url': cls.CORINE_BASE_URL,
            'api_key': cls.CORINE_API_KEY,
            'forest_classes': cls.FOREST_CLASSES,
            'risk_classes': cls.DEFORESTATION_RISK_CLASSES,
            'timeout': cls.REQUEST_TIMEOUT_SECONDS,
            'max_retries': cls.MAX_RETRY_ATTEMPTS
        }

    @classmethod
    def get_risk_assessment_config(cls) -> Dict[str, Any]:
        """Get risk assessment configuration."""
        return {
            'default_buffer_km': cls.DEFAULT_BUFFER_KM,
            'default_lookback_years': cls.DEFAULT_LOOKBACK_YEARS,
            'high_risk_threshold': cls.HIGH_RISK_THRESHOLD,
            'medium_risk_threshold': cls.MEDIUM_RISK_THRESHOLD,
            'weights': cls.RISK_WEIGHTS,
            'eudr_thresholds': cls.EUDR_THRESHOLDS,
            'data_source_priorities': cls.DATA_SOURCE_PRIORITIES
        }

    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Get performance-related configuration."""
        return {
            'max_locations_per_screening': cls.MAX_LOCATIONS_PER_SCREENING,
            'max_buffer_km': cls.MAX_BUFFER_KM,
            'max_lookback_years': cls.MAX_LOOKBACK_YEARS,
            'cache_ttl': cls.CACHE_TTL_SECONDS,
            'request_timeout': cls.REQUEST_TIMEOUT_SECONDS
        }

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []

        # Check required environment variables
        if not cls.GFW_API_KEY:
            issues.append("GFW_API_KEY not set (optional but recommended)")

        if not cls.CORINE_API_KEY:
            issues.append("COPERNICUS_API_KEY not set (optional but recommended)")

        # Validate thresholds
        if not (0 < cls.HIGH_RISK_THRESHOLD <= 1):
            issues.append(f"Invalid HIGH_RISK_THRESHOLD: {cls.HIGH_RISK_THRESHOLD}")

        if not (0 < cls.MEDIUM_RISK_THRESHOLD < cls.HIGH_RISK_THRESHOLD):
            issues.append(f"Invalid MEDIUM_RISK_THRESHOLD: {cls.MEDIUM_RISK_THRESHOLD}")

        # Validate weights
        total_weight = sum(cls.RISK_WEIGHTS.values())
        if abs(total_weight - 1.0) > 0.001:
            issues.append(f"Risk weights don't sum to 1.0: {total_weight}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'config_summary': {
                'gfw_configured': bool(cls.GFW_API_KEY),
                'corine_configured': bool(cls.CORINE_API_KEY),
                'risk_thresholds_valid': True,
                'weights_normalized': abs(total_weight - 1.0) <= 0.001
            }
        }


# Global configuration instance
geospatial_config = GeospatialConfig()