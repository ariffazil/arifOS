#!/usr/bin/env python3
"""
Raw SEA-LION API Test Script
Quick test script for SEA-LION API without governance overhead.

Usage:
    python test_sealion_raw.py "Your prompt here"
    python test_sealion_raw.py  # Interactive mode
"""

import os
import sys
import json

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)

# SEA-LION API Configuration
SEALION_API_URL = "https://api.sea-lion.ai/v1/chat/completions"
SEALION_API_KEY = os.getenv("SEALION_API_KEY")

def call_sealion(prompt: str, model: str = "aisingapore/Qwen-SEA-LION-v4-32B-IT") -> dict:
    """
    Call SEA-LION API with a prompt.

    Args:
        prompt: User prompt
        model: SEA-LION model to use

    Returns:
        dict with 'response' and 'raw_data'
    """
    if not SEALION_API_KEY:
        return {
            "error": "SEALION_API_KEY not set",
            "help": "Set environment variable: $env:SEALION_API_KEY='your-key'"
        }

    headers = {
        "Authorization": f"Bearer {SEALION_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(SEALION_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Extract response text
        if "choices" in data and len(data["choices"]) > 0:
            response_text = data["choices"][0]["message"]["content"]
            return {
                "response": response_text,
                "model": data.get("model", model),
                "usage": data.get("usage", {}),
                "raw_data": data
            }
        else:
            return {
                "error": "Unexpected response format",
                "raw_data": data
            }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {e}",
            "details": str(e)
        }

def interactive_mode():
    """Run interactive prompt loop."""
    print("=" * 70)
    print("SEA-LION Raw API Test - Interactive Mode")
    print("=" * 70)
    print()
    print("Commands:")
    print("  quit, exit, q - Exit")
    print("  clear, cls    - Clear screen")
    print()

    if not SEALION_API_KEY:
        print("[ERROR] SEALION_API_KEY not set!")
        print("Set it with: $env:SEALION_API_KEY='your-key'")
        return

    print(f"[OK] API Key loaded: {SEALION_API_KEY[:8]}...")
    print()

    while True:
        try:
            prompt = input("Prompt> ").strip()

            if prompt.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if prompt.lower() in ["clear", "cls"]:
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            if not prompt:
                continue

            print()
            print("[Calling SEA-LION API...]")

            result = call_sealion(prompt)

            if "error" in result:
                print(f"\n[ERROR] {result['error']}")
                if "details" in result:
                    print(f"Details: {result['details']}")
            else:
                print("\n" + "=" * 70)
                print("RESPONSE:")
                print("=" * 70)
                print(result["response"])
                print("=" * 70)
                print()
                print(f"Model: {result.get('model', 'unknown')}")
                if "usage" in result:
                    usage = result["usage"]
                    print(f"Tokens: {usage.get('total_tokens', 'N/A')} (prompt: {usage.get('prompt_tokens', 'N/A')}, completion: {usage.get('completion_tokens', 'N/A')})")

            print()

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit.")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")

def single_prompt_mode(prompt: str):
    """Run single prompt and exit."""
    print("=" * 70)
    print("SEA-LION Raw API Test - Single Prompt")
    print("=" * 70)
    print()

    if not SEALION_API_KEY:
        print("[ERROR] SEALION_API_KEY not set!")
        print("Set it with: $env:SEALION_API_KEY='your-key'")
        sys.exit(1)

    print(f"Prompt: {prompt}")
    print()
    print("[Calling SEA-LION API...]")
    print()

    result = call_sealion(prompt)

    if "error" in result:
        print(f"[ERROR] {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
        sys.exit(1)
    else:
        print("=" * 70)
        print("RESPONSE:")
        print("=" * 70)
        print(result["response"])
        print("=" * 70)
        print()
        print(f"Model: {result.get('model', 'unknown')}")
        if "usage" in result:
            usage = result["usage"]
            print(f"Tokens: {usage.get('total_tokens', 'N/A')} (prompt: {usage.get('prompt_tokens', 'N/A')}, completion: {usage.get('completion_tokens', 'N/A')})")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single prompt mode
        prompt = " ".join(sys.argv[1:])
        single_prompt_mode(prompt)
    else:
        # Interactive mode
        interactive_mode()
