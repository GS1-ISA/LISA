# Architecture
Last updated: 2025-09-02

- **FastAPI** backend (`src/`): orchestrator, memory, retrieval, reasoning.
- **Static web UI** (`webui/`): HTML/CSS/JS, streaming chat.
- **Pipelines**: ingest GS1/EFRAG/EUR-Lex; scheduler to refresh data.
- **Electron wrapper** (`desktop/electron/`): DMG (macOS), NSIS (Windows).
- **Tests** (`tests/`): unit, integration, system.
- **Docs** (`docs/` + `mkdocs.yml`): local MkDocs site.
