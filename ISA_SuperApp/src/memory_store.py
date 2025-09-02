import json
import logging
import os
from typing import Dict, List, Optional

from .logging_conf import setup_logging
from .utils.types import Entity, Relation
from .memory.logs import MemoryEventLogger

setup_logging()
log = logging.getLogger("memory")


class KnowledgeGraphMemory:
    def __init__(self, path: Optional[str] = None, event_logger: Optional[MemoryEventLogger] = None):
        self.path = path or os.getenv("ISA_MEMORY_FILE", "./memory.json")
        self._entities: Dict[str, Entity] = {}
        self._relations: List[Relation] = []
        self._load()
        self._logger = event_logger or MemoryEventLogger()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
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
            self._logger.log("create_entity", session_id="-", content=name, meta={"type": type})

    def add_observations(self, name: str, obs: List[str]):
        ent = self._entities.get(name)
        if not ent:
            self._entities[name] = ent = Entity(name, "unknown", [])
        for o in obs:
            if o not in ent.observations:
                ent.observations.append(o)
        self._save()
        self._logger.log("add_observations", session_id="-", content=name, meta={"count": len(obs)})

    def create_relation(self, subject: str, predicate: str, object: str):
        r = Relation(subject, predicate, object)
        if r.__dict__ not in [x.__dict__ for x in self._relations]:
            self._relations.append(r)
            self._save()
            self._logger.log("create_relation", session_id="-", content=f"{subject}-{predicate}->{object}", meta={})

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

    # --- Privacy & Deletion ---
    def delete_entity(self, name: str, reason: str = "privacy") -> bool:
        if name not in self._entities:
            return False
        # Remove relations involving this entity
        before_rel = len(self._relations)
        self._relations = [r for r in self._relations if r.subject != name and r.object != name]
        rel_removed = before_rel - len(self._relations)
        del self._entities[name]
        self._save()
        self._logger.log("delete_entity", session_id="-", content=name, meta={"reason": reason, "relations_removed": rel_removed})
        return True

    def delete_observation(self, name: str, observation: str, reason: str = "privacy") -> bool:
        ent = self._entities.get(name)
        if not ent:
            return False
        try:
            ent.observations.remove(observation)
            self._save()
            self._logger.log("delete_observation", session_id="-", content=name, meta={"reason": reason})
            return True
        except ValueError:
            return False
