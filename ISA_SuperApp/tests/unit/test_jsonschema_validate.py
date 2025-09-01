from typing import Any

import pytest

from src.utils.jsonschema_validate import compile_schema

SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string"},
    },
    "required": ["id", "name"],
    "additionalProperties": False,
}


def test_fastjsonschema_compiled_validator_validates_ok():
    try:
        validate = compile_schema(SCHEMA)
    except RuntimeError:
        pytest.skip("fastjsonschema not installed")
    validate({"id": 1, "name": "x"})
    with pytest.raises(Exception):
        validate({"id": 0, "name": "x"})
