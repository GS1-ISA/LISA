from __future__ import annotations

from dataclasses import dataclass

from .graph import PlanToolReflect

try:
    # Optional: only used if available
    from langgraph.graph import END, START, StateGraph  # type: ignore
except Exception:  # pragma: no cover - optional import
    StateGraph = None  # type: ignore
    START = None  # type: ignore
    END = None  # type: ignore


@dataclass
class LGState:
    steps: list[str]
    goal: str
    final: str | None = None


def _plan(state: LGState) -> LGState:
    state.steps.append(f"plan: solve '{state.goal}'")
    return state


def _tool(state: LGState) -> LGState:
    out = state.goal.upper()[:32]
    state.steps.append(f"tool: {out}")
    return state


def _reflect(state: LGState) -> LGState:
    state.final = f"Final answer: {state.goal.lower()}"
    state.steps.append(f"reflect: {state.final}")
    return state


class GraphRunner:
    """Run a small plan→tool→reflect graph via LangGraph if present.

    Falls back to the package's deterministic stub when LangGraph is not installed.
    """

    def run(self, goal: str) -> str:
        if StateGraph is None:
            # Fallback to deterministic stub
            stub = PlanToolReflect().run(goal)
            return stub.final
        # Build simple graph
        g = StateGraph(LGState)  # type: ignore[misc]
        g.add_node("plan", _plan)
        g.add_node("tool", _tool)
        g.add_node("reflect", _reflect)
        g.add_edge(START, "plan")
        g.add_edge("plan", "tool")
        g.add_edge("tool", "reflect")
        g.add_edge("reflect", END)
        app = g.compile()
        state = LGState(steps=[], goal=goal)
        out = app.invoke(state)
        # LangGraph may return dict-like state; handle both
        if isinstance(out, dict):
            return out.get("final") or "Final answer:"
        return out.final or "Final answer:"
