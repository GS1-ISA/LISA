import os

os.environ["ISA_TEST_MODE"] = "1"
from fastapi.testclient import TestClient
from src.api_server import app


def test_end_to_end_flow():
    c = TestClient(app)
    c.post("/admin/ingest")
    c.post("/admin/reindex")
    r = c.post("/search", json={"query": "ESG regulation"})
    assert r.status_code == 200
    r = c.post("/doc/generate", json={"title": "ESG Brief", "outline": "Intro; Data; Actions"})
    assert r.status_code == 200 and "markdown" in r.json()
