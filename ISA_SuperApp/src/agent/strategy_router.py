from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict


ARMS_FILE = Path("agent/outcomes/arms.json")
ARMS_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class ArmStats:
    count: int = 0
    success: int = 0
    reward_sum: float = 0.0


def load_stats() -> Dict[str, ArmStats]:
    if not ARMS_FILE.exists():
        return {}
    try:
        raw = json.loads(ARMS_FILE.read_text(encoding="utf-8"))
        return {k: ArmStats(**v) for k, v in raw.items()}
    except Exception:
        return {}


def save_stats(stats: Dict[str, ArmStats]) -> None:
    ARMS_FILE.write_text(
        json.dumps({k: asdict(v) for k, v in stats.items()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


STRATEGIES = ["test_first", "scaffold_repair", "refactor_then_feature"]


def choose_strategy(task_kind: str, epsilon: float = 0.15) -> str:
    """Epsilon-greedy selection among strategies.

    task_kind reserved for future contextual policies.
    """
    stats = load_stats()
    # explore
    if random.random() < epsilon:
        return random.choice(STRATEGIES)
    # exploit by avg reward
    best = None
    best_avg = -1e9
    for s in STRATEGIES:
        st = stats.get(s, ArmStats())
        avg = (st.reward_sum / st.count) if st.count else 0.0
        if avg > best_avg:
            best = s; best_avg = avg
    return best or STRATEGIES[0]


def update_reward(strategy: str, success: bool, coverage_delta: float = 0.0, type_errors: int = 0) -> None:
    """Update bandit reward model.

    Reward heuristic: base +2 for success, -2 otherwise; +coverage_delta; - type_errors*0.5.
    """
    stats = load_stats()
    st = stats.get(strategy, ArmStats())
    st.count += 1
    if success:
        st.success += 1
    reward = (2.0 if success else -2.0) + float(coverage_delta) - 0.5 * float(type_errors)
    st.reward_sum += reward
    stats[strategy] = st
    save_stats(stats)

