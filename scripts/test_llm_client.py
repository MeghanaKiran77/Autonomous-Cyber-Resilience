#!/usr/bin/env python3
"""
Quick test script for LLM client integration.

Usage:
    export GROQ_API_KEY=your-key-here
    python scripts/test_llm_client.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.schema import LLMConfig
from llm.factory import create_llm_client


def test_basic_call():
    """Test basic LLM call."""
    print("=" * 60)
    print("Testing LLM Client Integration")
    print("=" * 60)

    # Create client
    config = LLMConfig(provider="groq", model="llama-3.1-70b-versatile")
    print(f"\nProvider: {config.provider}")
    print(f"Model: {config.model}")

    try:
        client = create_llm_client(config)
        print("✓ Client created successfully")
    except ValueError as e:
        print(f"✗ Failed to create client: {e}")
        print("\nMake sure to set your API key:")
        print("  export GROQ_API_KEY=your-key-here")
        return False

    # Test simple call
    print("\n" + "-" * 60)
    print("Test 1: Simple text generation")
    print("-" * 60)

    try:
        response = client.call(
            prompt="Say 'Hello from Groq!' and nothing else.",
            temperature=0.1,
            max_tokens=50,
        )

        print(f"✓ Response received")
        print(f"  Content: {response.content}")
        print(f"  Tokens (in/out): {response.tokens_input}/{response.tokens_output}")
        print(f"  Cost: ${response.cost_usd:.6f}")
        print(f"  Latency: {response.latency_ms:.0f}ms")
    except Exception as e:
        print(f"✗ Call failed: {e}")
        return False

    # Test structured call
    print("\n" + "-" * 60)
    print("Test 2: Structured JSON generation")
    print("-" * 60)

    schema = {
        "vulnerability_type": "string",
        "confidence": "number",
        "description": "string",
    }

    try:
        result = client.call_structured(
            prompt="Analyze this SQL query for vulnerabilities: SELECT * FROM users WHERE id = '" + input_id + "'",
            schema=schema,
            temperature=0.1,
        )

        print(f"✓ Structured response received")
        print(f"  Keys: {list(result.keys())}")
        print(f"  Content: {result}")
    except Exception as e:
        print(f"✗ Structured call failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_basic_call()
    sys.exit(0 if success else 1)
