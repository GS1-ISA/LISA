from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore

POLICY_PATH = Path(".agent/policy.yaml")


@dataclass
class PRContext:
    changed_files: list[str]
    labels: list[str]


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def is_significant(
    changed: list[str], threshold_files: int = 15
) -> bool:
    # LOC threshold requires CI context; here we use file count only
    return len(changed) > threshold_files


def next_job(pr: PRContext, policy: dict[str, Any] | None = None) -> str | None:
    pol = policy or load_policy()
    for job in pol.get("jobs", []):
        cond = job.get("when", {})
        any_globs = list(cond.get("changed_paths_any", []))
        if any_globs and any(
            any(fnmatch.fnmatch(f, g) for g in any_globs) for f in pr.changed_files
        ):
            return job["id"]
        if cond.get("significance") and is_significant(pr.changed_files):
            return job["id"]
    return None


def is_waiver_needed(
    step_id: str, policy: dict[str, Any] | None = None
) -> bool:
    pol = policy or load_policy()
    for job in pol.get("jobs", []):
        if job.get("id") == step_id:
            return bool(job.get("requires_waiver", False))
    return False


def kill_switch_active(pr: PRContext, policy: dict[str, Any] | None = None) -> bool:
    pol = policy or load_policy()
    label = pol.get("kill_switch", {}).get("label", "policy/agent-blocked")
    return label in pr.labels
