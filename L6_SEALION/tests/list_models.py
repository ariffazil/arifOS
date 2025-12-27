#!/usr/bin/env python3
"""
Quick script to list available models for your API key
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
    print("❌ No API key found!")
    sys.exit(1)

# Get API base
api_base = os.getenv("ARIF_LLM_API_BASE")

print(f"\n🔍 Checking available models...")
print(f"API Base: {api_base if api_base else 'default'}")
print()

# Try to list models
try:
    # For OpenAI-compatible APIs
    import requests

    if api_base:
        url = f"{api_base.rstrip('/')}/models"
    else:
        url = "https://api.openai.com/v1/models"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        models = data.get("data", [])

        print(f"✅ Found {len(models)} available models:\n")
        for i, model in enumerate(models, 1):
            model_id = model.get("id", "unknown")
            print(f"{i}. {model_id}")

        if models:
            print(f"\n💡 Use the first model with:")
            print(f'python L6_SEALION/tests/raw_sealion_simple.py --model "{models[0]["id"]}"')
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry setting ARIF_LLM_API_BASE environment variable to your API endpoint")
