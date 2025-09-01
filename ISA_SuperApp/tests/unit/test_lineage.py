from pathlib import Path
import json

from src.utils.lineage import sha256_bytes, record_lineage


def test_sha256_and_record_lineage(tmp_path: Path):
    content = b"hello world"
    h = sha256_bytes(content)
    assert len(h) == 64

    log_path = tmp_path / "log.jsonl"
    rid = record_lineage(inputs={"sample": h}, outputs={"result": h}, log_path=log_path)
    assert log_path.exists()
    data = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert data and data[0]["run_id"] == rid
    assert data[0]["inputs"]["sample"] == h
