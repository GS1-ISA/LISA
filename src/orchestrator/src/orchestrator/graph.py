from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class OrchestratorResult:
    steps: List[str]
    final: str


class PlanToolReflect:
    """Tiny, dependency-free stub for plan→tool→reflect.

    Deterministic behavior for CI smoke only.
    """

    def run(self, goal: str) -> OrchestratorResult:
        steps: list[str] = []
        steps.append(f"plan: solve '{goal}' with a simple tool")
        tool_out = self._tool(goal)
        steps.append(f"tool: {tool_out}")
        reflect = self._reflect(tool_out)
        steps.append(f"reflect: {reflect}")
        return OrchestratorResult(steps=steps, final=reflect)

    def _tool(self, goal: str) -> str:
        # Minimal deterministic transform
        return goal.upper()[:32]

    def _reflect(self, tool_out: str) -> str:
        return f"Final answer: {tool_out.lower()}"
