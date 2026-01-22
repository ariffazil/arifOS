#!/usr/bin/env python3
"""
Test SEA-LION AI with arifOS v44 TEARFRAME Physics Enforcement

This script runs SEA-LION through the full governed pipeline including:
- TEARFRAME Session Physics (v44)
- Constitutional Floors (F1-F9)
- Fail-closed enforcement

Usage:
    1. Make sure your .env file has:
       ARIF_LLM_API_KEY=your-sealion-api-key
       ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1
       ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT

    2. Run: python test_sealion_v44.py
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("[WARNING] python-dotenv not installed. Using environment variables only.")

from arifos_core.system.pipeline import Pipeline
from arifos_core.system.apex_prime import Verdict, APEX_VERSION, APEX_EPOCH


def print_header(text: str):
    print()
    print("=" * 70)
    print(text)
    print("=" * 70)
    print()


def print_physics_report(state):
    """Show the TEARFRAME physics data."""
    if hasattr(state, "physics_attributes") and state.physics_attributes:
        attrs = state.physics_attributes
        print("\n📊 TEARFRAME Physics Report:")
        print(f"  • Turn Rate: {attrs.get('turn_rate', 0):.2f} messages/min")
        print(f"  • Token Burn: {attrs.get('budget_burn_pct', 0):.1f}%")
        print(f"  • Cadence: {attrs.get('cadence', 0):.2f}s between turns")
        print(f"  • SABAR Streak: {attrs.get('sabar_streak', 0)}")
        print(f"  • VOID Streak: {attrs.get('void_streak', 0)}")


def main():
    print_header(f"arifOS v44 TEARFRAME - SEA-LION AI Test")

    # Verify v44
    print(f"✓ System Version: {APEX_VERSION}")
    print(f"✓ Epoch: {APEX_EPOCH}")
    print()

    # Check API key
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("❌ ERROR: ARIF_LLM_API_KEY not found in .env")
        print()
        print("Add to your .env file:")
        print("  ARIF_LLM_API_KEY=your-sealion-api-key")
        print("  ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1")
        print("  ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT")
        print()
        print("Get your key at: https://playground.sea-lion.ai")
        return 1

    api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
    model = os.getenv("ARIF_LLM_MODEL", "aisingapore/Llama-SEA-LION-v3-70B-IT")

    print(f"🔧 Configuration:")
    print(f"  • API Base: {api_base}")
    print(f"  • Model: {model}")
    print(f"  • API Key: {api_key[:12]}...{api_key[-4:]}")
    print()

    # Initialize pipeline
    try:
        pipeline = Pipeline(
            llm_backend="litellm",
            model_name=model,
            api_base=api_base,
            api_key=api_key,
        )
        print("✓ Pipeline initialized with TEARFRAME v44 physics")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return 1

    # Test queries
    test_queries = [
        ("Safe Query", "What is artificial intelligence in one sentence?"),
        ("Malay Query", "Apa itu AI dalam satu ayat?"),
        ("Edge Case", "Tell me about constitutional AI governance."),
    ]

    results = []
    user_id = "sealion_test_user"

    for i, (label, query) in enumerate(test_queries, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}/{len(test_queries)}: {label}")
        print(f"{'─' * 70}")
        print(f"Query: {query}")
        print()

        try:
            # Run through full governed pipeline
            state = pipeline.run(
                query=query,
                user_id=user_id,
                session_id=f"sealion_test_{i}",
            )

            # Show verdict
            verdict = state.verdict.verdict if hasattr(state.verdict, "verdict") else state.verdict
            verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)

            print(f"🔒 Verdict: {verdict_str}")

            # Show physics
            print_physics_report(state)

            # Show response
            if verdict_str == "SEAL":
                print(f"\n✓ Response: {state.output[:200]}...")
                results.append((label, "PASS", verdict_str))
            else:
                print(f"\n⚠️  Response blocked by physics floor")
                print(
                    f"   Reason: {state.verdict.reason if hasattr(state.verdict, 'reason') else 'N/A'}"
                )
                results.append((label, "BLOCKED", verdict_str))

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((label, "ERROR", str(e)))

    # Summary
    print_header("Test Summary")

    passed = sum(1 for _, status, _ in results if status == "PASS")
    blocked = sum(1 for _, status, _ in results if status == "BLOCKED")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    total = len(results)

    print(f"Results:")
    print(f"  ✓ PASS (SEAL): {passed}/{total}")
    print(f"  ⚠️  BLOCKED: {blocked}/{total}")
    print(f"  ❌ ERROR: {errors}/{total}")
    print()

    for label, status, detail in results:
        symbol = "✓" if status == "PASS" else "⚠️" if status == "BLOCKED" else "❌"
        print(f"  [{symbol}] {label}: {status} ({detail})")

    print()

    if errors == 0:
        print("🎉 SUCCESS! SEA-LION + arifOS v44 TEARFRAME is working!")
        print()
        print("What just happened:")
        print("  1. SEA-LION AI generated responses")
        print("  2. TEARFRAME physics measured session behavior")
        print("  3. Constitutional floors (F1-F9) evaluated output")
        print("  4. Physics enforcement applied (fail-closed)")
        print()
        print("Your SEA-LION AI is now governed by physics! 🔒")
        return 0
    else:
        print(f"⚠️  {errors} error(s) occurred. Check your API key and connection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
