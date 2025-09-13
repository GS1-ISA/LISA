#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path.cwd()
CATALOG = ROOT / "docs" / "audit" / "rule_catalog.csv"


COMPONENTS = [
    (
        "Planner",
        "packages/agent_core/agent_core/planner.py",
        ["planner", "plan", "operational loop"],
    ),
    (
        "Builder",
        "packages/agent_core/agent_core/builder.py",
        ["builder", "apply", "diff"],
    ),
    (
        "Verifier",
        "packages/agent_core/agent_core/verifier.py",
        ["verifier", "gate", "ci", "lint", "type", "test"],
    ),
    (
        "Critic",
        "packages/agent_core/agent_core/critic.py",
        ["critic", "reflect", "review"],
    ),
    (
        "RewardAggregator",
        "packages/agent_core/agent_core/reward.py",
        ["reward", "score"],
    ),
    (
        "TraceLogger",
        "packages/agent_core/agent_core/memory.py",
        ["trace", "memory", "jsonl"],
    ),
    (
        "Policy",
        "packages/agent_core/agent_core/policy.py",
        ["policy", "allowlist", "autonomy"],
    ),
    ("Orchestrator", "ISA_SuperApp/src/assistant.py", ["orchestrator", "assistant"]),
]


def load_rules() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with CATALOG.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def rules_for_keywords(rows: list[dict[str, str]], keywords: list[str]) -> list[str]:
    out: list[str] = []
    for row in rows:
        text = (row.get("Title", "") + " " + row.get("SourceFile", "")).lower()
        if any(k in text for k in keywords):
            out.append(row["RuleID"])
    return sorted(set(out))


def write_mermaid(path: Path) -> None:
    g = """
flowchart LR
  User(Developer/User) --> Planner
  Planner --> Builder
  Builder --> Verifier
  Verifier -- pass --> Merge[Branch/PR Merge]
  Verifier -- fail --> Critic
  Critic --> Planner
  Builder --> TraceLogger
  Verifier --> TraceLogger
  Critic --> RewardAggregator
  RewardAggregator --> Planner
  Planner --> Policy
  subgraph Agent Core
    Planner
    Builder
    Verifier
    Critic
    RewardAggregator
    TraceLogger
    Policy
  end
  Orchestrator -. invokes .-> Planner
  Orchestrator -. invokes .-> Builder
  Orchestrator -. invokes .-> Verifier
""".strip()
    path.write_text(g + "\n", encoding="utf-8")


def main() -> int:
    rules = load_rules()
    linkage_csv = ROOT / "docs" / "audit" / "agent_linkage.csv"
    linkage_csv.parent.mkdir(parents=True, exist_ok=True)
    with linkage_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Component", "Source", "Exists", "RuleIDs"])
        for name, src, kws in COMPONENTS:
            p = ROOT / src
            rule_ids = rules_for_keywords(rules, kws + [name.lower()])
            w.writerow([name, src, str(p.exists()), ";".join(rule_ids)])

    mermaid = ROOT / "docs" / "audit" / "agent_loop_map.mermaid"
    write_mermaid(mermaid)
    print(f"Wrote {linkage_csv} and {mermaid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
