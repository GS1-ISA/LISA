import logging
import os

from packages.docs_provider.context7 import Context7Provider

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# A predefined list of top libraries to warm the cache for.
# In a more advanced implementation, this could be dynamically generated
# from the dependency map created in the reconnaissance phase.
TOP_LIBS = ["pytest", "ruff", "mypy", "httpx", "chromadb", "langgraph"]

QUERIES = [
    "getting started guide",
    "basic usage example",
    "configuration options",
    "api reference",
]


def main():
    """Warms the Context7 cache for a predefined list of libraries."""
    logging.info("Starting Context7 cache warming process...")

    if os.getenv("CONTEXT7_ENABLED", "0") != "1":
        logging.warning("CONTEXT7_ENABLED is not set to '1'. Cache warming skipped.")
        return

    provider = Context7Provider()

    for lib in TOP_LIBS:
        logging.info(f"--- Warming cache for library: {lib} ---")
        for query in QUERIES:
            try:
                provider.get_docs(query=query, libs=[lib])
            except Exception as e:
                logging.error(
                    f"Failed to warm cache for {lib} with query '{query}': {e}"
                )

    logging.info("Cache warming process complete.")


if __name__ == "__main__":
    main()
