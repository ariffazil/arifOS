#!/usr/bin/env python3
"""
🦁 Simple RAW SEA-LION Test Script (NO Governance)

Just test the raw LLM with your own prompts.
No arifOS, no governance, no metrics - pure model calls.

Usage:
    # Interactive mode
    python L6_SEALION/tests/raw_sealion_simple.py

    # Single prompt
    python L6_SEALION/tests/raw_sealion_simple.py --prompt "Your question here"

    # Custom model
    python L6_SEALION/tests/raw_sealion_simple.py --model "standard" --prompt "Test"
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.integration.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig


def get_api_key():
    """Get API key from environment"""
    api_key = (
        os.getenv("ARIF_LLM_API_KEY")
        or os.getenv("SEALION_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )

    if not api_key:
        print("\n❌ API Key not found!")
        print("\nSet one of these environment variables:")
        print("  - ARIF_LLM_API_KEY")
        print("  - SEALION_API_KEY")
        print("  - LLM_API_KEY")
        print("  - OPENAI_API_KEY")
        print("\nExample (PowerShell):")
        print('  $env:ARIF_LLM_API_KEY = "your-api-key-here"')
        print()
        sys.exit(1)

    return api_key


def call_raw_llm(prompt, model="aisingapore/Gemma-SEA-LION-v4-27B-IT", max_tokens=512, temperature=0.2):
    """
    Call SEA-LION LLM directly (no governance)

    Args:
        prompt: User prompt
        model: Model name
        max_tokens: Max tokens to generate
        temperature: Temperature (0.0-1.0)

    Returns:
        tuple: (response_text, elapsed_time, error)
    """
    print(f"\n🦁 Calling {model}...")
    print(f"📝 Prompt: {prompt[:60]}..." if len(prompt) > 60 else f"📝 Prompt: {prompt}")
    print()

    # Get API key
    api_key = get_api_key()

    # Get API base (default to SEA-LION endpoint)
    api_base = os.getenv("ARIF_LLM_API_BASE")
    if not api_base:
        api_base = "https://api.sea-lion.ai/v1"

    # Create config
    config = LiteLLMConfig(
        provider="openai",
        api_base=api_base,
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Create generator
    generate = make_llm_generate(config)

    # Call LLM
    start_time = time.time()
    error = None
    response = None

    try:
        response = generate(prompt)
        elapsed = time.time() - start_time

        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"📊 Response length: {len(response)} chars")
        print()

    except Exception as e:
        elapsed = time.time() - start_time
        error = str(e)
        print(f"❌ Error: {error}")
        print(f"⏱️ Failed after {elapsed:.2f}s")
        print()

    return response, elapsed, error


def interactive_mode(model="aisingapore/Gemma-SEA-LION-v4-27B-IT", max_tokens=512, temperature=0.2):
    """Interactive prompt mode"""
    print("\n" + "🦁" * 40)
    print("  RAW SEA-LION Interactive Mode")
    print("🦁" * 40)
    print(f"\nModel: {model}")
    print(f"Max tokens: {max_tokens}, Temperature: {temperature}")
    print("\nType 'quit' or 'exit' to stop")
    print("Type 'help' for options")
    print("─" * 80 + "\n")

    while True:
        try:
            # Get prompt from user
            prompt = input("🦁 Prompt> ").strip()

            if not prompt:
                continue

            # Handle commands
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break

            if prompt.lower() == 'help':
                print("\nCommands:")
                print("  quit, exit, q  - Exit interactive mode")
                print("  help           - Show this help")
                print("  clear          - Clear screen")
                print("\nJust type your prompt to get a response.\n")
                continue

            if prompt.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            # Call LLM
            response, elapsed, error = call_raw_llm(
                prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Show response
            if response:
                print("─" * 80)
                print("📤 RESPONSE:\n")
                print(response)
                print("\n" + "─" * 80 + "\n")
            else:
                print(f"❌ No response (error: {error})\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break


def single_prompt_mode(prompt, model="aisingapore/Gemma-SEA-LION-v4-27B-IT", max_tokens=512, temperature=0.2):
    """Single prompt mode"""
    print("\n" + "🦁" * 40)
    print("  RAW SEA-LION Single Prompt Mode")
    print("🦁" * 40)
    print(f"\nModel: {model}")
    print(f"Max tokens: {max_tokens}, Temperature: {temperature}")
    print()

    # Call LLM
    response, elapsed, error = call_raw_llm(
        prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    )

    # Show response
    if response:
        print("─" * 80)
        print("📤 RESPONSE:\n")
        print(response)
        print("\n" + "─" * 80)
        print(f"\n⏱️ Total time: {elapsed:.2f}s\n")
    else:
        print(f"❌ Failed: {error}\n")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Simple RAW SEA-LION test (no governance)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python raw_sealion_simple.py

  # Single prompt
  python raw_sealion_simple.py --prompt "Explain quantum mechanics"

  # Custom model
  python raw_sealion_simple.py --model "standard" --prompt "Test"

  # Adjust generation parameters
  python raw_sealion_simple.py --prompt "Test" --max_tokens 256 --temperature 0.7
        """
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt to send (if not provided, enters interactive mode)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="aisingapore/Gemma-SEA-LION-v4-27B-IT",
        help="Model name (default: aisingapore/Gemma-SEA-LION-v4-27B-IT)"
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=512,
        help="Max tokens to generate (default: 512)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Generation temperature 0.0-1.0 (default: 0.2)"
    )

    args = parser.parse_args()

    try:
        if args.prompt:
            # Single prompt mode
            single_prompt_mode(
                prompt=args.prompt,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )
        else:
            # Interactive mode
            interactive_mode(
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
