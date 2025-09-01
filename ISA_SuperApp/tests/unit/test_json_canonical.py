from src.utils.json_canonical import canonical_dumps


def test_canonical_dumps_is_deterministic():
    obj = {"b": 2, "a": 1, "nested": {"y": [3, 2, 1], "x": "ä"}}
    first = canonical_dumps(obj)
    second = canonical_dumps(obj)
    assert first == second
    # Keys sorted: 'a' comes before 'b' and 'nested'
    assert first.startswith('{"a":1,')
