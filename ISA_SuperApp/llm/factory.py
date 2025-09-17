"""
Factory for creating LLM providers in ISA SuperApp.
"""

from typing import Any

from isa_superapp.core.exceptions import LLMError

from .anthropic_provider import AnthropicProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider


def create_llm_provider(config: dict[str, Any]) -> Any:
    """Create an LLM provider based on configuration."""
    provider_type = config.get("provider", "").lower()

    if provider_type == "openai":
        return OpenAIProvider(
            model=config.get("model", "gpt-4"),
            api_key=config.get("api_key"),
            max_tokens=config.get("max_tokens", 1000),
            temperature=config.get("temperature", 0.7),
        )
    elif provider_type == "anthropic":
        return AnthropicProvider(
            model=config.get("model", "claude-3-sonnet-20240229"),
            api_key=config.get("api_key"),
            max_tokens=config.get("max_tokens", 1000),
            temperature=config.get("temperature", 0.7),
        )
    elif provider_type == "mock":
        return MockProvider(
            model=config.get("model", "mock-model"),
            responses=config.get("responses"),
            embedding_dimension=config.get("embedding_dimension", 5),
        )
    else:
        raise LLMError(f"Unknown LLM provider type: {provider_type}")
