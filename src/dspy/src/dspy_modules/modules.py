from __future__ import annotations


class ClassifierStub:
    def __init__(self, rule: str = "contains:ok") -> None:
        self.rule = rule

    def compile(self) -> None:
        # No-op: deterministic stub
        return None

    def predict(self, text: str) -> str:
        if "ok" in text.lower():
            return "OK"
        return "OTHER"

