from pathlib import Path

from scripts.research.index_docs import _load_json, _normalize_tr_entries, kg_from_normalized


def test_kg_from_normalized(tmp_path: Path):
    fixture = Path(__file__).parent / "fixtures" / "w3c_tr_index.json"
    data = _load_json(fixture)
    docs = _normalize_tr_entries(data)
    kg_path = tmp_path / "kg.json"
    n = kg_from_normalized(docs, kg_path)
    assert n >= 1 and kg_path.exists()
    txt = kg_path.read_text(encoding="utf-8")
    assert '"entities"' in txt and 'url:' in txt

