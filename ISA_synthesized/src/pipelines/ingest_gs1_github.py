import os, requests
from ..memory import KnowledgeGraphMemory

GITHUB_API = "https://api.github.com"


def ingest_markdowns_to_memory(org: str, kg: KnowledgeGraphMemory, limit: int = 5):
    headers = {}
    tok = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    r = requests.get(f"{GITHUB_API}/orgs/{org}/repos?per_page=100", headers=headers, timeout=60)
    r.raise_for_status()
    for repo in r.json()[:limit]:
        name = repo.get("name", "")
        desc = repo.get("description") or ""
        kg.create_entity(name, "repo", [desc[:200]] if desc else [])
