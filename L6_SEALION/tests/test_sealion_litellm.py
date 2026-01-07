#!/usr/bin/env python3
"""
Test script for SEA-LION via LiteLLM gateway.

This script validates the LiteLLM integration with SEA-LION,
testing basic connectivity and response quality.

Usage:
    # Set your API key
    export ARIF_LLM_API_KEY='your-sealion-api-key'
    
    # Run the test
    python scripts/test_sealion_litellm.py
    
    # Or use .env file (recommended)
    cp .env.example .env
    # Edit .env with your key
    python scripts/test_sealion_litellm.py

Author: arifOS Project
Version: v38.2
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.integration.connectors.litellm_gateway import (
    make_llm_generate,
    get_supported_providers,
    LiteLLMConfig,
)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)
    print()


def print_section(text: str) -> None:
    """Print a section separator."""
    print()
    print("-" * 60)
    print(text)
    print("-" * 60)


def main():
    """Run SEA-LION LiteLLM integration tests."""
    print_header("arifOS v38.2 - SEA-LION LiteLLM Test Suite")
    
    # Show supported providers
    print("Supported Providers:")
    for provider, info in get_supported_providers().items():
        print(f"  • {provider}: {info['description']}")
        if "api_base" in info:
            print(f"    API Base: {info['api_base']}")
    print()
    
    # Check configuration
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("[ERROR] ARIF_LLM_API_KEY not set!")
        print()
        print("Options:")
        print("  1. Create .env file:")
        print("     cp .env.example .env")
        print("     # Edit .env with your SEA-LION API key")
        print()
        print("  2. Export environment variable:")
        print("     export ARIF_LLM_API_KEY='your-key'")
        print()
        print("Get your key at: https://playground.sea-lion.ai")
        sys.exit(1)
    
    provider = os.getenv("ARIF_LLM_PROVIDER", "openai")
    api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
    model = os.getenv("ARIF_LLM_MODEL", "aisingapore/Llama-SEA-LION-v3-70B-IT")
    
    print(f"[CONFIG] Provider: {provider}")
    print(f"[CONFIG] API Base: {api_base}")
    print(f"[CONFIG] Model: {model}")
    print(f"[CONFIG] API Key: {api_key[:12]}...{api_key[-4:]}")
    print()
    
    # Create generate function
    try:
        generate = make_llm_generate()
        print("[✓] LiteLLM gateway initialized successfully")
    except Exception as e:
        print(f"[✗] Failed to initialize gateway: {e}")
        sys.exit(1)
    
    # Test queries
    test_queries = [
        ("English - AI Governance", "What is AI governance in one sentence?"),
        ("Malay - AI Definition", "Apa itu artificial intelligence?"),
        ("Technical - Constitutional AI", "Explain constitutional AI in 2 sentences."),
    ]
    
    results = []
    
    for i, (label, query) in enumerate(test_queries, 1):
        print_section(f"TEST {i}/{len(test_queries)}: {label}")
        print(f"Query: {query}")
        print()
        
        try:
            response = generate(query)
            print(f"Response: {response}")
            results.append((label, "PASS", len(response)))
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append((label, "FAIL", 0))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    for label, status, length in results:
        symbol = "✓" if status == "PASS" else "✗"
        detail = f"({length} chars)" if status == "PASS" else ""
        print(f"  [{symbol}] {label}: {status} {detail}")
    
    print()
    
    if passed == total:
        print("[SUCCESS] All tests passed! SEA-LION integration working correctly.")
        print()
        print("Next steps:")
        print("  1. Start API server: python -m arifos_core.api.app")
        print("  2. Test endpoint: curl -X POST http://localhost:8000/pipeline/run \\")
        print("                          -H 'Content-Type: application/json' \\")
        print("                          -d '{\"query\": \"Test query\"}'")
        return 0
    else:
        print(f"[PARTIAL] {total - passed} test(s) failed.")
        print("Check your API key and network connection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
