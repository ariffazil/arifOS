#!/usr/bin/env python3
"""Quick diagnostic test for SEA-LION runtime fixes (v45Ω Patch B.2.1)"""

import os
import sys

# Test 1: Verify API endpoint format
print("=" * 60)
print("Test 1: API Endpoint Format")
print("=" * 60)

sys.path.insert(0, "L6_SEALION/cli")
from sealion_raw_client import DEFAULT_API_BASE, RawSEALionClient

print(f"DEFAULT_API_BASE: {DEFAULT_API_BASE}")
print(f"Expected: https://api.sea-lion.ai/v1")
print(f"Result: {'[OK]' if DEFAULT_API_BASE == 'https://api.sea-lion.ai/v1' else '[FAIL]'}")

# Test 2: Verify Pipeline.run() signature compatibility
print("\n" + "=" * 60)
print("Test 2: Pipeline.run() Signature")
print("=" * 60)

from arifos_core.system.pipeline import Pipeline
import inspect

sig = inspect.signature(Pipeline.run)
params = list(sig.parameters.keys())
print(f"Pipeline.run() parameters: {params}")
print(f"Has 'lane' param: {'lane' in params}")
print(f"Result: {'[FAIL]' if 'lane' in params else '[OK]'}")

# Test 3: Smoke test RAW client (if API key available)
print("\n" + "=" * 60)
print("Test 3: RAW Client Smoke Test")
print("=" * 60)

api_key = os.getenv("SEALION_API_KEY") or os.getenv("ARIF_LLM_API_KEY")
if api_key:
    try:
        client = RawSEALionClient(
            api_key=api_key,
            model="aisingapore/Qwen-SEA-LION-v4-32B-IT",
            enable_memory=False,
            enable_tools=False,
        )
        result = client.generate("Test query", max_tokens=10)

        if "[API ERROR]" in result["response"]:
            print(f"[FAIL] API Error: {result['response']}")
        elif "[CONNECTION ERROR]" in result["response"]:
            print(f"[FAIL] Connection Error: {result['response']}")
        else:
            print(f"[OK] API call successful")
            print(f"   Response preview: {result['response'][:100]}...")
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
else:
    print("[SKIP] No API key found (set SEALION_API_KEY)")

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)
