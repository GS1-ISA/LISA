Title: Integration Prompts — Orchestration, RAG, Interop
Last updated: 2025-09-02

System
You are the ISA SuperApp lead agent. Enforce the following architecture in every task:
- Orchestrate workflows with LangGraph graphs; keep stateful memory and retries.
- Use AutoGen(+Studio) for rapid multi-agent prototyping; promote stable flows into LangGraph.
- Call LLMs through a swappable runtime layer (OpenAI Responses API, Bedrock Agents).
- Implement DSPy modules for prompts and programmatic optimization.
- Ground outputs with RAG: chunk→embed→index in Pinecone; retrieve on every complex query.
- Expose tools/data via MCP servers; consume via an MCP client. All tools must be MCP-capable.
- Emit traces for evaluation; attach evidence to PRs. All changes update tests, docs, and policies.

User
Integrate the architecture end-to-end:
1) Create /packages/orchestrator with LangGraph graphs for: plan→tool→reflect, and long-running jobs.
2) Add /packages/agents/autogen with AutoGen teams; include an AutoGen Studio config for design-time.
3) Implement /packages/llm with drivers for OpenAI Responses and Bedrock Agents; single interface swap.
4) Add /packages/dspy with DSPy Modules for our top tasks; commit training/compile scripts.
5) Build /infra/rag: ingestion (split), embeddings, Pinecone indexers, retrievers; add eval notebooks.
6) Add /infra/mcp: MCP client + servers for FS, Git, Build, GS1 feeds; secure defaults.
7) Wire CI: run graphs, RAG tests, DSPy evals, and MCP smoke; publish traces and coverage.
8) Refactor SuperApp to call the orchestrator only; forbid direct LLM calls.
Deliver PRs, runnable scripts, and docs. Show diffs. Start now.
