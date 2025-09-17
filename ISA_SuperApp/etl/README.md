# ISA_D ETL System

## Overview

The ISA_D ETL (Extract, Transform, Load) system is a comprehensive enterprise data pipeline built with Dagster and OpenLineage for orchestrating data workflows and tracking data lineage. This system provides robust data ingestion from Eurostat and ESMA APIs, with full integration into the ISA_D architecture.

## Architecture

### Core Components

- **Dagster**: Workflow orchestration and asset management
- **OpenLineage**: Data lineage tracking and metadata management
- **SQLAlchemy**: Database operations with connection pooling
- **Vector Store**: Integration with ISA_D's vector storage for embeddings
- **Monitoring**: Comprehensive logging and alerting capabilities

### Data Flow

```
Eurostat/ESMA APIs → Dagster Assets → Data Cleaning → Quality Validation → Database Storage → Vector Store → Lineage Tracking
```

## Features

### Data Ingestion
- **Eurostat Integration**: Economic indicators, population data, trade statistics
- **ESMA Integration**: Financial instruments, market data, regulatory reports
- **Retry Logic**: Automatic retry with exponential backoff
- **Error Handling**: Comprehensive error handling and recovery

### Data Processing
- **Data Cleaning**: Standardization, type conversion, null handling
- **Quality Validation**: Automated quality checks and reporting
- **Schema Validation**: Data structure validation and transformation
- **Deduplication**: Automatic duplicate detection and removal

### Storage & Integration
- **Database Storage**: PostgreSQL/SQLite with optimized schemas
- **Vector Store**: Integration with ChromaDB for semantic search
- **ISA_D Integration**: Seamless integration with existing ISA_D components

### Monitoring & Observability
- **Structured Logging**: JSON-formatted logs with context
- **Metrics Collection**: Prometheus metrics for monitoring
- **Alerting**: Integration with DataDog and Sentry
- **Health Checks**: Automated system health monitoring

### Data Lineage
- **OpenLineage Integration**: Complete data lineage tracking
- **Metadata Management**: Rich metadata for all data assets
- **Provenance Tracking**: Source-to-destination data flow tracking
- **Impact Analysis**: Automated impact analysis for data changes

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (recommended) or SQLite
- OpenLineage backend (optional)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
export DATABASE_URL="postgresql://user:password@localhost/isa_etl"
export OPENLINEAGE_URL="http://localhost:5000"
export DATADOG_API_KEY="your_datadog_key"
export SENTRY_DSN="your_sentry_dsn"
```

3. Initialize the database:
```bash
python -c "from src.database_manager import get_db_manager; get_db_manager()"
```

## Usage

### Running Pipelines

#### Development Mode
```bash
# Start Dagster development server
dagster dev

# Access UI at http://localhost:3000
```

#### Production Mode
```bash
# Start Dagster daemon
dagster-daemon run

# Start web server
dagster-webserver
```

### Pipeline Execution

#### Eurostat Pipeline
```python
from dagster import execute_job
from definitions import eurostat_job

result = execute_job(eurostat_job)
```

#### ESMA Pipeline
```python
from dagster import execute_job
from definitions import esma_job

result = execute_job(esma_job)
```

#### Full ETL Pipeline
```python
from dagster import execute_job
from definitions import etl_job

result = execute_job(etl_job)
```

### Testing

Run the test suite:
```bash
python test_etl.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///isa_etl.db` |
| `OPENLINEAGE_URL` | OpenLineage backend URL | `http://localhost:5000` |
| `DATADOG_API_KEY` | DataDog API key | None |
| `SENTRY_DSN` | Sentry DSN | None |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration File

The system uses a YAML configuration file (`config.yaml`) for advanced settings:

```yaml
database:
  url: ${DATABASE_URL}
  pool_size: 20
  max_overflow: 30

eurostat:
  base_url: "https://ec.europa.eu/eurostat/api/dissemination"
  timeout: 30
  retry_attempts: 3

openlineage:
  url: ${OPENLINEAGE_URL}
  api_key: ${OPENLINEAGE_API_KEY}
```

## Data Sources

### Eurostat
- **Economic Indicators**: GDP, business surveys, national accounts
- **Population Data**: Demographics, population density, age distribution
- **Trade Statistics**: Intra-EU and extra-EU trade data

### ESMA
- **Financial Instruments**: ETFs, derivatives, securities
- **Market Data**: Trading venues, market abuse reports
- **Regulatory Reports**: Supervisory convergence, risk monitoring

## Data Quality

### Quality Metrics
- **Completeness**: Percentage of non-null values
- **Accuracy**: Data validation against known ranges
- **Consistency**: Cross-field validation
- **Timeliness**: Data freshness and update frequency

### Quality Gates
- Automatic quality scoring for all datasets
- Configurable quality thresholds
- Quality report generation
- Alerting on quality degradation

## Monitoring

### Metrics
- Pipeline execution time
- Data volume processed
- Error rates and retry counts
- Database connection health
- API response times

### Dashboards
- Dagster UI for pipeline monitoring
- Grafana dashboards for metrics visualization
- DataDog integration for alerting

## Data Lineage

### Lineage Tracking
- **Dataset Provenance**: Source system tracking
- **Transformation History**: Step-by-step transformation tracking
- **Dependency Mapping**: Upstream/downstream dependency tracking
- **Impact Analysis**: Automated impact assessment

### Lineage Queries
```python
from openlineage_config import get_openlineage_config

config = get_openlineage_config()
# Query lineage information
lineage = config.client.get_lineage("eurostat_economic_indicators")
```

## API Reference

### Core Classes

#### `DatabaseResource`
Database connection management with pooling and health monitoring.

#### `EurostatAPIResource`
Eurostat API client with retry logic and error handling.

#### `ESMAApiResource`
ESMA API client with authentication and rate limiting.

#### `OpenLineageConfig`
OpenLineage integration for data lineage tracking.

### Asset Functions

#### Eurostat Assets
- `eurostat_economic_indicators()`: Fetch economic data
- `eurostat_population_data()`: Fetch population statistics
- `eurostat_trade_statistics()`: Fetch trade data

#### ESMA Assets
- `esma_financial_instruments()`: Fetch financial instrument data
- `esma_market_data()`: Fetch market data
- `esma_regulatory_reports()`: Fetch regulatory reports

#### Transformation Assets
- `clean_eurostat_data()`: Clean Eurostat data
- `clean_esma_data()`: Clean ESMA data
- `merge_datasets()`: Merge multiple data sources
- `validate_data_quality()`: Quality validation

#### Storage Assets
- `store_eurostat_data()`: Store Eurostat data in database
- `store_esma_data()`: Store ESMA data in database
- `update_vector_store()`: Update vector store with processed data

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
python -c "from src.database_manager import get_db_manager; print(get_db_manager().is_healthy())"
```

#### API Rate Limiting
- Automatic retry with exponential backoff
- Configurable rate limits in `config.yaml`
- Monitoring of API usage

#### Memory Issues
- Batch processing for large datasets
- Configurable batch sizes
- Memory usage monitoring

### Logs and Debugging

#### Log Files
- Application logs: `logs/etl.log`
- Dagster logs: `logs/dagster.log`
- OpenLineage logs: `logs/openlineage.log`

#### Debug Mode
```bash
export LOG_LEVEL=DEBUG
dagster dev
```

## Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
4. Format code: `black . && isort .`

### Code Standards
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

## License

This project is part of the ISA_D system. See the main project license for details.

## Support

For support and questions:
- Check the troubleshooting guide
- Review the logs and monitoring dashboards
- Contact the ISA_D development team