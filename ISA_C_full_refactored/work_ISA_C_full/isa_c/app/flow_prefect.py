from __future__ import annotations

import logging
from datetime import datetime
from importlib import import_module

from isa_c.app.runner import get_default_modules

log = logging.getLogger("isa_c.flow")


def run_flow() -> None:
    try:
        from prefect import flow, task  # type: ignore
    except Exception as e:
        log.error("Prefect not installed, cannot run flow", extra={"err": str(e)})
        return

    @task
    def _run_mod(mod: str, since: str) -> None:
        m = import_module(f"isa_c.adapters.{mod}_adapter")
        df = m.run(datetime.fromisoformat(since))
        p = f"data/raw/{mod}/latest.csv"
        from pathlib import Path

        Path(f"data/raw/{mod}").mkdir(parents=True, exist_ok=True)
        df.to_csv(p, index=False)

    @flow(name="ISA_C Fetch Flow")
    def esg_flow(since: str = "1970-01-01"):
        for m in get_default_modules():
            _run_mod.submit(m, since)

    esg_flow()
