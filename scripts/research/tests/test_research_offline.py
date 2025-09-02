from pathlib import Path

from scripts.research.fetcher import fetch
from scripts.research.extract import html_to_text


def test_fetch_local_file_and_extract(tmp_path: Path):
    html = """
    <html><head><title>T</title><style>body{}</style></head>
    <body><h1>Hello</h1><script>var x=1;</script><p>World!</p></body></html>
    """
    f = tmp_path / "sample.html"
    f.write_text(html, encoding="utf-8")
    data, rec = fetch(str(f))
    assert data is not None and rec.ok and rec.from_cache
    text = html_to_text(data.decode("utf-8"))
    assert text == "T Hello World!"

