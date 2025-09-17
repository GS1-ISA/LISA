"""
Data transformation assets.

This module contains Dagster assets for cleaning, validating, and transforming
data from Eurostat and ESMA sources.
"""

import pandas as pd
from dagster import (
    AssetExecutionContext,
    AssetIn,
    MetadataValue,
    Output,
    asset,
)

from isa_superapp.etl.core.logger import get_logger


@asset(
    group_name="transformations",
    description="Clean and standardize Eurostat data",
    ins={"eurostat_data": AssetIn()},
)
def clean_eurostat_data(
    context: AssetExecutionContext,
    eurostat_data: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Clean and standardize Eurostat data."""
    logger = get_logger("etl.transform.eurostat")

    df = eurostat_data.copy()

    # Remove rows with null values in critical columns
    initial_count = len(df)
    df = df.dropna(subset=["value"])

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Convert data types
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Add metadata columns
    df["processed_at"] = pd.Timestamp.now()
    df["data_source"] = "eurostat"
    df["data_quality_score"] = _calculate_data_quality_score(df)

    cleaned_count = len(df)
    removed_count = initial_count - cleaned_count

    logger.info(f"Cleaned Eurostat data: {cleaned_count} records retained, {removed_count} removed")

    return Output(
        value=df,
        metadata={
            "initial_records": initial_count,
            "cleaned_records": cleaned_count,
            "removed_records": removed_count,
            "columns": list(df.columns),
            "data_quality_score": df["data_quality_score"].mean(),
        },
    )


@asset(
    group_name="transformations",
    description="Clean and standardize ESMA data",
    ins={"esma_data": AssetIn()},
)
def clean_esma_data(
    context: AssetExecutionContext,
    esma_data: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Clean and standardize ESMA data."""
    logger = get_logger("etl.transform.esma")

    df = esma_data.copy()

    # Remove rows with null values in critical columns
    initial_count = len(df)
    df = df.dropna(subset=["data"])

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Parse JSON data if present
    if "data" in df.columns:
        df["parsed_data"] = df["data"].apply(_parse_json_data)

    # Add metadata columns
    df["processed_at"] = pd.Timestamp.now()
    df["data_source"] = "esma"
    df["data_quality_score"] = _calculate_data_quality_score(df)

    cleaned_count = len(df)
    removed_count = initial_count - cleaned_count

    logger.info(f"Cleaned ESMA data: {cleaned_count} records retained, {removed_count} removed")

    return Output(
        value=df,
        metadata={
            "initial_records": initial_count,
            "cleaned_records": cleaned_count,
            "removed_records": removed_count,
            "columns": list(df.columns),
            "data_quality_score": df["data_quality_score"].mean(),
        },
    )


@asset(
    group_name="transformations",
    description="Merge Eurostat and ESMA datasets",
    ins={
        "cleaned_eurostat": AssetIn("clean_eurostat_data"),
        "cleaned_esma": AssetIn("clean_esma_data"),
    },
)
def merge_datasets(
    context: AssetExecutionContext,
    cleaned_eurostat: pd.DataFrame,
    cleaned_esma: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Merge Eurostat and ESMA datasets."""
    logger = get_logger("etl.transform.merge")

    # Create unified schema
    eurostat_cols = set(cleaned_eurostat.columns)
    esma_cols = set(cleaned_esma.columns)
    common_cols = eurostat_cols.intersection(esma_cols)

    # Add missing columns with null values
    for col in esma_cols - eurostat_cols:
        cleaned_eurostat[col] = None
    for col in eurostat_cols - esma_cols:
        cleaned_esma[col] = None

    # Concatenate datasets
    merged_df = pd.concat([cleaned_eurostat, cleaned_esma], ignore_index=True)

    # Add merge metadata
    merged_df["merge_timestamp"] = pd.Timestamp.now()
    merged_df["dataset_type"] = merged_df["data_source"]

    logger.info(f"Merged datasets: {len(merged_df)} total records")

    return Output(
        value=merged_df,
        metadata={
            "eurostat_records": len(cleaned_eurostat),
            "esma_records": len(cleaned_esma),
            "total_records": len(merged_df),
            "common_columns": list(common_cols),
            "columns": list(merged_df.columns),
        },
    )


@asset(
    group_name="transformations",
    description="Validate data quality and generate quality report",
    ins={"merged_data": AssetIn("merge_datasets")},
)
def validate_data_quality(
    context: AssetExecutionContext,
    merged_data: pd.DataFrame,
) -> Output[pd.DataFrame]:
    """Validate data quality and generate quality report."""
    logger = get_logger("etl.transform.quality")

    df = merged_data.copy()

    # Quality checks
    quality_report = {
        "total_records": len(df),
        "null_values": df.isnull().sum().to_dict(),
        "duplicate_records": df.duplicated().sum(),
        "data_types": df.dtypes.to_dict(),
        "value_ranges": _check_value_ranges(df),
        "consistency_checks": _check_data_consistency(df),
    }

    # Add quality validation columns
    df["quality_valid"] = _validate_record_quality(df)
    df["quality_issues"] = df.apply(_identify_quality_issues, axis=1)

    # Filter out low-quality records if configured
    high_quality_df = df[df["quality_valid"]]

    logger.info(f"Quality validation complete: {len(high_quality_df)} high-quality records")

    return Output(
        value=high_quality_df,
        metadata={
            "quality_report": MetadataValue.json(quality_report),
            "high_quality_records": len(high_quality_df),
            "low_quality_records": len(df) - len(high_quality_df),
            "validation_rules": [
                "null_value_check",
                "duplicate_check",
                "range_check",
                "consistency_check",
            ],
        },
    )


def _calculate_data_quality_score(df: pd.DataFrame) -> pd.Series:
    """Calculate data quality score for each record."""
    scores = pd.Series([1.0] * len(df), index=df.index)

    # Reduce score for null values
    null_penalty = df.isnull().sum(axis=1) * 0.1
    scores = scores - null_penalty

    # Ensure scores are between 0 and 1
    scores = scores.clip(0, 1)

    return scores


def _parse_json_data(data_str: str) -> dict:
    """Parse JSON data string."""
    try:
        return pd.json_normalize(data_str) if isinstance(data_str, str) else {}
    except:
        return {}


def _check_value_ranges(df: pd.DataFrame) -> dict:
    """Check value ranges for numeric columns."""
    ranges = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        ranges[col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": df[col].mean(),
            "std": df[col].std(),
        }

    return ranges


def _check_data_consistency(df: pd.DataFrame) -> dict:
    """Check data consistency across columns."""
    consistency = {}

    # Check for logical inconsistencies
    if "data_source" in df.columns:
        consistency["data_source_distribution"] = df["data_source"].value_counts().to_dict()

    return consistency


def _validate_record_quality(df: pd.DataFrame) -> pd.Series:
    """Validate quality of individual records."""
    # Simple validation: record is valid if it has no null critical fields
    critical_fields = ["value", "data"]
    critical_fields = [f for f in critical_fields if f in df.columns]

    if critical_fields:
        return ~df[critical_fields].isnull().any(axis=1)
    else:
        return pd.Series([True] * len(df))


def _identify_quality_issues(row: pd.Series) -> list:
    """Identify quality issues for a record."""
    issues = []

    # Check for null values in critical fields
    critical_fields = ["value", "data"]
    for field in critical_fields:
        if field in row.index and pd.isnull(row[field]):
            issues.append(f"null_{field}")

    return issues
