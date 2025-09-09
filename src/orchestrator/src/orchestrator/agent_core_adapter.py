from __future__ import annotations

"""
Adapter bridging the orchestrator package to agent_core agents.

Defaults to lightweight stubs if agent_core or external deps are unavailable so
that importing this module never pulls heavy optional dependencies in CI.
"""

from dataclasses import dataclass
from typing import List


try:  # pragma: no cover - optional dependency boundary
    from src.agent_core.agents.planner import PlannerAgent
    from src.agent_core.agents.researcher import ResearcherAgent
    from src.agent_core.agents.synthesizer import SynthesizerAgent
    from src.agent_core.memory.rag_store import RAGMemory
    from src.tools.web_research import WebResearchTool

    _AGENT_CORE_AVAILABLE = True
except Exception:  # pragma: no cover - optional import path
    _AGENT_CORE_AVAILABLE = False


@dataclass
class AgentCoreResult:
    steps: List[str]
    final: str


class OrchestratorAgentRunner:
    """Run a simple Planner→Researcher→Synthesizer pipeline.

    If agent_core is not importable, produces a deterministic stub result to
    keep tests stable in minimal environments.
    """

    def run(self, goal: str) -> AgentCoreResult:
        if not _AGENT_CORE_AVAILABLE:
            steps = [
                f"plan: stub for '{goal}'",
                f"research: stub-web",
                f"synthesize: stub-report",
            ]
            return AgentCoreResult(steps=steps, final=f"Final answer: {goal.lower()}")

        # Real path using agent_core with default light components
        planner = PlannerAgent()  # NullProvider by default
        plan = planner.run(goal)
        steps: List[str] = [f"plan: {len(plan)} steps"]

        researcher = ResearcherAgent(WebResearchTool(), RAGMemory())
        research_summary = researcher.run(f"search for {goal}", max_steps=2)
        steps.append("research: completed")

        synthesizer = SynthesizerAgent()
        report = synthesizer.run(goal, researcher.rag_memory)
        steps.append("synthesize: completed")
        return AgentCoreResult(
            steps=steps, final=report.splitlines()[0] if report else "Final answer:"
        )
