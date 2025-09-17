"""
ETL Assets for ISA_D.

This module contains all Dagster assets for data ingestion, transformation,
and loading operations.
"""

from .esma import (
    esma_financial_instruments,
    esma_market_data,
    esma_regulatory_reports,
)
from .eurostat import (
    eurostat_economic_indicators,
    eurostat_population_data,
    eurostat_trade_statistics,
)
from .storage import (
    store_esma_data,
    store_eurostat_data,
    update_vector_store,
)
from .transformations import (
    clean_esma_data,
    clean_eurostat_data,
    merge_datasets,
    validate_data_quality,
)

__all__ = [
    # Eurostat assets
    "eurostat_economic_indicators",
    "eurostat_population_data",
    "eurostat_trade_statistics",
    # ESMA assets
    "esma_financial_instruments",
    "esma_market_data",
    "esma_regulatory_reports",
    # Transformation assets
    "clean_eurostat_data",
    "clean_esma_data",
    "merge_datasets",
    "validate_data_quality",
    # Storage assets
    "store_eurostat_data",
    "store_esma_data",
    "update_vector_store",
]
