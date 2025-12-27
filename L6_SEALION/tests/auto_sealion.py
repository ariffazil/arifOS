#!/usr/bin/env python3
"""
AUTO SEA-LION - Automatically finds and uses the right model

Just run: python L6_SEALION/tests/auto_sealion.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import litellm

# Get API key
api_key = (
    os.getenv("ARIF_LLM_API_KEY")
    or os.getenv("SEALION_API_KEY")
    or os.getenv("LLM_API_KEY")
    or os.getenv("OPENAI_API_KEY")
)

if not api_key:
    print("\n❌ No API key found!")
    print("Set: $env:ARIF_LLM_API_KEY = 'your-key'\n")
    sys.exit(1)

api_base = os.getenv("ARIF_LLM_API_BASE")

# Actual SEA-LION model names (2025) - from https://sea-lion.ai/models/
MODELS_TO_TRY = [
    # V4 Generation (Latest - Oct 2025)
    "aisingapore/Gemma-SEA-LION-v4-27B-IT",
    "aisingapore/Qwen-SEA-LION-v4-32B-IT",
    # V3.5 Generation
    "aisingapore/Llama-SEA-LION-v3.5-8B-R",
    # V3 Generation
    "aisingapore/Gemma-SEA-LION-v3-9B-IT",
    "aisingapore/Llama-SEA-LION-v3-70B-IT",
    # V1/V2 Legacy
    "aisingapore/sea-lion-7b-instruct",
    "aisingapore/SEA-LION-v1-7B",
]

# SEA-LION API endpoint
if not api_base:
    api_base = "https://api.sea-lion.ai/v1"
    print(f"ℹ️  No ARIF_LLM_API_BASE set, using default: {api_base}")

print("\n🦁 AUTO SEA-LION - Finding your model...\n")
print(f"API Base: {api_base if api_base else 'default OpenAI'}")
print()

working_model = None

for model_name in MODELS_TO_TRY:
    print(f"Trying: {model_name}...", end=" ")
    try:
        # Try a simple completion
        # SEA-LION uses OpenAI-compatible API
        response = litellm.completion(
            model=f"openai/{model_name}",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10,
            api_key=api_key,
            api_base=api_base,
        )

        # If we got here, it worked!
        working_model = model_name
        print("✅ WORKS!")
        break

    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
            print("❌ Not available")
        else:
            print(f"❌ Error: {error_msg[:50]}...")

if working_model:
    print(f"\n🎉 SUCCESS! Your model is: {working_model}")
    print(f"\nNow testing with a real prompt...\n")

    # Test with actual prompt
    print("─" * 80)
    print("📝 Prompt: What is 2+2?")
    print()

    try:
        response = litellm.completion(
            model=f"openai/{working_model}",
            messages=[{"role": "user", "content": "What is 2+2?"}],
            max_tokens=100,
            api_key=api_key,
            api_base=api_base,
        )

        answer = response.choices[0].message.content
        print(f"📤 Response: {answer}")
        print("─" * 80)

        print(f"\n✅ PERFECT! Use this model going forward:")
        print(f'   python L6_SEALION/tests/raw_sealion_simple.py --model "{working_model}"')
        print()

    except Exception as e:
        print(f"❌ Error during test: {e}")

else:
    print("\n❌ None of the common models worked!")
    print("\nTry checking your API provider's documentation for the correct model name.")
    print("Or run: python L6_SEALION/tests/list_models.py")
    print()
