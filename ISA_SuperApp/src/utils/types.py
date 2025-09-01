from dataclasses import dataclass, field


@dataclass
class Entity:
    name: str
    type: str
    observations: list[str] = field(default_factory=list)


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
    thoughts: list[Thought]
    final_answer: str
