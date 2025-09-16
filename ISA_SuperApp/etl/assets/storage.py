"""
Data storage assets.

This module contains Dagster assets for storing processed data in
the database and updating the vector store.
"""

import json
from typing import Any, Dict, List

import pandas as pd
from dagster import (
    AssetExecutionContext,
    AssetIn,
    MetadataValue,
    Output,
    asset,
)
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..core.logger import get_logger
from ..core.vector_store import create_vector_store


@asset(
    group_name="storage",
    description="Store Eurostat data in database",
    ins={"cleaned_data": AssetIn("clean_eurostat_data")},
)
def store_eurostat_data(
    context: AssetExecutionContext,
    cleaned_data: pd.DataFrame,
    database: Engine,
) -> Output[int]:
    """Store Eurostat data in database."""
    logger = get_logger("etl.storage.eurostat")

    table_name = "eurostat_data"

    try:
        # Create table if it doesn't exist
        _create_eurostat_table(database)

        # Insert data
        records_inserted = _insert_dataframe(database, table_name, cleaned_data)

        logger.info(f"Stored {records_inserted} Eurostat records in database")

        return Output(
            value=records_inserted,
            metadata={
                "table_name": table_name,
                "records_inserted": records_inserted,
                "columns": list(cleaned_data.columns),
            },
        )

    except Exception as e:
        logger.error(f"Failed to store Eurostat data: {e}")
        raise


@asset(
    group_name="storage",
    description="Store ESMA data in database",
    ins={"cleaned_data": AssetIn("clean_esma_data")},
)
def store_esma_data(
    context: AssetExecutionContext,
    cleaned_data: pd.DataFrame,
    database: Engine,
) -> Output[int]:
    """Store ESMA data in database."""
    logger = get_logger("etl.storage.esma")

    table_name = "esma_data"

    try:
        # Create table if it doesn't exist
        _create_esma_table(database)

        # Insert data
        records_inserted = _insert_dataframe(database, table_name, cleaned_data)

        logger.info(f"Stored {records_inserted} ESMA records in database")

        return Output(
            value=records_inserted,
            metadata={
                "table_name": table_name,
                "records_inserted": records_inserted,
                "columns": list(cleaned_data.columns),
            },
        )

    except Exception as e:
        logger.error(f"Failed to store ESMA data: {e}")
        raise


@asset(
    group_name="storage",
    description="Update vector store with processed data",
    ins={"validated_data": AssetIn("validate_data_quality")},
)
def update_vector_store(
    context: AssetExecutionContext,
    validated_data: pd.DataFrame,
) -> Output[int]:
    """Update vector store with processed data."""
    logger = get_logger("etl.storage.vector")

    try:
        # Create vector store instance
        vector_store = create_vector_store(
            provider="chroma",
            collection_name="isa_etl_data",
            dimension=384,  # Adjust based on embedding model
        )

        # Convert data to vector store format
        vectors = _prepare_vectors_for_storage(validated_data)

        # Add vectors to store
        await vector_store.add_vectors(vectors)

        logger.info(f"Updated vector store with {len(vectors)} vectors")

        return Output(
            value=len(vectors),
            metadata={
                "vector_store_provider": "chroma",
                "collection_name": "isa_etl_data",
                "vectors_added": len(vectors),
                "dimension": 384,
            },
        )

    except Exception as e:
        logger.error(f"Failed to update vector store: {e}")
        raise


def _create_eurostat_table(engine: Engine) -> None:
    """Create Eurostat data table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS eurostat_data (
        id SERIAL PRIMARY KEY,
        dataset_code VARCHAR(255),
        observation_key TEXT,
        value DECIMAL,
        flags VARCHAR(50),
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source VARCHAR(50) DEFAULT 'eurostat',
        data_quality_score DECIMAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_eurostat_dataset ON eurostat_data(dataset_code);
    CREATE INDEX IF NOT EXISTS idx_eurostat_processed ON eurostat_data(processed_at);
    """

    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()


def _create_esma_table(engine: Engine) -> None:
    """Create ESMA data table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS esma_data (
        id SERIAL PRIMARY KEY,
        endpoint VARCHAR(500),
        data JSONB,
        parsed_data JSONB,
        format VARCHAR(50),
        parsed BOOLEAN DEFAULT FALSE,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_source VARCHAR(50) DEFAULT 'esma',
        data_quality_score DECIMAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_esma_endpoint ON esma_data(endpoint);
    CREATE INDEX IF NOT EXISTS idx_esma_processed ON esma_data(processed_at);
    CREATE INDEX IF NOT EXISTS idx_esma_data_gin ON esma_data USING GIN(data);
    """

    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()


def _insert_dataframe(engine: Engine, table_name: str, df: pd.DataFrame) -> int:
    """Insert DataFrame into database table."""
    # Convert DataFrame to dict records
    records = df.to_dict("records")

    # Prepare insert statement
    columns = list(df.columns)
    placeholders = ", ".join([f":{col}" for col in columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    with engine.connect() as conn:
        result = conn.execute(text(insert_sql), records)
        conn.commit()

    return result.rowcount


def _prepare_vectors_for_storage(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Prepare data for vector store storage."""
    vectors = []

    for idx, row in df.iterrows():
        # Create vector representation
        # In a real implementation, you would generate embeddings here
        # For now, we'll create a simple text representation

        text_content = _row_to_text(row)

        # Mock embedding (replace with actual embedding generation)
        vector_data = [0.1] * 384  # 384-dimensional vector

        vector = {
            "id": f"etl_{idx}",
            "vector": vector_data,
            "document_id": f"etl_{idx}",
            "metadata": {
                "data_source": row.get("data_source", "unknown"),
                "processed_at": str(row.get("processed_at", "")),
                "quality_score": row.get("data_quality_score", 0),
                "dataset_type": row.get("dataset_type", "unknown"),
            },
            "text": text_content,
        }

        vectors.append(vector)

    return vectors


def _row_to_text(row: pd.Series) -> str:
    """Convert DataFrame row to text representation."""
    text_parts = []

    for col, value in row.items():
        if pd.notnull(value):
            text_parts.append(f"{col}: {value}")

    return " | ".join(text_parts)