from __future__ import annotations

import os
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
        # Optional path: delegate to agent_core via adapter if enabled
        if os.getenv("ORCHESTRATOR_USE_AGENT_CORE", "0") == "1":  # pragma: no cover - integration mode
            try:
                from .agent_core_adapter import OrchestratorAgentRunner  # local import to avoid hard dep

                res = OrchestratorAgentRunner().run(goal)
                # Normalize to OrchestratorResult
                return OrchestratorResult(steps=res.steps, final=res.final)
            except Exception:
                # Fallback to deterministic stub
                pass
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
