Title: LLM Runtime Layer — OpenAI Responses API and Bedrock Agents
Last updated: 2025-09-02

Interface
- Single driver interface with swappable backends (OpenAI Responses, Bedrock Agents).
- Tool call support; streaming; retries; timeouts; telemetry.

Parity Tests
- Ensure equivalent behavior on eval tasks; snapshot key outputs; tolerance windows documented.

Policies
- Default safe OFF for external calls in CI; keys via env; rate limits and budgets enforced.
