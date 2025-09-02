Title: Memory Privacy — DSR (Access/Delete/Export) Runbook
Last updated: 2025-09-02

Scope
- Handle Data Subject Requests (DSR) for memory data captured by the app (agent/memory logs, KG memory).

Where data lives
- Event logs (append-only JSONL): `agent/memory/memory_log.jsonl`
- Knowledge Graph memory file: `ISA_SuperApp/memory.json` (default; configurable via `ISA_MEMORY_FILE`)

Actions
- Access/Export: provide the relevant JSONL lines and KG entries for the subject (filter by identifiers).
- Delete entity: use `KnowledgeGraphMemory.delete_entity(name, reason="dsr-delete")` — this logs a `delete_entity` event with relations removed.
- Delete observation: `KnowledgeGraphMemory.delete_observation(name, observation, reason)`. Logs a `delete_observation` event.

Audit
- Ensure all deletions carry a reason and are logged. Include the log snapshot (`docs/audit/memory_logs_snapshot.jsonl`) in case artifacts exist.

Policy
- Keep deletion reversible only via backups until retention windows expire. Review legal retention rules before hard-deleting.

References
- Code: `ISA_SuperApp/src/memory_store.py`
- CI: memory log snapshot upload and coherence gate
- Quality policy: `docs/QUALITY_METHODS.md`

