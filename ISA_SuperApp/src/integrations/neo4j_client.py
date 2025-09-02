import logging
import os
from typing import Tuple

log = logging.getLogger("neo4j_client")


def get_config():
    return (
        os.getenv("NEO4J_URI") or "neo4j://localhost:7687",
        os.getenv("NEO4J_USERNAME") or "neo4j",
        os.getenv("NEO4J_PASSWORD") or "",
    )


def verify_connection() -> Tuple[bool, str]:
    try:
        from neo4j import GraphDatabase
    except Exception:
        return False, "neo4j driver not installed"
    uri, u, p = get_config()
    try:
        driver = GraphDatabase.driver(uri, auth=(u, p))
        with driver.session() as s:
            rec = s.run("RETURN 1 AS ok").single()
            ok = False
            try:
                ok = bool(rec is not None and rec["ok"] == 1)
            except Exception:
                ok = False
            return ok, f"Connected to {uri}"
    except Exception as e:
        return False, f"Connection error: {e}"
