from fastapi.testclient import TestClient

from src.api_server import app


def test_metrics_endpoint_ok():
    c = TestClient(app)
    r = c.get("/metrics")
    assert r.status_code == 200
    # basic shape assertions
    assert b"http_requests_total" in r.content


def test_ask_endpoint_ok():
    c = TestClient(app)
    r = c.post("/ask", json={"question": "What is ISA?", "explain": False})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
