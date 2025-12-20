#!/usr/bin/env python3
"""
SEA-LION + FULL PIPELINE Demo - All 9 Constitutional Floors

This shows the REAL arifOS v44 system with:
- All 9 Constitutional Floors (F1-F9)
- TEARFRAME Physics (v44)
- Semantic Analysis (AGI/ASI)
- Truth checking
- Safety enforcement
- The COMPLETE governance stack!
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from arifos_core.system.pipeline import Pipeline
from arifos_core.system.apex_prime import Verdict, APEX_VERSION


def print_banner():
    print("\n" + "🔥" * 35)
    print("  ⚖️  FULL 9-FLOOR GOVERNANCE DEMO ⚖️")
    print("🔥" * 35)
    print(f"  Version: {APEX_VERSION}")
    print("  ALL Constitutional Floors: ACTIVE")
    print("🔥" * 35 + "\n")


def show_full_report(state):
    """Show complete governance report - all 9 floors."""
    print("\n" + "=" * 70)
    print("⚖️  CONSTITUTIONAL GOVERNANCE - FULL REPORT")
    print("=" * 70)

    # Get verdict
    if hasattr(state, "verdict"):
        if hasattr(state.verdict, "verdict"):
            verdict = state.verdict.verdict
        else:
            verdict = state.verdict
    else:
        verdict = "UNKNOWN"

    verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)

    # Show physics (F1, F3, F7)
    if hasattr(state, "physics_attributes") and state.physics_attributes:
        print("\n🔬 PHYSICS LAYER (F1, F3, F7):")
        attrs = state.physics_attributes
        print(
            f"  F1 Budget:     {attrs.get('budget_burn_pct', 0):.1f}% {'✅' if attrs.get('budget_burn_pct', 0) < 80 else '❌'}"
        )
        print(
            f"  F3 Turn Rate:  {attrs.get('turn_rate', 0):.1f} msg/min {'✅' if attrs.get('turn_rate', 0) < 20 else '❌'}"
        )
        print(
            f"  F7 Streaks:    {attrs.get('sabar_streak', 0)} fails {'✅' if attrs.get('sabar_streak', 0) < 3 else '❌'}"
        )

    # Show semantic analysis (F2, F4, F5, F6, F8, F9)
    if hasattr(state, "metrics") and state.metrics:
        print("\n🧠 SEMANTIC LAYER (F2, F4, F5, F6, F8, F9):")
        m = state.metrics

        # F2 Truth
        truth = m.truth if hasattr(m, "truth") else 0.0
        print(f"  F2 Truth:      {truth:.2f} {'✅' if truth >= 0.99 else '❌ HALLUCINATION!'}")

        # F4 DeltaS (Clarity)
        delta_s = m.delta_s if hasattr(m, "delta_s") else 0.0
        print(f"  F4 Clarity:    {delta_s:.2f} {'✅' if delta_s > 0 else '❌'}")

        # F5 Peace²
        peace = m.peace_squared if hasattr(m, "peace_squared") else 0.0
        print(f"  F5 Peace²:     {peace:.2f} {'✅' if peace >= 1.0 else '❌ UNSAFE!'}")

        # F6 Kappa_r (Empathy)
        kappa = m.kappa_r if hasattr(m, "kappa_r") else 0.0
        print(f"  F6 Empathy:    {kappa:.2f} {'✅' if kappa >= 0.95 else '❌'}")

        # F8 Genius Index
        if hasattr(m, "genius_index"):
            print(f"  F8 Genius:     {m.genius_index:.2f} {'✅' if m.genius_index > 0 else '⚠️'}")

        # F9 Anti-Hantu
        anti_hantu = m.anti_hantu if hasattr(m, "anti_hantu") else True
        print(f"  F9 Anti-Hantu: {'✅ PASS' if anti_hantu else '❌ FAIL'}")

    print("\n" + "─" * 70)

    # Final verdict
    if verdict_str == "SEAL":
        print("✅ FINAL VERDICT: SEAL - Approved by all floors")
    elif verdict_str == "SABAR":
        print("⚠️  FINAL VERDICT: SABAR - Constitutional pause (floor warning)")
    elif verdict_str == "VOID":
        print("🚫 FINAL VERDICT: VOID - Blocked by constitutional floor")
    elif verdict_str == "HOLD_888":
        print("🔒 FINAL VERDICT: HOLD_888 - Session locked (streak threshold)")
    else:
        print(f"⚠️  FINAL VERDICT: {verdict_str}")

    # Show reason if available
    if hasattr(state, "verdict") and hasattr(state.verdict, "reason"):
        print(f"   Reason: {state.verdict.reason}")

    print("=" * 70 + "\n")


def main():
    print_banner()

    # Check API key
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("❌ ERROR: ARIF_LLM_API_KEY not in .env\n")
        return 1

    api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")
    model = os.getenv("ARIF_LLM_MODEL", "aisingapore/Llama-SEA-LION-v3-70B-IT")

    print(f"🔧 Configuration:")
    print(f"  • Model: SEA-LION v3")
    print(f"  • Governance: ALL 9 Floors ACTIVE")
    print(f"  • Version: {APEX_VERSION}\n")

    # Initialize FULL pipeline
    try:
        print("⏳ Initializing full governance pipeline...")
        pipeline = Pipeline(
            model_name=model,
            api_key=api_key,
        )
        print("✅ Pipeline initialized with full constitutional governance\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        print("Note: Full pipeline requires all governance modules.")
        print("Falling back would require semantic engines (AGI/ASI).\n")
        return 1

    print("=" * 70)
    print("  INTERACTIVE MODE - Full Governance")
    print("  Type 'quit' to exit")
    print("=" * 70 + "\n")

    turn_count = 0
    user_id = "demo_user"

    while True:
        try:
            prompt = input("\n🎯 Your prompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ["quit", "exit", "q"]:
                break

            turn_count += 1

            print(f"\n⏳ Turn {turn_count}: Running through FULL governance pipeline...")
            print("   (Physics → Semantic → All 9 Floors → Verdict)\n")

            # Run through FULL pipeline
            state = pipeline.run(
                query=prompt,
                user_id=user_id,
                session_id=f"full_demo_{turn_count}",
            )

            # Show complete governance report
            show_full_report(state)

            # Show response if SEAL
            verdict = state.verdict.verdict if hasattr(state.verdict, "verdict") else state.verdict
            verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)

            if verdict_str == "SEAL":
                print("🤖 SEA-LION Response:")
                print("─" * 70)
                output = state.output if hasattr(state, "output") else "No output"
                print(output[:400] + "..." if len(output) > 400 else output)
                print("─" * 70)
            else:
                print("🚫 Response blocked by constitutional governance")
                print(f"   Floor violation: Check report above")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   This might be a configuration or API issue.\n")

    print(f"\n📊 Session Summary:")
    print(f"  • Total turns: {turn_count}")
    print(f"  • Governance: Full 9-Floor System")
    print(f"  • Version: {APEX_VERSION}\n")

    print("✅ Full constitutional governance demo complete!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
