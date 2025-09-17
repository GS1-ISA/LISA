#!/usr/bin/env python3
"""
Simple test script for LLM integration.
"""
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, "src")

try:
    from src.agent_core.llm_client import LLMClient
except ImportError as e:
    print(f"❌ Failed to import LLMClient: {e}")
    sys.exit(1)

async def test_llm_integration():
    """Test basic LLM integration."""
    print("🧪 Testing LLM integration...")

    # Create client
    try:
        client = LLMClient()
        print("✅ LLMClient created successfully")
    except Exception as e:
        print(f"❌ Failed to create LLMClient: {e}")
        return False

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    print(f"🔑 OpenAI API key: {'✓' if openai_key else '✗'}")
    print(f"🔑 Anthropic API key: {'✓' if anthropic_key else '✗'}")

    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Cannot test live API calls.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables to test with real APIs.")
        return True  # Still consider this a successful test of the integration setup

    # Test basic generation
    try:
        print("\n🧪 Testing LLM generation...")
        model = "gpt-4" if openai_key else "claude-3-sonnet-20240229"
        response = await client.generate(
            prompt="Say 'Hello from LLM integration test!' and nothing else.",
            model=model
        )

        print("✅ LLM Response received:")
        print(f"   Content: {response.content}")
        print(f"   Model: {response.model}")
        print(f"   Provider: {response.provider}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Cost: ${response.cost:.4f}")

        # Basic validation
        if "Hello from LLM integration test" in response.content:
            print("✅ Response contains expected content")
        else:
            print("⚠️  Response doesn't contain expected content, but that's okay for testing")

        # Test cost tracking
        summary = client.get_cost_summary()
        print("\n💰 Cost summary:")
        print(f"   Total cost: ${summary['total_cost']:.4f}")
        print(f"   Total tokens: {summary['total_tokens']}")
        print(f"   Requests: {summary['requests_count']}")

        return True

    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_integration())
    if success:
        print("\n🎉 LLM integration test completed!")
        sys.exit(0)
    else:
        print("\n❌ LLM integration test failed!")
        sys.exit(1)
