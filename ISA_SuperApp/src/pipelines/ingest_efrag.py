from ..memory import KnowledgeGraphMemory


def ingest_efrag_news(kg: KnowledgeGraphMemory, limit: int = 3):
    kg.create_entity(
        "EFRAG-News-Seed",
        "efrag_news",
        ["Seeded offline; replace with live scraper in production."],
    )
