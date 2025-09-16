"""
Dagster definitions for ISA_D ETL system.

This module defines all Dagster assets, jobs, schedules, and resources
for the enterprise ETL pipelines.
"""

import os
from pathlib import Path

from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)
from dagster_dbt import dbt_cli_resource
from openlineage.dagster import OpenLineageDagsterResource

from . import assets
from .resources import database_resource, eurostat_api_resource, esma_api_resource


# Load all assets from the assets module
all_assets = load_assets_from_modules([assets])

# Define jobs
etl_job = define_asset_job(
    "etl_job",
    selection=AssetSelection.all(),
    description="Complete ETL pipeline for Eurostat and ESMA data",
)

eurostat_job = define_asset_job(
    "eurostat_job",
    selection=AssetSelection.groups("eurostat"),
    description="Eurostat data ingestion pipeline",
)

esma_job = define_asset_job(
    "esma_job",
    selection=AssetSelection.groups("esma"),
    description="ESMA data ingestion pipeline",
)

# Define schedules
daily_etl_schedule = ScheduleDefinition(
    job=etl_job,
    cron_schedule="0 2 * * *",  # Daily at 2 AM
    description="Daily ETL pipeline execution",
)

hourly_eurostat_schedule = ScheduleDefinition(
    job=eurostat_job,
    cron_schedule="0 * * * *",  # Hourly
    description="Hourly Eurostat data updates",
)

# OpenLineage configuration
openlineage_resource = OpenLineageDagsterResource(
    config={
        "transport": {
            "type": "http",
            "url": os.getenv("OPENLINEAGE_URL", "http://localhost:5000"),
            "endpoint": "api/v1/lineage",
        },
        "facets": {
            "data_quality": {"enabled": True},
            "data_source": {"enabled": True},
            "schema": {"enabled": True},
        },
    }
)

# DBT resource (if using DBT for transformations)
dbt_resource = dbt_cli_resource.configured(
    {
        "project_dir": str(Path(__file__).parent / "dbt"),
        "profiles_dir": str(Path(__file__).parent / "dbt" / "profiles"),
    }
)

# Define all resources
resources = {
    "database": database_resource,
    "eurostat_api": eurostat_api_resource,
    "esma_api": esma_api_resource,
    "openlineage": openlineage_resource,
    "dbt": dbt_resource,
}

# Main definitions object
defs = Definitions(
    assets=all_assets,
    jobs=[etl_job, eurostat_job, esma_job],
    schedules=[daily_etl_schedule, hourly_eurostat_schedule],
    resources=resources,
)