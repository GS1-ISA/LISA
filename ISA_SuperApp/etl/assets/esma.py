"""
ESMA data ingestion assets.

This module contains Dagster assets for ingesting data from ESMA APIs,
including financial instruments, market data, and regulatory reports.
"""

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    Output,
    asset,
    get_dagster_logger,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.exceptions import ISAConfigurationError, ISAValidationError
from ..core.logger import get_logger


@asset(
    group_name="esma",
    description="Fetch financial instruments data from ESMA API",
    metadata={"source": "esma", "dataset": "financial_instruments"},
)
def esma_financial_instruments(
    context: AssetExecutionContext,
    esma_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch financial instruments data from ESMA."""
    logger = get_logger("etl.esma.instruments")

    # ESMA endpoints for financial instruments
    endpoints = [
        "/public-ws/financial-instruments",
        "/public-ws/derivatives",
        "/public-ws/etfs",
    ]

    all_data = []

    for endpoint in endpoints:
        try:
            data = _fetch_esma_endpoint(
                endpoint, esma_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records from {endpoint}")
        except Exception as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")
            context.add_output_metadata(
                metadata={
                    f"{endpoint}_error": MetadataValue.text(str(e))
                }
            )

    if not all_data:
        raise ISAValidationError("No financial instruments data retrieved")

    df = pd.DataFrame(all_data)

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "endpoints": endpoints,
            "source": MetadataValue.text("ESMA API"),
        },
    )


@asset(
    group_name="esma",
    description="Fetch market data from ESMA API",
    metadata={"source": "esma", "dataset": "market_data"},
)
def esma_market_data(
    context: AssetExecutionContext,
    esma_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch market data from ESMA."""
    logger = get_logger("etl.esma.market")

    # ESMA endpoints for market data
    endpoints = [
        "/public-ws/market-data",
        "/public-ws/trading-venues",
        "/public-ws/market-abuse",
    ]

    all_data = []

    for endpoint in endpoints:
        try:
            data = _fetch_esma_endpoint(
                endpoint, esma_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records from {endpoint}")
        except Exception as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")

    if not all_data:
        raise ISAValidationError("No market data retrieved")

    df = pd.DataFrame(all_data)

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "endpoints": endpoints,
            "source": MetadataValue.text("ESMA API"),
        },
    )


@asset(
    group_name="esma",
    description="Fetch regulatory reports from ESMA API",
    metadata={"source": "esma", "dataset": "regulatory_reports"},
)
def esma_regulatory_reports(
    context: AssetExecutionContext,
    esma_api: Dict[str, Any],
) -> Output[pd.DataFrame]:
    """Fetch regulatory reports from ESMA."""
    logger = get_logger("etl.esma.regulatory")

    # ESMA endpoints for regulatory reports
    endpoints = [
        "/public-ws/regulatory-reports",
        "/public-ws/risk-monitoring",
        "/public-ws/supervisory-convergence",
    ]

    all_data = []

    for endpoint in endpoints:
        try:
            data = _fetch_esma_endpoint(
                endpoint, esma_api, context
            )
            if data:
                all_data.extend(data)
                logger.info(f"Fetched {len(data)} records from {endpoint}")
        except Exception as e:
            logger.error(f"Failed to fetch {endpoint}: {e}")

    if not all_data:
        raise ISAValidationError("No regulatory reports data retrieved")

    df = pd.DataFrame(all_data)

    return Output(
        value=df,
        metadata={
            "num_records": len(df),
            "columns": list(df.columns),
            "endpoints": endpoints,
            "source": MetadataValue.text("ESMA API"),
        },
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def _fetch_esma_endpoint(
    endpoint: str,
    api_config: Dict[str, Any],
    context: AssetExecutionContext,
) -> List[Dict[str, Any]]:
    """Fetch data from a specific ESMA endpoint."""
    base_url = api_config["base_url"]
    timeout = api_config["timeout"]

    # Construct API URL
    url = f"{base_url}{endpoint}"

    headers = api_config.get("headers", {})

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # ESMA typically returns XML or JSON
        content_type = response.headers.get("content-type", "")

        if "json" in content_type.lower():
            data = response.json()
            return _parse_esma_json_response(data, endpoint)
        elif "xml" in content_type.lower():
            # Parse XML response
            return _parse_esma_xml_response(response.text, endpoint)
        else:
            # Try to parse as JSON first, fallback to text
            try:
                data = response.json()
                return _parse_esma_json_response(data, endpoint)
            except json.JSONDecodeError:
                return _parse_esma_text_response(response.text, endpoint)

    except requests.RequestException as e:
        raise ISAConfigurationError(f"API request failed for {endpoint}: {e}")


def _parse_esma_json_response(data: Dict[str, Any], endpoint: str) -> List[Dict[str, Any]]:
    """Parse ESMA JSON response into records."""
    records = []

    # ESMA API responses vary by endpoint
    # This is a generic parser that may need customization per endpoint

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                record = {
                    "endpoint": endpoint,
                    "data": json.dumps(item),
                    **item
                }
                records.append(record)
    elif isinstance(data, dict):
        # Single record or nested structure
        if "records" in data:
            for record in data["records"]:
                record["endpoint"] = endpoint
                records.append(record)
        else:
            record = {
                "endpoint": endpoint,
                "data": json.dumps(data),
                **data
            }
            records.append(record)

    return records


def _parse_esma_xml_response(xml_text: str, endpoint: str) -> List[Dict[str, Any]]:
    """Parse ESMA XML response into records."""
    # Placeholder for XML parsing
    # In a real implementation, use lxml or xml.etree
    return [{
        "endpoint": endpoint,
        "data": xml_text,
        "format": "xml",
        "parsed": False
    }]


def _parse_esma_text_response(text: str, endpoint: str) -> List[Dict[str, Any]]:
    """Parse ESMA text response into records."""
    return [{
        "endpoint": endpoint,
        "data": text,
        "format": "text",
        "parsed": False
    }]