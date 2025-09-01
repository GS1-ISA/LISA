import os


def test_dev_artifacts_exist():
    root = os.path.dirname(os.path.dirname(__file__))
    script = os.path.join(root, "scripts", "install_xcode_cli.sh")
    dev_setup = os.path.join(root, "DEV_SETUP.md")
    assert os.path.exists(script), f"Missing {script}"
    assert os.path.exists(dev_setup), f"Missing {dev_setup}"


def test_readme_mentions_dev_setup():
    root = os.path.dirname(os.path.dirname(__file__))
    readme = os.path.join(root, "README.md")
    with open(readme, "r", encoding="utf-8") as f:
        txt = f.read()
    assert "DEV_SETUP.md" in txt, "README.md should reference DEV_SETUP.md"
