from dataclasses import dataclass
from typing import Any


@dataclass
class PlanStep:
    description: str
    tools: list[str]


class Planner:
    """Builds and updates plans (skeleton)."""

    def plan(self, goal: str, context: dict[str, Any]) -> list[PlanStep]:
        return [PlanStep(description=f"Plan for: {goal}", tools=["ruff", "pytest"])]
