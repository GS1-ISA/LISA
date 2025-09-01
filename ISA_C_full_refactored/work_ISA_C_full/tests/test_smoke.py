
def test_import_package():
    import importlib
    assert importlib.import_module("isa_c") is not None
