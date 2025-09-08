"""Lightweight orchestrator shims for tests.

This repo variant keeps the full orchestrator graphs elsewhere. To satisfy
tests that import `orchestrator`, provide minimal stub implementations with the
expected interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class PlanResult:
    final: str
    steps: List[str]


class PlanToolReflect:
    def run(self, query: str) -> PlanResult:
        steps = [
            f"plan: decompose '{query}'",
            f"tool: run-research for '{query}'",
            f"reflect: verify '{query}'",
        ]
        return PlanResult(
            final=f"Final answer: stub-orchestrator for '{query}'", steps=steps
        )


class GraphRunner:
    def run(self, query: str) -> str:
        return f"Final answer: graph-runner for '{query}'"
