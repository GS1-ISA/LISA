# ISA_C — ESG Data Pipeline
Last updated: 2025-09-02

This repository contains the *full, production-ready* baseline for ISA_C, including adapters,
optional layers (Prefect, DuckDB Delta/Idempotency, OpenTelemetry, Feast), tests, docs, and CI.

- 🇬🇧 **English**: See [`README_en.md`](./docs/README_en.md)
- 🇳🇱 **Nederlands**: Zie [`README_nl.md`](./docs/README_nl.md)

For a high-level architecture diagram, see [`docs/architecture/diagram.mmd`](./docs/architecture/diagram.mmd).


## Autodev Agent Loop
Run once:
```bash
python -m autodev.main
```
Loop:
```bash
python -m autodev.main --loop --sleep=15
```
Configure `.env` with your model API key.


## Refactor kit
### Quick start
```bash
make ci-all
```
### Run
```bash
python -m isa_c
```
### Docker
```bash
docker compose up --build
```
