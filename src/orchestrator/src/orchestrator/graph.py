from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass


@dataclass
class OrchestratorResult:
    steps: list[str]
    final: str


class PlanToolReflect:
    """Tiny, dependency-free stub for plan→tool→reflect.

    Deterministic behavior for CI smoke only.
    """

    def run(self, goal: str) -> OrchestratorResult:
        t0 = time.perf_counter()
        # Optional path: delegate to agent_core via adapter if enabled
        if (
            os.getenv("ORCHESTRATOR_USE_AGENT_CORE", "0") == "1"
        ):  # pragma: no cover - integration mode
            try:
                from .agent_core_adapter import (
                    OrchestratorAgentRunner,
                )  # local import to avoid hard dep

                res = OrchestratorAgentRunner().run(goal)
                # Normalize to OrchestratorResult
                out = OrchestratorResult(steps=res.steps, final=res.final)
                self._maybe_log_perf(t0, "adapter")
                return out
            except Exception:
                # Fallback to deterministic stub
                pass
        steps: list[str] = []
        steps.append(f"plan: solve '{goal}' with a simple tool")
        tool_out = self._tool(goal)
        steps.append(f"tool: {tool_out}")
        reflect = self._reflect(tool_out)
        steps.append(f"reflect: {reflect}")
        out = OrchestratorResult(steps=steps, final=reflect)
        self._maybe_log_perf(t0, "stub")
        return out

    def _tool(self, goal: str) -> str:
        # Minimal deterministic transform
        return goal.upper()[:32]

    def _reflect(self, tool_out: str) -> str:
        return f"Final answer: {tool_out.lower()}"

    def _maybe_log_perf(self, t0: float, mode: str) -> None:
        """Optionally append a JSONL perf record when PERF_LOG is set."""
        path = os.getenv("PERF_LOG")
        if not path:
            return
        try:
            rec = {
                "ts": time.time(),
                "component": "orchestrator.PlanToolReflect",
                "mode": mode,
                "duration_s": time.perf_counter() - t0,
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        except Exception:
            return
