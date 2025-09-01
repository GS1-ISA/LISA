import pathlib
def test_electron_scaffold_exists():
    root = pathlib.Path(__file__).parents[2]
    assert (root / "desktop" / "electron" / "package.json").exists()
