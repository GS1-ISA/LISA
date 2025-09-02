from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def run_orchestrator_stub(task: str) -> Optional[str]:
    """Run the Plan→Tool→Reflect stub if enabled by ISA_USE_ORCHESTRATOR_STUB=1.

    Returns final string or None if not enabled/available.
    """
    if os.getenv("ISA_USE_ORCHESTRATOR_STUB", "0") != "1":
        return None
    # Ensure packages/orchestrator/src on path
    repo = Path(__file__).resolve().parents[3]
    pkg_src = repo / "packages" / "orchestrator" / "src"
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))
    try:
        from orchestrator import PlanToolReflect  # type: ignore
    except Exception:
        return None
    g = PlanToolReflect()
    res = g.run(task)
    return res.final


def run_orchestrator_graph(task: str) -> Optional[str]:
    """Run the LangGraph-based GraphRunner if enabled and available.

    Controlled by ISA_USE_LANGGRAPH_ORCH=1. Returns final string or None.
    """
    if os.getenv("ISA_USE_LANGGRAPH_ORCH", "0") != "1":
        return None
    repo = Path(__file__).resolve().parents[3]
    pkg_src = repo / "packages" / "orchestrator" / "src"
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))
    try:
        from orchestrator import GraphRunner  # type: ignore
    except Exception:
        return None
    runner = GraphRunner()
    return runner.run(task)
