from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

from isa_c.app.runner import get_default_modules, run_pipeline
from isa_c.utils.log import setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="ISA_C ESG Pipeline")
    parser.add_argument("--since", type=str, default="1970-01-01", help="ISO date cutoff")
    parser.add_argument("--flow", action="store_true", help="Run Prefect flow if available")
    args = parser.parse_args()

    setup_logging()

    if args.flow or os.getenv("USE_PREFECT") == "1":
        try:
            from isa_c.app.flow_prefect import run_flow
        except Exception as e:
            print(f"Falling back to runner; Prefect not available: {e}", file=sys.stderr)
        else:
            run_flow()
            return 0

    since = datetime.fromisoformat(args.since)
    modules = get_default_modules()
    run_pipeline(modules, since)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
