"""
Tests for LLM provider functionality.
"""

import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from isa_superapp.core.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError
from isa_superapp.llm.anthropic_provider import AnthropicProvider
from isa_superapp.llm.base import ChatMessage, ChatResponse, LLMProvider
from isa_superapp.llm.mock_provider import MockProvider
from isa_superapp.llm.openai_provider import OpenAIProvider


class TestLLMProviderBase:
    """Test cases for LLMProvider base class."""

    def test_llm_provider_interface(self):
        """Test that LLMProvider defines the required interface."""
        # LLMProvider should be abstract
        with pytest.raises(TypeError):
            LLMProvider()

    def test_chat_message_model(self):
        """Test ChatMessage model."""
        message = ChatMessage(role="user", content="Hello, how are you?")

        assert message.role == "user"
        assert message.content == "Hello, how are you?"

        # Test with optional fields
        message_with_name = ChatMessage(
            role="assistant", content="I'm doing well!", name="Assistant"
        )

        assert message_with_name.name == "Assistant"

    def test_chat_response_model(self):
        """Test ChatResponse model."""
        response = ChatResponse(
            content="This is a response",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

        assert response.content == "This is a response"
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 30

        # Test with optional fields
        response_with_choices = ChatResponse(
            content="Response with choices",
            model="gpt-4",
            usage={"total_tokens": 50},
            choices=["choice1", "choice2"],
            finish_reason="stop",
        )

        assert len(response_with_choices.choices) == 2
        assert response_with_choices.finish_reason == "stop"


class TestOpenAIProvider:
    """Test cases for OpenAIProvider."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        client = Mock()

        # Mock chat completions
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Generated response"))]
        mock_completion.usage = Mock(
            prompt_tokens=10, completion_tokens=20, total_tokens=30
        )
        mock_completion.model = "gpt-4"

        client.chat.completions.create = Mock(return_value=mock_completion)

        # Mock embeddings
        mock_embedding = Mock()
        mock_embedding.data = [Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])]
        mock_embedding.usage = Mock(total_tokens=5)

        client.embeddings.create = Mock(return_value=mock_embedding)

        return client

    @pytest.mark.asyncio
    async def test_initialization(self, mock_openai_client):
        """Test OpenAI provider initialization."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(
                model="gpt-4", api_key="test-key", max_tokens=1000, temperature=0.7
            )

            assert provider.model == "gpt-4"
            assert provider.max_tokens == 1000
            assert provider.temperature == 0.7
            assert provider.client == mock_openai_client

    @pytest.mark.asyncio
    async def test_generate_text(self, mock_openai_client):
        """Test text generation."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            response = await provider.generate(
                prompt="Write a short story", max_tokens=150
            )

            assert response == "Generated response"
            mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_custom_parameters(self, mock_openai_client):
        """Test text generation with custom parameters."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(
                model="gpt-4", api_key="test-key", temperature=0.9, top_p=0.95
            )

            response = await provider.generate(
                prompt="Write a creative story", temperature=0.8, max_tokens=200
            )

            assert response == "Generated response"

            # Verify custom parameters were used
            call_args = mock_openai_client.chat.completions.create.call_args
            assert call_args[1]["temperature"] == 0.8
            assert call_args[1]["max_tokens"] == 200

    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_openai_client):
        """Test chat completion."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            messages = [
                ChatMessage(role="user", content="Hello!"),
                ChatMessage(role="assistant", content="Hi there!"),
                ChatMessage(role="user", content="How are you?"),
            ]

            response = await provider.chat(messages)

            assert isinstance(response, ChatResponse)
            assert response.content == "Generated response"
            assert response.model == "gpt-4"
            assert response.usage["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_embed_text(self, mock_openai_client):
        """Test text embedding."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            embedding = await provider.embed("This is a test sentence.")

            assert isinstance(embedding, list)
            assert len(embedding) == 5
            assert all(isinstance(x, float) for x in embedding)

            mock_openai_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, mock_openai_client):
        """Test embedding multiple texts."""
        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            texts = ["First text", "Second text", "Third text"]
            embeddings = await provider.embed_batch(texts)

            assert isinstance(embeddings, list)
            assert len(embeddings) == 3
            assert all(isinstance(emb, list) for emb in embeddings)
            assert all(len(emb) == 5 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_openai_client):
        """Test handling rate limit errors."""
        from openai import RateLimitError

        mock_openai_client.chat.completions.create.side_effect = RateLimitError(
            "Rate limit exceeded"
        )

        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            with pytest.raises(LLMRateLimitError):
                await provider.generate("Test prompt")

    @pytest.mark.asyncio
    async def test_timeout_error(self, mock_openai_client):
        """Test handling timeout errors."""
        import asyncio

        mock_openai_client.chat.completions.create.side_effect = asyncio.TimeoutError(
            "Request timed out"
        )

        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            with pytest.raises(LLMTimeoutError):
                await provider.generate("Test prompt")

    @pytest.mark.asyncio
    async def test_api_error(self, mock_openai_client):
        """Test handling API errors."""
        from openai import APIError

        mock_openai_client.chat.completions.create.side_effect = APIError(
            "API error occurred"
        )

        with patch(
            "isa_superapp.llm.openai_provider.OpenAI", return_value=mock_openai_client
        ):
            provider = OpenAIProvider(model="gpt-4", api_key="test-key")

            with pytest.raises(LLMError):
                await provider.generate("Test prompt")


class TestAnthropicProvider:
    """Test cases for AnthropicProvider."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        client = Mock()

        # Mock messages
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated response")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)
        mock_response.model = "claude-3-sonnet-20240229"

        client.messages.create = Mock(return_value=mock_response)

        return client

    @pytest.mark.asyncio
    async def test_initialization(self, mock_anthropic_client):
        """Test Anthropic provider initialization."""
        with patch(
            "isa_superapp.llm.anthropic_provider.Anthropic",
            return_value=mock_anthropic_client,
        ):
            provider = AnthropicProvider(
                model="claude-3-sonnet-20240229",
                api_key="test-key",
                max_tokens=1000,
                temperature=0.7,
            )

            assert provider.model == "claude-3-sonnet-20240229"
            assert provider.max_tokens == 1000
            assert provider.temperature == 0.7
            assert provider.client == mock_anthropic_client

    @pytest.mark.asyncio
    async def test_generate_text(self, mock_anthropic_client):
        """Test text generation with Anthropic."""
        with patch(
            "isa_superapp.llm.anthropic_provider.Anthropic",
            return_value=mock_anthropic_client,
        ):
            provider = AnthropicProvider(
                model="claude-3-sonnet-20240229", api_key="test-key"
            )

            response = await provider.generate(prompt="Write a poem", max_tokens=150)

            assert response == "Generated response"
            mock_anthropic_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_anthropic_client):
        """Test chat completion with Anthropic."""
        with patch(
            "isa_superapp.llm.anthropic_provider.Anthropic",
            return_value=mock_anthropic_client,
        ):
            provider = AnthropicProvider(
                model="claude-3-sonnet-20240229", api_key="test-key"
            )

            messages = [
                ChatMessage(role="user", content="Tell me a joke"),
                ChatMessage(
                    role="assistant", content="Why did the chicken cross the road?"
                ),
                ChatMessage(role="user", content="I don't know, why?"),
            ]

            response = await provider.chat(messages)

            assert isinstance(response, ChatResponse)
            assert response.content == "Generated response"
            assert response.model == "claude-3-sonnet-20240229"
            assert response.usage["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_anthropic_client):
        """Test handling rate limit errors with Anthropic."""
        from anthropic import RateLimitError

        mock_anthropic_client.messages.create.side_effect = RateLimitError(
            "Rate limit exceeded"
        )

        with patch(
            "isa_superapp.llm.anthropic_provider.Anthropic",
            return_value=mock_anthropic_client,
        ):
            provider = AnthropicProvider(
                model="claude-3-sonnet-20240229", api_key="test-key"
            )

            with pytest.raises(LLMRateLimitError):
                await provider.generate("Test prompt")


class TestMockProvider:
    """Test cases for MockProvider."""

    @pytest.fixture
    def provider(self):
        """Create a MockProvider instance."""
        return MockProvider()

    @pytest.mark.asyncio
    async def test_initialization(self, provider):
        """Test mock provider initialization."""
        assert provider.model == "mock-model"
        assert provider.responses is not None
        assert len(provider.responses) > 0

    @pytest.mark.asyncio
    async def test_generate_text(self, provider):
        """Test text generation with mock provider."""
        response = await provider.generate("Any prompt")

        assert isinstance(response, str)
        assert len(response) > 0
        assert response in provider.responses

    @pytest.mark.asyncio
    async def test_chat_completion(self, provider):
        """Test chat completion with mock provider."""
        messages = [
            ChatMessage(role="user", content="Hello!"),
            ChatMessage(role="assistant", content="Hi there!"),
        ]

        response = await provider.chat(messages)

        assert isinstance(response, ChatResponse)
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.model == "mock-model"
        assert response.usage["total_tokens"] > 0

    @pytest.mark.asyncio
    async def test_embed_text(self, provider):
        """Test text embedding with mock provider."""
        embedding = await provider.embed("Test text")

        assert isinstance(embedding, list)
        assert len(embedding) == provider.embedding_dimension
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_embed_batch(self, provider):
        """Test batch embedding with mock provider."""
        texts = ["First text", "Second text", "Third text"]
        embeddings = await provider.embed_batch(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == provider.embedding_dimension for emb in embeddings)

    @pytest.mark.asyncio
    async def test_custom_responses(self):
        """Test mock provider with custom responses."""
        custom_responses = [
            "Custom response 1",
            "Custom response 2",
            "Custom response 3",
        ]

        provider = MockProvider(responses=custom_responses)

        # Test multiple generations
        for i in range(3):
            response = await provider.generate("Test prompt")
            assert response in custom_responses

    @pytest.mark.asyncio
    async def test_custom_embedding_dimension(self):
        """Test mock provider with custom embedding dimension."""
        provider = MockProvider(embedding_dimension=10)

        embedding = await provider.embed("Test text")
        assert len(embedding) == 10


class TestLLMProviderFactory:
    """Test cases for LLM provider factory."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        from isa_superapp.llm.factory import create_llm_provider

        config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}

        with patch("isa_superapp.llm.openai_provider.OpenAI"):
            provider = create_llm_provider(config)
            assert isinstance(provider, OpenAIProvider)
            assert provider.model == "gpt-4"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        from isa_superapp.llm.factory import create_llm_provider

        config = {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "api_key": "test-key",
        }

        with patch("isa_superapp.llm.anthropic_provider.Anthropic"):
            provider = create_llm_provider(config)
            assert isinstance(provider, AnthropicProvider)
            assert provider.model == "claude-3-sonnet-20240229"

    def test_create_mock_provider(self):
        """Test creating Mock provider."""
        from isa_superapp.llm.factory import create_llm_provider

        config = {"provider": "mock", "model": "test-model"}

        provider = create_llm_provider(config)
        assert isinstance(provider, MockProvider)
        assert provider.model == "mock-model"

    def test_create_unknown_provider(self):
        """Test creating unknown provider type."""
        from isa_superapp.llm.factory import create_llm_provider

        config = {"provider": "unknown", "model": "unknown-model"}

        with pytest.raises(LLMError):
            create_llm_provider(config)


class TestLLMProviderIntegration:
    """Integration tests for LLM providers."""

    @pytest.mark.asyncio
    async def test_mock_provider_full_workflow(self):
        """Test complete workflow with mock provider."""
        provider = MockProvider()

        # Test text generation
        response = await provider.generate("Write a haiku about programming")
        assert isinstance(response, str)
        assert len(response) > 0

        # Test chat completion
        messages = [
            ChatMessage(role="user", content="What is Python?"),
            ChatMessage(role="assistant", content="Python is a programming language."),
            ChatMessage(role="user", content="What are its main features?"),
        ]

        chat_response = await provider.chat(messages)
        assert isinstance(chat_response, ChatResponse)
        assert isinstance(chat_response.content, str)
        assert len(chat_response.content) > 0

        # Test embedding
        embedding = await provider.embed("Python programming language")
        assert isinstance(embedding, list)
        assert all(isinstance(x, float) for x in embedding)

        # Test batch embedding
        texts = ["Python", "Java", "JavaScript"]
        embeddings = await provider.embed_batch(texts)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)


class TestLLMProviderPerformance:
    """Performance tests for LLM providers."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_mock_provider_performance(self):
        """Test mock provider performance."""
        import time

        provider = MockProvider()

        # Test generation performance
        num_requests = 100
        start_time = time.time()

        for i in range(num_requests):
            await provider.generate(f"Test prompt {i}")

        generation_time = time.time() - start_time

        # Test embedding performance
        start_time = time.time()

        for i in range(num_requests):
            await provider.embed(f"Test text {i}")

        embedding_time = time.time() - start_time

        # Performance assertions
        assert (
            generation_time < 5.0
        )  # Should handle 100 generations in less than 5 seconds
        assert (
            embedding_time < 5.0
        )  # Should handle 100 embeddings in less than 5 seconds

        print(f"Generated {num_requests} responses in {generation_time:.2f} seconds")
        print(f"Embedded {num_requests} texts in {embedding_time:.2f} seconds")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_chat_performance(self):
        """Test chat completion performance."""
        import time

        provider = MockProvider()

        messages = [
            ChatMessage(role="user", content="Hello!"),
            ChatMessage(role="assistant", content="Hi there!"),
            ChatMessage(role="user", content="How are you?"),
        ]

        num_requests = 50
        start_time = time.time()

        for i in range(num_requests):
            await provider.chat(messages)

        chat_time = time.time() - start_time

        assert chat_time < 3.0  # Should handle 50 chat requests in less than 3 seconds
        print(f"Completed {num_requests} chat requests in {chat_time:.2f} seconds")
