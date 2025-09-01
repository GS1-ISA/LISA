import logging, os, sys
def setup_logging():
    level = os.getenv("ISA_LOG_LEVEL","INFO").upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", stream=sys.stdout)
