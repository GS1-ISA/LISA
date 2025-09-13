import logging

from packages.docs_provider.src.docs_provider.cache import DiskCache

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """Purges the documentation provider's on-disk cache."""
    logging.info("Purging the documentation provider cache...")
    try:
        cache = DiskCache()
        cache.purge()
        logging.info(f"Successfully purged cache at: {cache.cache_dir}")
    except Exception as e:
        logging.error(f"An error occurred while purging the cache: {e}")


if __name__ == "__main__":
    main()
