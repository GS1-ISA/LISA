from fastapi.testclient import TestClient

from src.api_server import app

client = TestClient(app)


def test_validate_detects_geo_precision_violation():
    payload = {"geo": {"lat": 52.1, "lon": 4.12345}}
    resp = client.post("/validate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert any(v["rule_id"] == "EUDR_GEO_PRECISION" for v in data.get("violations", []))


def test_validate_passes_on_good_precision():
    payload = {"geo": {"lat": 52.123456, "lon": 4.654321}}
    resp = client.post("/validate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("violations", []) == []
