#!/usr/bin/env python3
"""
SEA-LION RAW - Minimal Interactive REPL

Direct HTTP calls to SEA-LION API. No dependencies except requests.

Usage:
    pip install requests
    python scripts/sealion_raw_only.py

Environment:
    SEALION_API_KEY=your-key-here
"""

import os
import sys
import json

try:
    import requests
except ImportError:
    print("ERROR: requests not installed")
    print("Install: pip install requests")
    sys.exit(1)


def call_sealion(prompt, api_key, model="aisingapore/Gemma-SEA-LION-v4-27B-IT"):
    """Direct HTTP call to SEA-LION API."""
    url = "https://api.sea-lion.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512,
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"ERROR: {e}"
    except (KeyError, IndexError) as e:
        return f"ERROR: Invalid response format - {e}"


def main():
    """Run interactive REPL."""
    # Get API key
    api_key = os.getenv("SEALION_API_KEY") or os.getenv("ARIF_LLM_API_KEY")

    if not api_key:
        print("ERROR: API key not found!")
        print("\nSet environment variable:")
        print("  Windows: $env:SEALION_API_KEY = 'sk-...'")
        print("  Linux: export SEALION_API_KEY='sk-...'")
        sys.exit(1)

    # Model selection
    models = [
        "aisingapore/Gemma-SEA-LION-v4-27B-IT",  # Default
        "aisingapore/Qwen-SEA-LION-v4-32B-IT",   # Flagship
        "aisingapore/Llama-SEA-LION-v3-70B-IT",  # Large
    ]

    current_model = models[0]

    # Banner
    print("\n" + "=" * 60)
    print("SEA-LION RAW - Direct API REPL".center(60))
    print("=" * 60)
    print(f"\nModel: {current_model}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print("\nCommands: /model /quit /help")
    print("=" * 60 + "\n")

    # REPL loop
    query_count = 0

    while True:
        try:
            # Get input
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            # Commands
            if user_input == "/quit" or user_input == "/exit":
                print("\nBye!\n")
                break

            elif user_input == "/help":
                print("\nCommands:")
                print("  /model  - List/switch models")
                print("  /quit   - Exit")
                print("  /help   - This help\n")
                continue

            elif user_input == "/model":
                print("\nAvailable models:")
                for i, m in enumerate(models, 1):
                    marker = " <-- CURRENT" if m == current_model else ""
                    print(f"  {i}. {m}{marker}")

                choice = input("\nSelect (1-3) or Enter to keep current: ").strip()
                if choice in ["1", "2", "3"]:
                    current_model = models[int(choice) - 1]
                    print(f"Switched to: {current_model}\n")
                continue

            # Process query
            query_count += 1
            print(f"\n[Query #{query_count}]")
            print("-" * 60)

            # Call API
            response = call_sealion(user_input, api_key, current_model)

            # Print response
            print(response)
            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\n(Ctrl+C to quit, or type /quit)\n")
        except EOFError:
            print("\n\nBye!\n")
            break


if __name__ == "__main__":
    main()
