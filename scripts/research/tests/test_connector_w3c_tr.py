from pathlib import Path

from scripts.research.connectors.w3c_tr import load_fixture, normalize_tr_entries


def test_w3c_tr_fixture_normalization():
    p = Path(__file__).parent / "fixtures" / "w3c_tr_index.json"
    data = load_fixture(p)
    docs = normalize_tr_entries(data)
    assert len(docs) == 2
    assert docs[0].url.startswith("https://www.w3.org/TR/")
    assert docs[0].date.count("-") == 2  # YYYY-MM-DD
