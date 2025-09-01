from dataclasses import dataclass, field


@dataclass
class Policy:
    allowed_tools: list[str] = field(default_factory=lambda: ["ruff", "pytest", "mypy"])
    blocked_paths: list[str] = field(default_factory=list)
    autonomy_tier: int = 0  # 0=T0, 1=T1, 2=T2
