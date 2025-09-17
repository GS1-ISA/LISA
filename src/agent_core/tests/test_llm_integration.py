import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from src.agent_core.llm_client import LLMClient, LLMResponse


class TestLLMIntegration:
    """Test LLM integration functionality."""

    @pytest.fixture
    def llm_client(self):
        """Create LLM client for testing."""
        return LLMClient()

    @pytest.mark.asyncio
    async def test_llm_client_initialization(self, llm_client):
        """Test that LLM client initializes correctly."""
        assert llm_client is not None
        assert hasattr(llm_client, "openai_client")
        assert hasattr(llm_client, "anthropic_client")
        assert hasattr(llm_client, "cost_tracker")

    @pytest.mark.asyncio
    async def test_generate_with_mock_openai(self, llm_client):
        """Test LLM generation with mocked OpenAI response."""
        # Mock OpenAI client
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response from OpenAI"
        mock_response.usage.total_tokens = 100
        mock_openai.chat.completions.create.return_value = mock_response

        with patch.object(llm_client, "openai_client", mock_openai):
            response = await llm_client.generate(
                prompt="Test prompt",
                model="gpt-4"
            )

            assert isinstance(response, LLMResponse)
            assert response.content == "Test response from OpenAI"
            assert response.provider == "openai"
            assert response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_generate_with_mock_anthropic(self, llm_client):
        """Test LLM generation with mocked Anthropic response."""
        # Mock Anthropic client
        mock_anthropic = MagicMock()
        mock_response = MagicMock()
        mock_response.content[0].text = "Test response from Anthropic"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        mock_anthropic.messages.create.return_value = mock_response

        with patch.object(llm_client, "anthropic_client", mock_anthropic):
            with patch.object(llm_client, "openai_client", None):  # Force Anthropic
                response = await llm_client.generate(
                    prompt="Test prompt",
                    model="claude-3-sonnet-20240229"
                )

                assert isinstance(response, LLMResponse)
                assert response.content == "Test response from Anthropic"
                assert response.provider == "anthropic"
                assert response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_fallback_logic(self, llm_client):
        """Test fallback from OpenAI to Anthropic."""
        # Mock OpenAI to fail
        mock_openai = MagicMock()
        mock_openai.chat.completions.create.side_effect = Exception("OpenAI failed")

        # Mock Anthropic to succeed
        mock_anthropic = MagicMock()
        mock_response = MagicMock()
        mock_response.content[0].text = "Fallback response from Anthropic"
        mock_response.usage.input_tokens = 30
        mock_response.usage.output_tokens = 20
        mock_anthropic.messages.create.return_value = mock_response

        with patch.object(llm_client, "openai_client", mock_openai), \
             patch.object(llm_client, "anthropic_client", mock_anthropic):

            response = await llm_client.generate(
                prompt="Test prompt",
                model="gpt-4"
            )

            assert isinstance(response, LLMResponse)
            assert response.content == "Fallback response from Anthropic"
            assert response.provider == "anthropic"

    def test_cost_tracking(self, llm_client):
        """Test cost tracking functionality."""
        # Test initial state
        assert llm_client.cost_tracker.total_cost == 0.0
        assert llm_client.cost_tracker.total_tokens == 0
        assert llm_client.cost_tracker.requests_count == 0

        # Test cost summary
        summary = llm_client.get_cost_summary()
        assert "total_cost" in summary
        assert "total_tokens" in summary
        assert "requests_count" in summary

    @pytest.mark.asyncio
    async def test_rate_limiting(self, llm_client):
        """Test rate limiting functionality."""
        # This test would need actual API calls to test rate limiting
        # For now, just verify the rate limiter exists
        assert hasattr(llm_client, "rate_limiter")
        assert llm_client.rate_limiter is not None


if __name__ == "__main__":
    # Simple integration test that can be run directly
    async def run_integration_test():
        print("Testing LLM integration...")

        # Create client
        client = LLMClient()

        # Check if API keys are available
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not openai_key and not anthropic_key:
            print("⚠️  No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
            print("Skipping live API test.")
            return

        print(f"🔑 OpenAI key: {'✓' if openai_key else '✗'}")
        print(f"🔑 Anthropic key: {'✓' if anthropic_key else '✗'}")

        # Test simple generation
        try:
            print("\n🧪 Testing LLM generation...")
            response = await client.generate(
                prompt="Say 'Hello, World!' and nothing else.",
                model="gpt-4" if openai_key else "claude-3-sonnet-20240229"
            )

            print("✅ LLM Response received:")
            print(f"   Content: {response.content}")
            print(f"   Model: {response.model}")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost:.4f}")
            print(f"   Provider: {response.provider}")

            # Check if it's not a placeholder
            if "placeholder" in response.content.lower() or "test" in response.content.lower():
                print("⚠️  Response appears to be a placeholder or test response")
            else:
                print("✅ Response appears to be from actual LLM")

        except Exception as e:
            print(f"❌ LLM test failed: {e}")
            return False

        # Test cost tracking
        print("\n💰 Cost tracking:")
        summary = client.get_cost_summary()
        print(f"   Total cost: ${summary['total_cost']:.4f}")
        print(f"   Total tokens: {summary['total_tokens']}")
        print(f"   Requests: {summary['requests_count']}")

        print("\n🎉 LLM integration test completed successfully!")
        return True

    # Run the test
    asyncio.run(run_integration_test())
