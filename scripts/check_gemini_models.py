"""
check_gemini_models.py — List available Gemini models for your API key

Usage:
    $env:GEMINI_API_KEY="your_key"
    python scripts/check_gemini_models.py
"""

import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed.")
    print("   Run: pip install google-generativeai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not set.")
    print("   PowerShell: $env:GEMINI_API_KEY='your_key'")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Listing available models for your API key...")
print("=" * 50)

try:
    found = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            found = True
            # Extract just the model name (remove 'models/' prefix)
            name = m.name.replace('models/', '')
            print(f"  {name}")

    if not found:
        print("  No models with generateContent support found.")
    else:
        print("=" * 50)
        print("\nUse one of these names in the test script.")
        print("Example: genai.GenerativeModel('gemini-2.0-flash')")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
