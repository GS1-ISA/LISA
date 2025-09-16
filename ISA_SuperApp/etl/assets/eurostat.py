"""
Eurostat data ingestion assets.

This module contains Dagster assets for ingesting data from Eurostat APIs,
including economic indicators, population data, and trade statistics.
"""

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dagster import (
    AssetExecutionContext,
    AssetIn,
    MetadataValue,
    Output,
    asset,
    get_dagster_logger,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.exceptions import ISAConfigurationError, ISAValidationError
from ..core.logger import get_logger
from ..openlineage_config import emit_etl_lineage


@asset(
    group_name="eurostat",
    description="Fetch economic indicators from Eurostat API",
    metadata={"source": "eurostat", "dataset": "economic_indicators"},
)
def eurostat_economic_indicators(
    context: AssetExecutionContext,
    eurostat_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch economic indicators from Eurostat."""
    logger = get_logger("etl.eurostat.economic")

    # Eurostat dataset codes for economic indicators
    datasets = [
        "nama_10_gdp",  # GDP and main components
        "ei_bsco_m",    # Business and consumer surveys
        "ei_nama_q",    # National accounts
    ]

    all_data = []

    for dataset_code in datasets:
        try:
            data = _fetch_eurostat_dataset(
                dataset_code, eurostat_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records for {dataset_code}")
        except Exception as e:
            logger.error(f"Failed to fetch {dataset_code}: {e}")
            context.add_output_metadata(
                metadata={
                    f"{dataset_code}_error": MetadataValue.text(str(e))
                }
            )

    if not all_data:
        raise ISAValidationError("No economic indicators data retrieved")

    df = pd.DataFrame(all_data)

    # Emit lineage event
    emit_etl_lineage(
        asset_name="eurostat_economic_indicators",
        output_datasets=[{
            "name": "eurostat_economic_indicators",
            "type": "table",
            "schema": dict(df.dtypes),
            "data_quality": {
                "row_count": len(df),
                "column_count": len(df.columns),
            }
        }],
        metadata={"run_id": context.run_id}
    )

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "datasets": datasets,
            "source": MetadataValue.text("Eurostat API"),
        },
    )


@asset(
    group_name="eurostat",
    description="Fetch population data from Eurostat API",
    metadata={"source": "eurostat", "dataset": "population"},
)
def eurostat_population_data(
    context: AssetExecutionContext,
    eurostat_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch population data from Eurostat."""
    logger = get_logger("etl.eurostat.population")

    # Eurostat dataset codes for population data
    datasets = [
        "demo_pjan",    # Population on 1 January
        "demo_magec",   # Mean age of childbearing
        "demo_r_d2jan", # Population density
    ]

    all_data = []

    for dataset_code in datasets:
        try:
            data = _fetch_eurostat_dataset(
                dataset_code, eurostat_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records for {dataset_code}")
        except Exception as e:
            logger.error(f"Failed to fetch {dataset_code}: {e}")

    if not all_data:
        raise ISAValidationError("No population data retrieved")

    df = pd.DataFrame(all_data)

    # Emit lineage event
    emit_etl_lineage(
        asset_name="eurostat_population_data",
        output_datasets=[{
            "name": "eurostat_population_data",
            "type": "table",
            "schema": dict(df.dtypes),
            "data_quality": {
                "row_count": len(df),
                "column_count": len(df.columns),
            }
        }],
        metadata={"run_id": context.run_id}
    )

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "datasets": datasets,
            "source": MetadataValue.text("Eurostat API"),
        },
    )


@asset(
    group_name="eurostat",
    description="Fetch trade statistics from Eurostat API",
    metadata={"source": "eurostat", "dataset": "trade"},
)
def eurostat_trade_statistics(
    context: AssetExecutionContext,
    eurostat_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch trade statistics from Eurostat."""
    logger = get_logger("etl.eurostat.trade")

    # Eurostat dataset codes for trade statistics
    datasets = [
        "ext_lt_intratrd",  # Intra-EU trade
        "ext_lt_maineu",    # Extra-EU trade
        "ext_st_27_2020sitc", # Trade by SITC
    ]

    all_data = []

    for dataset_code in datasets:
        try:
            data = _fetch_eurostat_dataset(
                dataset_code, eurostat_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records for {dataset_code}")
        except Exception as e:
            logger.error(f"Failed to fetch {dataset_code}: {e}")

    if not all_data:
        raise ISAValidationError("No trade statistics data retrieved")

    df = pd.DataFrame(all_data)

    # Emit lineage event
    emit_etl_lineage(
        asset_name="eurostat_trade_statistics",
        output_datasets=[{
            "name": "eurostat_trade_statistics",
            "type": "table",
            "schema": dict(df.dtypes),
            "data_quality": {
                "row_count": len(df),
                "column_count": len(df.columns),
            }
        }],
        metadata={"run_id": context.run_id}
    )

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "datasets": datasets,
            "source": MetadataValue.text("Eurostat API"),
        },
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def _fetch_eurostat_dataset(
    dataset_code: str,
    api_config: Dict[str, Any],
    context: AssetExecutionContext,
) -> List[Dict[str, Any]]:
    """Fetch data from a specific Eurostat dataset."""
    base_url = api_config["base_url"]
    timeout = api_config["timeout"]

    # Construct API URL
    url = f"{base_url}/sdmx/2.1/data/{dataset_code}/?format=JSON&compressed=false"

    headers = api_config.get("headers", {})

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        # Parse Eurostat JSON format
        records = _parse_eurostat_response(data, dataset_code)

        return records

    except requests.RequestException as e:
        raise ISAConfigurationError(f"API request failed for {dataset_code}: {e}")


def _parse_eurostat_response(data: Dict[str, Any], dataset_code: str) -> List[Dict[str, Any]]:
    """Parse Eurostat JSON response into records."""
    records = []

    if "dataSets" not in data or not data["dataSets"]:
        return records

    dataset = data["dataSets"][0]
    observations = dataset.get("observations", {})

    # Get dimension information
    structure = data.get("structure", {})
    dimensions = structure.get("dimensions", {}).get("observation", [])

    for obs_key, obs_value in observations.items():
        record = {
            "dataset_code": dataset_code,
            "observation_key": obs_key,
            "value": obs_value[0] if obs_value else None,
            "flags": obs_value[1] if len(obs_value) > 1 else None,
        }

        # Parse dimension values from key
        if dimensions:
            dimension_values = obs_key.split(":")
            for i, dimension in enumerate(dimensions):
                if i < len(dimension_values):
                    dim_name = dimension.get("name", f"dimension_{i}")
                    record[dim_name] = dimension_values[i]

        records.append(record)

    return records