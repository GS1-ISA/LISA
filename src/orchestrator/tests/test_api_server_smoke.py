from __future__ import annotations

from fastapi.testclient import TestClient

from src.api_server import app


def test_root_ok():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.text.strip() == "ok"


def test_metrics_exposes_prometheus_text():
    client = TestClient(app)
    # First hit a simple endpoint to ensure counters move
    client.get("/")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    # Basic sanity: default registry includes process_ and our histogram name
    assert "http_request_duration_seconds" in body
    assert "# HELP" in body

