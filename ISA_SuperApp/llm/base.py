"""
Base classes and models for LLM providers in ISA SuperApp.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str
    content: str
    name: str | None = None


@dataclass
class ChatResponse:
    """Represents a chat response."""
    content: str
    model: str
    usage: dict[str, Any]
    choices: list[str] | None = None
    finish_reason: str | None = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> str:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> ChatResponse:
        """Perform chat completion."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Embed text into vector."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts into vectors."""
        pass
