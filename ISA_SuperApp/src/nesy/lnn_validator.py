from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RuleViolation:
    rule_id: str
    message: str
    path: Tuple[str, ...]


def _decimal_precision(value: str | float | int) -> Optional[int]:
    try:
        s = str(value)
        if "." in s:
            return len(s.split(".")[1])
        return 0
    except Exception:
        return None


def validate_eudr_geo_precision(record: Dict[str, Any], min_decimals: int = 6) -> List[RuleViolation]:
    """EUDR example: geolocation precision must be >= min_decimals.

    Accepts fields under common keys: ("geo", {"lat"|"latitude"}, {"lon"|"lng"|"longitude"}).
    Returns a list of violations; empty list means pass.
    """
    violations: List[RuleViolation] = []
    geo = record.get("geo") or record.get("location") or {}
    if not isinstance(geo, dict):
        return [
            RuleViolation(
                rule_id="EUDR_GEO_TYPE",
                message="Geo/location field must be an object",
                path=("geo",),
            )
        ]

    lat = geo.get("lat") or geo.get("latitude")
    lon = geo.get("lon") or geo.get("lng") or geo.get("longitude")

    def _check(name: str, value: Any) -> Optional[RuleViolation]:
        if value is None:
            return RuleViolation(
                rule_id="EUDR_GEO_MISSING",
                message=f"Missing {name}",
                path=("geo", name),
            )
        prec = _decimal_precision(value)
        if prec is None:
            return RuleViolation(
                rule_id="EUDR_GEO_FORMAT",
                message=f"{name} not a numeric value",
                path=("geo", name),
            )
        if prec < min_decimals:
            return RuleViolation(
                rule_id="EUDR_GEO_PRECISION",
                message=f"{name} precision {prec} < required {min_decimals}",
                path=("geo", name),
            )
        return None

    for name, value in (("lat", lat), ("lon", lon)):
        v = _check(name, value)
        if v:
            violations.append(v)

    return violations


def validate_record(record: Dict[str, Any]) -> List[RuleViolation]:
    """Run all available rules on a record and return violations.

    This is a minimal MVP using Python rules; future versions may dispatch to LNN.
    """
    violations: List[RuleViolation] = []
    violations.extend(validate_eudr_geo_precision(record))
    return violations

