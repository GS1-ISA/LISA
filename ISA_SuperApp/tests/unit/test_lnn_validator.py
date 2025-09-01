from src.nesy.lnn_validator import validate_eudr_geo_precision, validate_record


def test_validate_eudr_geo_precision_detects_low_precision():
    rec = {"geo": {"lat": 52.1, "lon": 4.12345}}
    violations = validate_eudr_geo_precision(rec, min_decimals=6)
    ids = {v.rule_id for v in violations}
    assert "EUDR_GEO_PRECISION" in ids


def test_validate_eudr_geo_precision_passes_with_six_decimals():
    rec = {"geo": {"lat": 52.123456, "lon": 4.654321}}
    violations = validate_eudr_geo_precision(rec, min_decimals=6)
    assert violations == []


def test_validate_record_runs_all_rules():
    rec = {"geo": {"latitude": "52.1234", "longitude": "4.123456"}}
    violations = validate_record(rec)
    # latitude has only 4 decimals
    assert any(v.rule_id == "EUDR_GEO_PRECISION" and v.path == ("geo", "lat") for v in violations) or any(
        v.rule_id == "EUDR_GEO_PRECISION" and v.path == ("geo", "latitude") for v in violations
    )

