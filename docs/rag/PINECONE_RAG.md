Title: RAG Stack — Pinecone, Ingestion, Indexers, Retrievers
Last updated: 2025-09-02

Scope
- Build ingestion (splitters), embeddings, Pinecone indexing, and retrieval utilities with eval harness.

Plan
- Ingestion: deterministic splitters; content hash IDs; UTF‑8 + newline policy.
- Embeddings: batch + backpressure; seed for determinism; metrics for tokens and cost.
- Indexing: Pinecone namespace per dataset; upserts idempotent; health checks and retries.
- Retrieval: lexical + vector hybrid; k tuning per task; cache hits measured.
- Evals: golden Q/A and docsets; grounded accuracy and latency budgets; snapshot diffs.

Adapters & Flags
- Pinecone keys via env; feature flag to disable remote writes on forks.
- Optional local fallback index (FAISS or in‑memory lexical) for dev.
