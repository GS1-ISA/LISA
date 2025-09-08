from pathlib import Path

from scripts.research.index_docs import index_fr_fixture


def test_index_fr_fixture_builds_vector_index(tmp_path: Path):
    fixture = Path(__file__).parent / "fixtures" / "federal_register_sample.json"
    storage = tmp_path / "research_index_fr.json"
    n = index_fr_fixture(fixture, storage)
    assert n >= 1 and storage.exists()
    data = storage.read_text(encoding="utf-8")
    assert '"docs"' in data
