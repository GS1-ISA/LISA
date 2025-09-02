import os
from fastapi.testclient import TestClient

from src.api_server import app


def test_ask_via_orchestrator_flag_graph(monkeypatch):
    # Prefer LG graph path; will fallback to stub if not available
    monkeypatch.setenv("ISA_USE_LANGGRAPH_ORCH", "1")
    c = TestClient(app)
    r = c.post("/ask", json={"question": "Hello orchestrator", "explain": True})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and isinstance(data["answer"], str)
    assert "meta" in data and isinstance(data["meta"], dict)
    # Either graph or stub meta depending on availability
    assert any(k in data["meta"] for k in ("orchestrator_graph", "orchestrator_stub"))

