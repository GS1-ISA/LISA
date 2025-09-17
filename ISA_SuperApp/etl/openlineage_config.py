"""
OpenLineage configuration for ISA_D ETL system.

This module provides comprehensive OpenLineage integration for
data lineage tracking across the ETL pipelines.
"""

import os
from typing import Any

from openlineage.client import OpenLineageClient
from openlineage.client.facet import (
    DataQualityMetricsInputDatasetFacet,
    DataSourceDatasetFacet,
    SchemaDatasetFacet,
    SchemaField,
)


class OpenLineageConfig:
    """OpenLineage configuration and utilities."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        namespace: str = "isa-etl",
    ):
        """
        Initialize OpenLineage configuration.

        Args:
            url: OpenLineage backend URL
            api_key: API key for authentication
            namespace: Namespace for lineage events
        """
        self.url = url or os.getenv("OPENLINEAGE_URL", "http://localhost:5000")
        self.api_key = api_key or os.getenv("OPENLINEAGE_API_KEY")
        self.namespace = namespace

        # Initialize client
        self.client = self._create_client()

    def _create_client(self) -> OpenLineageClient:
        """Create OpenLineage client."""
        config = {
            "transport": {
                "type": "http",
                "url": self.url,
                "endpoint": "api/v1/lineage",
            }
        }

        if self.api_key:
            config["transport"]["auth"] = {
                "type": "api_key",
                "apiKey": self.api_key,
            }

        return OpenLineageClient(config=config)

    def create_dataset_facet(
        self,
        dataset_name: str,
        dataset_type: str,
        schema: dict[str, Any] | None = None,
        data_quality: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create dataset facets for lineage tracking."""
        facets = {}

        # Data source facet
        facets["dataSource"] = DataSourceDatasetFacet(
            name=dataset_name,
            uri=f"{self.namespace}://{dataset_type}/{dataset_name}",
        )

        # Schema facet
        if schema:
            fields = []
            for field_name, field_type in schema.items():
                fields.append(SchemaField(
                    name=field_name,
                    type=str(field_type),
                    description=f"Field {field_name} of type {field_type}",
                ))

            facets["schema"] = SchemaDatasetFacet(fields=fields)

        # Data quality facet
        if data_quality:
            facets["dataQualityMetrics"] = DataQualityMetricsInputDatasetFacet(
                rowCount=data_quality.get("row_count"),
                bytes=data_quality.get("bytes"),
                columnMetrics=data_quality.get("column_metrics", {}),
            )

        return facets

    def emit_lineage_event(
        self,
        job_name: str,
        job_namespace: str,
        inputs: list | None = None,
        outputs: list | None = None,
        run_id: str | None = None,
        **facets
    ) -> None:
        """Emit a lineage event."""
        try:
            self.client.emit(
                event_type="COMPLETE",
                job_name=job_name,
                job_namespace=job_namespace,
                inputs=inputs or [],
                outputs=outputs or [],
                run_id=run_id,
                **facets
            )
        except Exception as e:
            # Log error but don't fail the pipeline
            print(f"Failed to emit lineage event: {e}")


# Global instance
_openlineage_config: OpenLineageConfig | None = None


def get_openlineage_config() -> OpenLineageConfig:
    """Get or create global OpenLineage configuration instance."""
    global _openlineage_config

    if _openlineage_config is None:
        _openlineage_config = OpenLineageConfig()

    return _openlineage_config


def emit_etl_lineage(
    asset_name: str,
    input_datasets: list | None = None,
    output_datasets: list | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit lineage event for ETL asset."""
    config = get_openlineage_config()

    config.emit_lineage_event(
        job_name=f"etl.{asset_name}",
        job_namespace="isa-etl",
        inputs=input_datasets,
        outputs=output_datasets,
        run_id=metadata.get("run_id") if metadata else None,
    )
