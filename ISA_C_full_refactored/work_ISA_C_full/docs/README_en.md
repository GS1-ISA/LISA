# ISA_C — Integrated ESG Data Pipeline (English)

## Overview
ISA_C provides a clean, extensible baseline to ingest ESG-related sources (EU Cellar, EFRAG,
Eurostat, SEC, GS1, GS1 NL). The system offers:
- Modular adapters (Strategy pattern) under `isa_c.adapters.*`
- Orchestrators: a simple runner and an **optional** Prefect flow
- Optional **idempotency** and **delta** storage backed by DuckDB
- Robust logging with JSON output, correlation IDs, and rotating handlers
- Deterministic project setup (Makefile, pre-commit, mypy, ruff, pytest)
- Docs with MkDocs + mkdocstrings
- Example tests and CI (GitHub Actions)

## Quick Start
```bash
make setup        # create .venv and install basics (editable mode)
make run          # run the simple runner (offline samples by default)
# Opt-in:
USE_PREFECT=1 make run-flow
USE_DELTA=1 make run
```

Set environment in `.env` (see `.env.example`). When `ISA_OFFLINE=1`, each adapter writes a
small sample CSV under `data/raw/<adapter>/`.

## Architecture
- **Domain / Application**: thin orchestration + adapters
- **Infrastructure**: storage, logging, settings
- **Presentation**: CLI runner and Prefect flow (optional)

See the Mermaid diagram at `docs/architecture/diagram.mmd`.

## Adapters
Each adapter implements:
```python
class BaseAdapter(ABC):
    def fetch(self, since: datetime) -> pd.DataFrame: ...
    def validate(self, df: pd.DataFrame) -> ValidationResult: ...
```
Offline mode writes a `sample.csv`. Online mode should connect to real APIs (placeholders now).

## Optional Layers
- **Prefect** (`USE_PREFECT=1`): concurrent orchestration and retries.
- **DuckDB Idempotency** (`USE_DELTA=1`): prevent reprocessing, keep stamps/versions.
- **OpenTelemetry**: automatic tracing if OTEL env vars are present.
- **Feast**: opt-in via `docker-compose.feast.yml` for feature store.

## Quality Gates
- `ruff`, `black`, `mypy --strict`, `pytest -q`, `safety`/`pip-audit` optional
- Pre-commit hooks run on each commit

## Project Layout
```
isa_c/
  adapters/           # sources (cellar, efrag, eurostat, sec, gs1, gs1nl)
  app/                # runner and prefect flow
  storage/            # idempotency and caching
  utils/              # logging, settings, validation helpers
configs/
docs/
scripts/
tests/
```

## Assumptions
- Python ≥ 3.11
- Network/offline toggled by `ISA_OFFLINE=1`
- Data modeled as Pandas DataFrames; persisted as CSV/Parquet as needed

## Contributing
- Open PRs with green CI only
- Follow style guides and commit conventional messages
- Record significant choices in ADRs under `docs/architecture/decisions/`
