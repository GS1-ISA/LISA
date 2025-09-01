from pathlib import Path

from src.utils.json_canonical import canonical_dumps


def test_snapshot_canonical_sample_matches():
    # Build the same object we snapshot
    obj = {"b": 2, "a": 1, "nested": {"y": [3, 2, 1], "x": "ä"}}
    expected = Path("tests/snapshots/canonical_sample.json").read_text(encoding="utf-8")
    actual = canonical_dumps(obj) + "\n"
    assert actual == expected

