from pathlib import Path

from scripts.research.connectors.federal_register import load_fixture, normalize_fr_entries


def test_federal_register_fixture_normalization():
    p = Path(__file__).parent / "fixtures" / "federal_register_sample.json"
    data = load_fixture(p)
    docs = normalize_fr_entries(data)
    assert len(docs) == 2
    assert docs[0].html_url.startswith("https://www.federalregister.gov/")
    assert docs[0].publication_date.count("-") == 2

