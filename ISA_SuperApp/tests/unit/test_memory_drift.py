from src.memory.drift import compute_drift, check_drift


def test_memory_drift_basic():
    a = "policy data esg csrd"
    b = "policy data esg csrd"
    c = "unrelated content without overlap"
    assert compute_drift(a, b) < 0.05
    assert compute_drift(a, c) > 0.8
    flag, d = check_drift(a, c, threshold=0.7)
    assert flag and d > 0.7

