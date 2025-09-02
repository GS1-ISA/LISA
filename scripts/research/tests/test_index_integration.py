from pathlib import Path

from scripts.research.index_docs import index_tr_fixture


def test_index_tr_fixture_builds_vector_index(tmp_path: Path):
    # Use fixture JSON and a temp storage path
    fixture = Path(__file__).parent / "fixtures" / "w3c_tr_index.json"
    storage = tmp_path / "research_index.json"
    n = index_tr_fixture(fixture, storage)
    assert n >= 1 and storage.exists()
    # Sanity load of the storage to ensure JSON structure is present
    data = storage.read_text(encoding="utf-8")
    assert '"docs"' in data

