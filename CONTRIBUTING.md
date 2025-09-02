Title: Contributing Guide — Local Checks and Workflow

Thanks for contributing! Please follow these steps to keep quality high and docs coherent.

Local Setup
- Python 3.11+ recommended. Create a venv at repo root and install deps:
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `python -m pip install -U pip wheel`
  - `pip install -r ISA_SuperApp/requirements.txt -r ISA_SuperApp/requirements-dev.txt`

Before You Commit / Open a PR
- Lint/format: `ruff format . && ruff check --fix .`
- Types (advisory): `mypy ISA_SuperApp/src || true`
- Determinism snapshot: `cd ISA_SuperApp && pytest -q tests/unit/test_snapshot_canonical_sample.py || true`
- Docs references: `make docs-lint` (inspect `docs/audit/docs_ref_report.md`)
- Healthcheck (consolidated): `make healthcheck` (see `docs/audit/healthcheck.md`)
- PR Notes: `make pr-notes` (attach `agent/outcomes/PR_NOTES.md` to your PR)

Commit Messages
- Follow Conventional Commits (commitlint is configured). Examples:
  - `feat(api): add /ask endpoint`
  - `fix(observability): include trace/span in logs`
  - `docs: update roadmap and adoption plan`

Agentic Practices
- Keep changes small and reversible; include tests/docs; respect determinism.
- Use adapters/feature flags for new integrations; defaults safe (OFF).
- If you add external tracing or tools, gate with env flags (e.g., `OTEL_ENABLED`).

Observability (Optional)
- Tracing: `make otel-up`; then `export OTEL_ENABLED=1` and run `make api`. Jaeger UI at http://127.0.0.1:16686
- Metrics: `make prom-up` and visit Prometheus (9090) / Grafana (3000)

Thank you!
