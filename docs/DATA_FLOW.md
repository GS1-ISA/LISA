# Research Data Flow — CLI, Agents, Tools, Memory
Last updated: 2025-09-06

Overview
This diagram shows how a research request flows through the system in this repository variant (CLI-first; optional API for smoke tests).

ASCII Diagram
```
Client/CLI/API            Orchestrator                Agents                      Tools/Memory             Output
-----------------        ------------------          ---------------------        -------------------      -------------------------
`run_research_crew.py` -> ResearchGraph.run  ->  Planner -> Researcher -> Synth -> WebResearchTool ----->  HTTP(S) pages (DDG, httpx)
HTTP GET /research   \                              |           |                 RAGMemory (ChromaDB) ->  Vector store (persistent)
                      \------------------------------+-----------+--------------------------------------------------------------

Notes
- Planner may consult Docs Provider (Context7) if `CONTEXT7_ENABLED=1`.
- Researcher uses DuckDuckGo search + `httpx` + BeautifulSoup with file caching.
- RAGMemory uses ChromaDB `PersistentClient` under `storage/vector_store/...` with SentenceTransformer embeddings.
- `/metrics` exposes Prometheus counters and latencies for basic observability.
```

Related Files
- CLI: `README.md` (Run the Research Crew)
- API: `src/api_server.py` (minimal, for container smoke checks)
- Orchestrator: `src/orchestrator/research_graph.py`
- Agents: `src/agent_core/agents/*`
- Tools: `src/tools/web_research.py`
- Memory: `src/agent_core/memory/rag_store.py`
