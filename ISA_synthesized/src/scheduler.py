import os, time, logging, argparse
import schedule
from .assistant import AssistantOrchestrator
from .pipelines.ingest_gs1_github import ingest_markdowns_to_memory as ingest_gs1
from .pipelines.ingest_eur_lex import ingest_eurlex_esg
from .pipelines.ingest_efrag import ingest_efrag_news
from .pipelines.ingest_gs1_standards_log import ingest_gs1_standards_log

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("scheduler")


def job_refresh(orch: AssistantOrchestrator):
    log.info("Job: ingest ESG + GS1 sources")
    try:
        ingest_eurlex_esg(orch.memory, "ESG", limit=5)
    except Exception as e:
        log.warning("EUR-Lex ingest failed: %s", e)
    try:
        ingest_efrag_news(orch.memory, limit=5)
    except Exception as e:
        log.warning("EFRAG ingest failed: %s", e)
    try:
        ingest_gs1_standards_log(orch.memory)
    except Exception as e:
        log.warning("GS1 log ingest failed: %s", e)
    try:
        orch.rebuild_index_from_memory()
        log.info("Vector index rebuilt.")
    except Exception as e:
        log.warning("Index rebuild failed: %s", e)


def main():
    parser = argparse.ArgumentParser(description="ISA Scheduler")
    parser.add_argument(
        "--interval-min",
        type=int,
        default=360,
        help="Run refresh job every N minutes (default 360)",
    )
    args = parser.parse_args()
    orch = AssistantOrchestrator()
    job_refresh(orch)
    schedule.every(args.interval_min).minutes.do(job_refresh, orch=orch)
    log.info("Scheduler started, interval=%d minutes", args.interval_min)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
