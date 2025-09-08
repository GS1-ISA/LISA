Last updated: 2025-09-02
Agent Core (Skeleton)

Purpose: Provide minimal, typed modules for the agent roles and policies.

Modules
- planner.py — plans steps and tools
- builder.py — applies patches and executes tools
- verifier.py — runs gates
- critic.py — structured review
- reward.py — aggregates rewards
- memory.py — JSONL traces and summaries
- policy.py — allowlists, limits, autonomy tiers

Note: This is a placeholder scaffold; logic will be implemented incrementally.
