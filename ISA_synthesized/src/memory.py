import os, json, logging
from typing import List, Dict, Optional
from .logging_conf import setup_logging
from .utils.types import Entity, Relation

setup_logging()
log = logging.getLogger("memory")


class KnowledgeGraphMemory:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.getenv("ISA_MEMORY_FILE", "./memory.json")
        self._entities: Dict[str, Entity] = {}
        self._relations: List[Relation] = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._entities = {
                    k: Entity(
                        name=k,
                        type=v.get("type", "unknown"),
                        observations=v.get("observations", []),
                    )
                    for k, v in data.get("entities", {}).items()
                }
                self._relations = [Relation(**r) for r in data.get("relations", [])]
                log.info(
                    "Loaded memory: %d entities, %d relations",
                    len(self._entities),
                    len(self._relations),
                )
            except Exception:
                log.exception("Load failed; starting empty")
        else:
            log.info("Starting empty memory at %s", self.path)

    def _save(self):
        try:
            data = {
                "entities": {
                    n: {"type": e.type, "observations": e.observations}
                    for n, e in self._entities.items()
                },
                "relations": [r.__dict__ for r in self._relations],
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            log.exception("Save failed")

    def create_entity(self, name: str, type: str, observations: Optional[List[str]] = None):
        if name not in self._entities:
            self._entities[name] = Entity(name, type, observations or [])
            self._save()

    def add_observations(self, name: str, obs: List[str]):
        ent = self._entities.get(name)
        if not ent:
            self._entities[name] = ent = Entity(name, "unknown", [])
        for o in obs:
            if o not in ent.observations:
                ent.observations.append(o)
        self._save()

    def create_relation(self, subject: str, predicate: str, object: str):
        r = Relation(subject, predicate, object)
        if r.__dict__ not in [x.__dict__ for x in self._relations]:
            self._relations.append(r)
            self._save()

    def get_entity(self, name: str) -> Optional[Entity]:
        return self._entities.get(name)

    def query(self, term: str):
        t = term.lower()
        hits = []
        for n, e in self._entities.items():
            if t in n.lower() or t in e.type.lower() or any(t in o.lower() for o in e.observations):
                hits.append(e)
        return hits

    def dump_graph(self) -> Dict:
        return {
            "entities": {
                n: {"type": e.type, "observations": e.observations}
                for n, e in self._entities.items()
            },
            "relations": [r.__dict__ for r in self._relations],
        }
