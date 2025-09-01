import logging, requests
from ..memory import KnowledgeGraphMemory
log = logging.getLogger("ingest_gs1_log")
def ingest_gs1_standards_log(kg: KnowledgeGraphMemory, url: str = "https://www.gs1.org/standards/log"):
    try:
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            log.warning("GS1 log fetch failed: %s", r.status_code); return
        kg.create_entity("GS1-Standards-Log", "gs1_log", [f"Fetched {len(r.text)} chars from {url}"])
    except Exception as e:
        log.warning("GS1 log ingest error: %s", e)
