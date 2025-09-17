from infra.rag.ingest.splitter import split_text


def test_splitter_deterministic_and_bounds():
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    chunks = split_text(text, max_len=40)
    assert all(len(c) <= 40 for c in chunks)
    # Stable re-run
    assert chunks == split_text(text, max_len=40)
