from __future__ import annotations
import importlib, logging, os
from datetime import datetime
from pathlib import Path
from isa_c.utils.settings import SETTINGS

log = logging.getLogger("isa_c.runner")

def get_default_modules() -> list[str]:
    return SETTINGS.default_modules

def run_module(mod: str, since: datetime) -> None:
    stamp = Path(f"data/raw/.{mod}.done")
    stamp.parent.mkdir(parents=True, exist_ok=True)
    if stamp.exists() and os.getenv("FORCE") != "1":
        log.info("skip up-to-date", extra={"module": mod})
        return
    pkg = importlib.import_module(f"isa_c.adapters.{mod}_adapter")
    df = pkg.run(since)
    outdir = Path(f"data/raw/{mod}")
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / "latest.csv"
    df.to_csv(p, index=False)
    stamp.touch()
    log.info("written", extra={"module": mod, "path": str(p)})

def run_pipeline(modules: list[str], since: datetime) -> None:
    log.info("start pipeline", extra={"modules": modules, "since": since.isoformat()})
    for m in modules:
        try:
            run_module(m, since)
        except Exception as e:  # noqa: BLE001
            log.exception("module failed", extra={"module": m, "error": str(e)})
    log.info("pipeline complete")
