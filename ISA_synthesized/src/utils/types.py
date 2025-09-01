from dataclasses import dataclass, field
from typing import List


@dataclass
class Entity:
    name: str
    type: str
    observations: List[str] = field(default_factory=list)


@dataclass
class Relation:
    subject: str
    predicate: str
    object: str


@dataclass
class Thought:
    content: str
    number: int


@dataclass
class ReasoningResult:
    thoughts: List[Thought]
    final_answer: str
