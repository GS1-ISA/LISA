#!/usr/bin/env python3
"""
Advisory cost telemetry stub.

Emits a JSON summary artifact of estimated monthly costs and warns at 80% of the
configured budget. This stub reads environment variables so it can run offline:

  - COST_MONTHLY_USD: float, current month spend estimate (default 0.0)
  - COST_BUDGET_USD: float, monthly budget (default 50.0)

Writes cost_report.json to the current working directory.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone


def main() -> int:
    spend = float(os.getenv("COST_MONTHLY_USD", "0.0"))
    budget = float(os.getenv("COST_BUDGET_USD", "50.0"))
    pct = (spend / budget * 100.0) if budget > 0 else 0.0
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "spend_usd": round(spend, 2),
        "budget_usd": round(budget, 2),
        "pct_of_budget": round(pct, 1),
        "advisory": True,
    }
    with open("cost_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report))
    if budget > 0 and pct >= 80.0:
        print(f"::warning::Cost at {pct:.1f}% of budget (${spend:.2f}/${budget:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

