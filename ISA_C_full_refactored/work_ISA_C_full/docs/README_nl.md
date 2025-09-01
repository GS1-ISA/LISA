# ISA_C — Geïntegreerde ESG Datapijplijn (Nederlands)

## Overzicht
ISA_C levert een schone, uitbreidbare basis om ESG-bronnen in te lezen (EU Cellar, EFRAG,
Eurostat, SEC, GS1, GS1 NL). Het systeem biedt:
- Modulaire adapters (Strategy pattern) onder `isa_c.adapters.*`
- Orchestrators: een eenvoudige runner en **optioneel** een Prefect-flow
- Optionele **idempotency** en **delta** opslag met DuckDB
- Robuuste logging met JSON-uitvoer, correlatie-ID's en roterende handlers
- Deterministische setup (Makefile, pre-commit, mypy, ruff, pytest)
- Documentatie met MkDocs + mkdocstrings
- Voorbeeldtests en CI (GitHub Actions)

## Snelstart
```bash
make setup        # maakt .venv en installeert basis (editable mode)
make run          # draait de eenvoudige runner (standaard offline samples)
# Optioneel:
USE_PREFECT=1 make run-flow
USE_DELTA=1 make run
```

Stel variabelen in via `.env` (zie `.env.example`). Met `ISA_OFFLINE=1` schrijven adapters
een kleine sample CSV in `data/raw/<adapter>/`.

## Architectuur
- **Domein / Applicatie**: dunne orkestratie + adapters
- **Infrastructuur**: storage, logging, settings
- **Presentatie**: CLI-runner en Prefect-flow (optioneel)

Zie het Mermaid-diagram in `docs/architecture/diagram.mmd`.

## Adapters
Elke adapter implementeert:
```python
class BaseAdapter(ABC):
    def fetch(self, since: datetime) -> pd.DataFrame: ...
    def validate(self, df: pd.DataFrame) -> ValidationResult: ...
```
Offline-modus schrijft `sample.csv`. Online-modus verbindt met echte API’s (nu placeholders).

## Optionele Lagen
- **Prefect** (`USE_PREFECT=1`): parallelle orkestratie en retries.
- **DuckDB Idempotency** (`USE_DELTA=1`): voorkomt herverwerking, houdt stempels/versies bij.
- **OpenTelemetry**: automatische tracing wanneer OTEL-variabelen gezet zijn.
- **Feast**: opt-in via `docker-compose.feast.yml` als feature store.

## Kwaliteitshekken
- `ruff`, `black`, `mypy --strict`, `pytest -q`, `safety`/`pip-audit` optioneel
- Pre-commit hooks draaien op elke commit

## Projectstructuur
```
isa_c/
  adapters/
  app/
  storage/
  utils/
configs/
docs/
scripts/
tests/
```

## Aannames
- Python ≥ 3.11
- Netwerk/offline via `ISA_OFFLINE=1`
- Data als Pandas DataFrames; persist als CSV/Parquet waar nodig

## Bijdragen
- Alleen PR’s met groene CI
- Volg stijlgidsen en gebruik conventionele commitberichten
- Leg belangrijke keuzes vast in ADR’s onder `docs/architecture/decisions/`
