Title: MCP — Model Context Protocol for Tools & Data
Last updated: 2025-09-02

Goals
- Standardize tool/data access. All tools exposed via MCP servers; clients enforce auth and scopes.

Initial Servers
- FS (filesystem restricted), Git (read‑only by default), Build (safe commands catalog), GS1 feeds (read‑only)

Client
- Minimal MCP client with session/permissions; adapters for orchestrator.

CI Smoke
- Spin up servers for FS/Git; run basic list/read; assert permission boundaries; publish logs.

