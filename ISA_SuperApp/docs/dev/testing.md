# Testing
Last updated: 2025-09-02

Use `pytest`:
```bash
pytest -q
```
- Set `ISA_TEST_MODE=1` to bypass rate-limits/external calls.
- Avoid hard-coded paths; use `pathlib`.
- Coverage: `pytest --cov=src --cov-report=term-missing`.

Structure:
- `tests/unit/*` — pure units
- `tests/integration/*` — FastAPI TestClient calls
- `tests/system/*` — ingest/reindex flows, desktop smoke
