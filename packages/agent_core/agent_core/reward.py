from typing import Dict, Any


class RewardAggregator:
    """Computes a simple reward score (skeleton)."""

    def score(self, signals: Dict[str, Any]) -> float:
        score = 0.0
        if signals.get("tests_pass"):
            score += 3
        if signals.get("coverage_delta", 0) > 0:
            score += signals["coverage_delta"] * 0.5
        if signals.get("revert"):
            score -= 4
        return score
