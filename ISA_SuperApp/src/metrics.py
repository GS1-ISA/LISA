import time, threading
from collections import defaultdict


class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = {}
        self.lock = threading.Lock()

    def inc(self, name: str, value: int = 1):
        with self.lock:
            self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        with self.lock:
            self.gauges[name] = value

    def render_prom(self) -> str:
        lines = []
        with self.lock:
            for k, v in self.counters.items():
                lines.append(f"# TYPE {k} counter")
                lines.append(f"{k} {v}")
            for k, v in self.gauges.items():
                lines.append(f"# TYPE {k} gauge")
                lines.append(f"{k} {v}")
        return "\n".join(lines) + "\n"


METRICS = Metrics()
