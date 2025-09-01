from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class PlanStep:
    description: str
    tools: List[str]


class Planner:
    """Builds and updates plans (skeleton)."""

    def plan(self, goal: str, context: Dict[str, Any]) -> List[PlanStep]:
        return [PlanStep(description=f"Plan for: {goal}", tools=["ruff", "pytest"])]
