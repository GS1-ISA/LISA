#!/usr/bin/env python3
"""
Test script for OpenRouter free model integration in ISA_D.
This script tests all the free models and ISA-specific use cases.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent_core.llm_client import get_openrouter_free_client, test_free_models


async def test_isa_compliance_scenarios():
    """Test ISA-specific compliance scenarios with free models."""
    print("🧪 Testing ISA Compliance Scenarios with Free Models")
    print("=" * 60)

    client = get_openrouter_free_client()

    test_cases = [
        {
            "name": "EU CSRD Mapping",
            "query": "Map EU Corporate Sustainability Reporting Directive (CSRD) Article 8 requirements to GDSN attributes for retail sector compliance",
            "expected_model": "primary"  # Should use Gemini 2.5 Flash for compliance analysis
        },
        {
            "name": "Standards Gap Analysis",
            "query": "Analyze compliance gaps between current GDSN implementation and EU ESG reporting requirements for Dutch manufacturers",
            "expected_model": "primary"  # Complex compliance analysis
        },
        {
            "name": "Regulatory Document Processing",
            "query": "Extract key compliance requirements from EU Regulation 2023/1234 on sustainable products",
            "expected_model": "long_context"  # Long regulatory document processing
        },
        {
            "name": "GS1 Standards Mapping",
            "query": "Create attribute mapping table for GS1 GDSN product sustainability fields to EU taxonomy requirements",
            "expected_model": "fast"  # Structured output generation
        },
        {
            "name": "Circular Economy Analysis",
            "query": "Explain the relationship between circular economy requirements and GS1 traceability standards",
            "expected_model": "reasoning"  # Step-by-step reasoning
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query'][:80]}...")

        try:
            messages = [{"role": "user", "content": test_case["query"]}]
            result = client.chat_completion(messages)

            print(f"✅ Model Used: {result['model_used']}")
            print(f"📊 Tokens: {result['usage']['total_tokens']}")
            print("💰 Cost: FREE")
            print(f"📝 Response Preview: {result['content'][:150]}...")

            # Verify model selection logic
            if test_case["expected_model"] in result["model_used"].lower():
                print(f"✅ Correct model selected for {test_case['expected_model']} scenario")
            else:
                print("⚠️  Model selection may need optimization")

        except Exception as e:
            print(f"❌ Error: {e}")

async def test_rate_limiting():
    """Test rate limiting behavior."""
    print("\n\n⏱️  Testing Rate Limiting")
    print("=" * 30)

    client = get_openrouter_free_client()

    # Test rapid requests to see rate limiting in action
    test_query = "Quick test query for rate limiting"
    messages = [{"role": "user", "content": test_query}]

    for i in range(5):
        try:
            result = client.chat_completion(messages)
            print(f"Request {i+1}: ✅ {result['model_used']} - {result['usage']['total_tokens']} tokens")
        except Exception as e:
            print(f"Request {i+1}: ❌ Rate limited or error: {e}")

async def test_model_fallback():
    """Test model fallback behavior."""
    print("\n\n🔄 Testing Model Fallback")
    print("=" * 30)

    client = get_openrouter_free_client()

    # Test with a potentially problematic query
    problematic_query = "This is a test query that might cause issues with some models but should work with fallback"
    messages = [{"role": "user", "content": problematic_query}]

    try:
        result = client.chat_completion(messages, model="nonexistent-model:free")
        print(f"✅ Fallback successful: {result['model_used']}")
    except Exception as e:
        print(f"❌ Fallback failed: {e}")

async def test_cost_tracking():
    """Test cost tracking functionality."""
    print("\n\n💰 Testing Cost Tracking")
    print("=" * 30)

    client = get_openrouter_free_client()

    # Make a few requests
    test_queries = [
        "Test cost tracking query 1",
        "Test cost tracking query 2",
        "Test cost tracking query 3"
    ]

    for query in test_queries:
        messages = [{"role": "user", "content": query}]
        result = client.chat_completion(messages)
        print(f"Query: {query[:30]}... Cost: {result['cost']}")

    # Check summary
    summary = client.get_cost_summary()
    print("\n📊 Cost Summary:")
    print(f"Total Requests: {summary['requests_count']}")
    print(f"Total Tokens: {summary['tokens_used']}")
    print(f"Total Cost: ${summary['total_cost']:.4f} (should be $0.00 for free models)")

async def main():
    """Run all tests."""
    print("🚀 ISA_D OpenRouter Free Model Integration Test Suite")
    print("=" * 60)
    print(f"OpenRouter API Key: {'✅ Configured' if os.getenv('OPENROUTER_API_KEY') else '❌ Missing'}")
    print(f"Free Models Enabled: {'✅ Yes' if os.getenv('OPENROUTER_USE_FREE_MODELS') else '❌ No'}")
    print()

    # Run basic model test
    print("1️⃣ Running Basic Model Tests...")
    test_free_models()

    # Run ISA-specific tests
    await test_isa_compliance_scenarios()

    # Test advanced features
    await test_rate_limiting()
    await test_model_fallback()
    await test_cost_tracking()

    print("\n🎉 All tests completed!")
    print("\n💡 Next Steps:")
    print("1. Review test results above")
    print("2. Start the ISA_D backend: python -m src.api_server")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Test the web interface at http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())
