# Research Capabilities — Acquisition, Extraction, Provenance
Last updated: 2025-09-02

Overview
- Deterministic, ethical research pipeline with caching, robots/ToS compliance, extraction, and provenance.

Components
- Fetcher (`scripts/research/fetcher.py`): caching, audit logs, robots check, local file support for offline tests.
- Extractor (`scripts/research/extract.py`): bs4+lxml extraction, boilerplate removal, whitespace normalization.
- Offline tests: `scripts/research/tests/` ensures deterministic behavior without network.
- Indexer: `scripts/research/index_docs.py` converts normalized fixtures (e.g., W3C TR) into the SuperApp VectorIndex storage for retrieval experiments.
  - Supports W3C TR and Federal Register fixture indexing; can also write normalized docs into KG with provenance.

Policies
- Respect robots.txt and Terms; no live network in PR CI; nightly seeds with allowlists.
- Audit log JSONL includes url, ts, status, bytes, sha256, robots status.
- Provenance: content store hashed by sha256; metadata recorded.

Next
- Tier‑1 connectors (EUR‑Lex, Federal Register, WHO, W3C TR) via APIs.
- Search ledger auto‑population from research sessions.
- Summarize/embed harvested docs and index in VectorIndex + KG with provenance.
 - Nightly `research_seed.yml` builds fixture indexes and offline eval artifacts (top hits per query) to validate RAG utility.

Use‑Cases Mapped To Tools (Web‑Enabled)
- Research & Best Practices: curate insights from reputable engineering blogs and agent benchmark roundups (e.g., RisingStack for programming workflows, EvidentlyAI agent benchmark guides). Capture summaries as research ledgers with citations.
- Code Example Discovery: leverage example‑centric search (Blueprint/Codota patterns) and semantic code search (Sourcegraph/Cody) to find idioms and references; feed results into short design notes with links.
- Benchmarking Developer Tools: evaluate Cursor/Copilot/Claude Code for generation and review productivity on a small, curated PR set; consider DevBench/SWE‑bench for end‑to‑end capacity tracking.
- Plugin‑Based Assistance: document safe usage of ChatGPT code/browsing plugins and IDE integrations (Copilot Agent) with explicit privacy and rate policies.
- Continuous Quality & Code Health: integrate Semgrep rulesets; optionally CodeScene for hotspots/code health trends (advisory reports in CI).
- Targeted Agent Collections: define task‑specific subagents for debugging, code review, DevOps; measure value with before/after metrics.
- Educational Support: VS Code explainers (e.g., GPTutor‑style) to speed onboarding; formalize into onboarding runbooks.

Example Agent Workflows
- Design Flow: agent searches for “enterprise UX dashboard patterns 2025”, synthesizes principles, and drafts a UI spec (with citations and design tradeoffs).
- Error Fixing: given a stack trace, agent queries known blogs/forums for context, proposes fixes with links and minimal repros.
- Code Snippets: “Given this partial Python code, find REST patterns in projects on GitHub using Sourcegraph” → insert examples and annotate differences.
- Benchmark Evaluation: run DevBench/SWE‑bench (subset) on nightly, analyze failures, suggest training/eval improvements.
- Refactoring Support: use example‑first queries (“decorator patterns in Python”) to scaffold refactors and tests.

Tooling Summary (to be adopted under flags)
- Blogs/Benchmarks: RisingStack, EvidentlyAI summaries
- Example Search: Blueprint, Codota
- Semantic Search: Sourcegraph/Cody (or local sg/rg if offline)
- Agents: Cursor, Copilot Agent, Claude Code (documented usage & privacy)
- Eval Frameworks: DevBench, SWE‑bench, AgentBench (nightly/offline fixtures where possible)
- Static Analysis: Semgrep (curated rules), CodeScene optional
- Education: GPTutor‑style explainers

Adoption Notes
- Default to offline/test fixtures in PR CI; allow live network in nightly for approved domains/workflows only.
- Ensure Terms/robots/ToS and privacy are respected for any online access; prefer official APIs.
- Capture provenance and summarize outcomes to research ledgers; link to ADRs if adopted.
