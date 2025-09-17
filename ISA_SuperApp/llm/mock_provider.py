"""
Mock LLM provider for testing in ISA SuperApp.
"""

import random

from .base import ChatMessage, ChatResponse, LLMProvider


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(
        self,
        model: str = "mock-model",
        responses: list[str] | None = None,
        embedding_dimension: int = 5,
    ):
        """Initialize mock provider."""
        super().__init__(model)
        self.responses = responses or [
            "This is a mock response.",
            "Another mock response.",
            "Yet another mock response.",
        ]
        self.embedding_dimension = embedding_dimension

    async def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> str:
        """Generate mock text."""
        return random.choice(self.responses)

    async def chat(
        self,
        messages: list[ChatMessage],
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> ChatResponse:
        """Mock chat completion."""
        return ChatResponse(
            content=random.choice(self.responses),
            model=self.model,
            usage={"total_tokens": 30}
        )

    async def embed(self, text: str) -> list[float]:
        """Mock text embedding."""
        return [random.random() for _ in range(self.embedding_dimension)]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Mock batch embedding."""
        return [
            [random.random() for _ in range(self.embedding_dimension)]
            for _ in texts
        ]
