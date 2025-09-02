# Configuration
Last updated: 2025-09-02

Settings are provided via `.env` (copy from `.env.example`). Never commit secrets.
Key variables:
- `OPENROUTER_API_KEY` / `ISA_API_KEY_OPENROUTER`
- `FIGMA_ACCESS_TOKEN`
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- `ISA_AUTH_SECRET`, users and passwords for admin/user roles.

Additional environment flags
- `ISA_LLM_PROVIDER` (default `openrouter`), `OPENAI_API_KEY`
- `ISA_FORBID_DIRECT_LLM` (set `1` to forbid direct LLM calls; use orchestrator only)
- `ISA_MEMORY_ADAPTERS` (comma list; default includes `langchain,structured,memengine,zep,amem,aws,mcp`)
- `ISA_SLEEPTIME_MINUTES` (default `30`) and `ISA_MEMORY_FILE`
- `OTEL_ENABLED=1` to enable tracing; `OTEL_EXPORTER_OTLP_ENDPOINT`
