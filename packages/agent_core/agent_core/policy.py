from dataclasses import dataclass, field
from typing import List


@dataclass
class Policy:
    allowed_tools: List[str] = field(default_factory=lambda: ["ruff", "pytest", "mypy"])
    blocked_paths: List[str] = field(default_factory=list)
    autonomy_tier: int = 0  # 0=T0, 1=T1, 2=T2

