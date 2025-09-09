from infra.rag.ingest.splitter import split_text


def test_splitter_perf_benchmark(benchmark):
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
        "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
        "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    )

    def run():
        split_text(text, max_len=80)

    benchmark(run)

