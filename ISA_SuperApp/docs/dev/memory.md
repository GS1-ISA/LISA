Title: Memory & Context — Router, Adapters, and Coherence
Last updated: 2025-09-02

Overview
- ISA uses a modular memory stack: short-term buffer, vector/KG long-term, and structured facts.
- A Memory Router detects context type (short/long/structured) and builds enriched context from KG + vector + adapters.
- All memory writes/reads are logged to JSONL for audits.

Key Components
- Router: `src/memory/router.py` — detect, route, build context.
- Adapters: `src/memory/adapters/*` — LangChain buffer (optional), structured facts, external stubs (Zep, MemEngine, A‑MEM, AWS, MCP).
- Logs: `src/memory/logs.py` — append-only JSONL (`agent/memory/memory_log.jsonl`).
- Drift: `src/memory/drift.py` — advisory drift check (cosine over tokens).
- Nap-time: `src/memory/background.py` — summarize recent events into long-term KG after idle windows.

Configuration
- `ISA_MEMORY_ADAPTERS`: comma-separated list to enable (default: `langchain,structured,memengine,zep,amem,aws,mcp`).
- `ISA_SLEEPTIME_MINUTES`: idle window for nap-time learning (default: 30).
- `ISA_MEMORY_FILE`: path to KG persistence (default: `./memory.json`).

CI Integration
- `ci.yml` runs an advisory memory coherence gate and uploads a memory log snapshot to `docs/audit/memory_logs_snapshot.jsonl`.
- Promotion criteria are described in root `docs/CI_WORKFLOWS.md`.

References
- Memory Architecture (site): `agents/MEMORY_ARCHITECTURE.md` (diagram and policies).
