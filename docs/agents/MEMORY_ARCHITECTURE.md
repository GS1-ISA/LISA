Title: ISA Memory Architecture — Modular, Multi-Backend, CI-Gated
Last updated: 2025-09-02

Overview: Multi-backend memory system combining buffer/summary/vector, structured facts, temporal KG, and adapters to external tools. All memory writes are logged for audits; CI includes coherence and determinism checks.

Mermaid
```mermaid
flowchart TD
  U[User/Agent Interaction] --> R[Memory Router]
  R -->|short| BUF[LangChain Buffer]
  R -->|long| VEC[Vector Index]
  R -->|structured| STR[Structured Memory]
  R --> KG[KnowledgeGraphMemory]
  R --> EXT{{Adapters}}
  EXT --> MEMENG[MemEngine]
  EXT --> ZEP[Zep Temporal KG]
  EXT --> AMEM[A-MEM]
  EXT --> AWS[AWS Augmented]
  EXT --> MCP[MCP Context]
  subgraph Retrieval & Summarization
    VEC --> CTX[Context Builder]
    KG --> CTX
    BUF --> CTX
    STR --> CTX
  end
  CTX --> Reasoner[SequentialReasoner]
  U -->|feedback| Logger[MemoryEventLogger]
  Logger --> Audits[Docs/audit/memory_logs_snapshot.jsonl]
  Nap[Nap-Time Learner] --> KG
```

Routing
- Short-term: recent exchanges buffered (LangChain adapter or local buffer)
- Long-term: vector index and KG (entities + relations) provide retrieval
- Structured: typed facts (owners, IDs, policy decisions) kept in structured store
- External: Adapters AMEM, Zep, MemEngine, AWS, MCP included as optional modules

Policies
- All writes logged to `agent/memory/memory_log.jsonl`
- Deletions audited in the same log with reason/actor
- Nap-time summarization condenses recent events into long-term KG

CI Gates
- Determinism snapshot (canonical JSON)
- Memory coherence advisory gate (`scripts/memory_coherence_gate.py`)
- Memory logs snapshot uploaded as artifact

Adoption
- Adapters are optional; router degrades gracefully
- Feature flags via environment variables to steer routing or destinations

