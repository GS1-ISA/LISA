# API
Last updated: 2025-09-02

## Endpoints
- `POST /ask` — {question, explain?} → {answer, trace?, importance?}
- `POST /ask_stream` — JSONL chunks for streaming
- `POST /doc/generate` — {title, outline?} → {markdown, download}
- `GET /memory?query=...` — list memory items
- `POST /search` — vector/lexical search results
- Admin: `/admin/verify`, `/admin/ingest`, `/admin/reindex`
- Auth: `/auth/login`, `/auth/logout`, `/auth/me`
- Projects: `/projects` GET/POST
- Metrics: `/metrics`
