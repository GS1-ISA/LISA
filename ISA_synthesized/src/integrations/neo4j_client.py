import os, logging
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
            return (rec and rec["ok"] == 1), f"Connected to {uri}"
    except Exception as e:
        return False, f"Connection error: {e}"
