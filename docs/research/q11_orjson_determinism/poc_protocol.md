Title: Micro‑POC Protocol — Q11 Determinism (orjson vs stdlib)
Last updated: 2025-09-02

Question/Hypothesis: orjson + explicit newline/encoding yields stable snapshots across OS/Python with ≤5% overhead.
Success Metrics: 100% snapshot match across OS/Python; perf delta ≤5%
Dataset & Splits: canonical samples; edge cases (Unicode, large lists)
Environment: devcontainer (pinned), Python 3.11/3.12; OS notes
Procedure: run snapshot suite stdlib vs orjson; compare outputs and timings
Safety/Legal: N/A
Results: (TBD)
Replication Notes: (TBD)
Decision: (TBD)
Follow‑ups: (TBD)

