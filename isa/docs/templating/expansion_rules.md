# ISA Smart Templating Rules

These rules allow any future ISA markdown document to self-expand as new development signals are detected.

---

## 📄 Expansion Triggers (Markdown-Level)

1. `<!-- AUTO_EXPAND_ON: plugin_submission -->`
   → Inserts plugin metadata block if new plugin is detected.

2. `<!-- AUTO_EXPAND_ON: governance_vote -->`
   → Appends governance outcome and voting rationale.

3. `<!-- AUTO_EXPAND_ON: api_exposure -->`
   → Inserts OpenAPI or GraphQL spec snippets from docs/interface.

4. `<!-- AUTO_EXPAND_ON: KG_entity_growth -->`
   → Adds TypeDB schema deltas from knowledge ingestion tools.

---

## 🛠 Runtime Template Injection (Tool-Driven)

- `docs/phases/phaseX.md` will ingest from:
  - `memory/prompt_versions.json`
  - `config/langgraph_nodes/`
  - `docs/testing/agent_behavior_tests.md`

Use templating flags in `.md` files to denote insertion points.

Example:
```md
<!-- AUTO_EXPAND_ON: plugin_submission -->
<!-- INSERT: from memory/plugin_metadata.json -->
```
