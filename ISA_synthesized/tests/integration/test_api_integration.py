import os

os.environ["ISA_TEST_MODE"] = "1"
from fastapi.testclient import TestClient

from src.api_server import app


def test_basic_endpoints():
    c = TestClient(app)
    assert c.get("/ui/users").status_code == 200
    r = c.post("/ask", json={"question": "Test?", "explain": True})
    assert r.status_code == 200


def test_auth_and_metrics():
    c = TestClient(app)
    r = c.get("/ui/admin")
    assert r.status_code in (200, 403)
    r = c.get("/metrics")
    assert r.status_code == 200
