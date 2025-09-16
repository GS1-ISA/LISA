"""
Geospatial analysis modules for EUDR compliance screening.

This package provides integration with Global Forest Watch (GFW) and CORINE Land Cover
data sources for deforestation risk assessment and supply chain geospatial analysis.
"""

from .gfw_client import GFWClient
from .corine_client import CORINEClient
from .risk_assessment import GeospatialRiskAssessor
from .screening_engine import EUDRGeospatialScreeningEngine

__all__ = [
    'GFWClient',
    'CORINEClient',
    'GeospatialRiskAssessor',
    'EUDRGeospatialScreeningEngine'
]