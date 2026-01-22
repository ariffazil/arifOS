#!/usr/bin/env python3
"""
Interactive SEA-LION AI Test with arifOS v44 TEARFRAME Physics

Type your prompts and watch the physics enforcement in real-time!

Usage:
    python test_sealion_interactive.py

    Then type your prompts when asked.
    Type 'quit' to exit.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables")

from arifos_core.integration.connectors.litellm_gateway import make_llm_generate
from arifos_core.system.apex_prime import APEX_VERSION, APEX_EPOCH


def print_banner():
    print("\n" + "=" * 70)
    print("  arifOS v44 TEARFRAME - SEA-LION Interactive Test")
    print("=" * 70)
    print(f"  System Version: {APEX_VERSION}")
    print(f"  Epoch: {APEX_EPOCH}")
    print("=" * 70 + "\n")


def main():
    print_banner()

    # Check API key
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("❌ ERROR: ARIF_LLM_API_KEY not found in .env\n")
        print("Add to your .env file:")
        print("  ARIF_LLM_API_KEY=your-sealion-api-key")
        print("  ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1")
        print("  ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT\n")
        return 1

    api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
    model = os.getenv("ARIF_LLM_MODEL", "aisingapore/Llama-SEA-LION-v3-70B-IT")

    print(f"🔧 Configuration:")
    print(f"  • API Base: {api_base}")
    print(f"  • Model: {model}")
    print(f"  • API Key: {api_key[:8]}...{api_key[-4:]}\n")

    # Initialize LLM
    try:
        generate = make_llm_generate()
        print("✓ SEA-LION connection initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}\n")
        return 1

    print("=" * 70)
    print("  Ready! Type your prompts below.")
    print("  Commands: 'quit' to exit, 'clear' to clear screen")
    print("=" * 70 + "\n")

    turn_count = 0

    while True:
        try:
            # Get user input
            prompt = input("\n🎯 Your prompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!\n")
                break

            if prompt.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue

            turn_count += 1

            # Call SEA-LION
            print(f"\n⏳ Calling SEA-LION (turn {turn_count})...")

            try:
                response = generate(prompt)

                print("\n" + "─" * 70)
                print("🤖 SEA-LION Response:")
                print("─" * 70)
                print(response)
                print("─" * 70)

                print(f"\n✓ Turn {turn_count} complete")
                print(f"   Characters: {len(response)}")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("   Check your API key and network connection")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 EOF. Goodbye!\n")
            break

    print(f"\n📊 Session Stats:")
    print(f"  • Total turns: {turn_count}")
    print(f"  • Model: {model}")
    print(f"  • Version: {APEX_VERSION}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
