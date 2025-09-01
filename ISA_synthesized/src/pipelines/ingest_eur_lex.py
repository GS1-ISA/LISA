from ..memory import KnowledgeGraphMemory
def ingest_eurlex_esg(kg: KnowledgeGraphMemory, query:str="ESG", limit:int=3):
    kg.create_entity(f"EUR-LEX:{query}","eu_esg_search",[f"Query placeholder: {query}"])
