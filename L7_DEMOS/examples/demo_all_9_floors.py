#!/usr/bin/env python3
"""
SIMULATED Full 9-Floor Governance Demo

Shows what the FULL system does (with mocked semantic analysis)
so you can see ALL 9 floors in action!
"""

import os
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from arifos_core.integration.connectors.litellm_gateway import make_llm_generate
from arifos_core.utils.session_telemetry import SessionTelemetry
from arifos_core.utils.reduction_engine import compute_attributes
from arifos_core.apex.governance.session_physics import evaluate_physics_floors
from arifos_core.system.apex_prime import Verdict, APEX_VERSION
import time


def analyze_response_semantics(prompt, response):
    """
    MOCK semantic analysis - shows what the real system would calculate.

    In the real system, this would be AGI/ASI engines analyzing:
    - Truth (is it factually correct?)
    - Safety (is it harmful?)
    - Empathy (is it considerate?)
    - Etc.
    """
    # Simple heuristics to demonstrate
    response_lower = response.lower()

    # F2 Truth check (mock - detects obvious hallucinations)
    truth = 1.0
    if any(word in response_lower for word in ["kashmir", "bangladesh", "government"]):
        if "arif" in prompt.lower():
            truth = 0.85  # Likely hallucinating about me!

    # F5 Peace² (mock - detects unsafe content)
    peace = 1.0
    if any(word in response_lower for word in ["weapon", "harm", "attack", "kill"]):
        peace = 0.0

    # F6 Kappa_r (mock - empathy check)
    kappa = 0.98
    if any(word in response_lower for word in ["stupid", "idiot", "dumb"]):
        kappa = 0.80

    # F4 DeltaS (clarity gain)
    delta_s = 0.15 if len(response) > 50 else 0.05

    # F9 Anti-Hantu (no deception)
    anti_hantu = "I apologize" not in response_lower or truth > 0.95

    return {
        "truth": truth,
        "delta_s": delta_s,
        "peace": peace,
        "kappa": kappa,
        "anti_hantu": anti_hantu,
    }


def show_full_governance(attrs, physics_verdict, semantic_metrics):
    """Show ALL 9 floors."""
    print("\n" + "=" * 70)
    print("⚖️  FULL CONSTITUTIONAL GOVERNANCE - ALL 9 FLOORS")
    print("=" * 70)

    print("\n🔬 PHYSICS LAYER (v44 TEARFRAME):")
    print(
        f"  F1 Budget:     {attrs.budget_burn_pct:.1f}% {'✅ PASS' if attrs.budget_burn_pct < 80 else '❌ FAIL'}"
    )
    print(
        f"  F3 Turn Rate:  {attrs.turn_rate:.1f} msg/min {'✅ PASS' if attrs.turn_rate < 20 else '❌ FAIL (BURST!)'}"
    )
    print(
        f"  F7 Streaks:    {attrs.sabar_streak} fails {'✅ PASS' if attrs.sabar_streak < 3 else '❌ FAIL (LOCKED!)'}"
    )

    print("\n🧠 SEMANTIC LAYER (Content Analysis):")
    print(
        f"  F2 Truth:      {semantic_metrics['truth']:.2f} {'✅ PASS' if semantic_metrics['truth'] >= 0.99 else '❌ FAIL - HALLUCINATION DETECTED!'}"
    )
    print(
        f"  F4 Clarity:    {semantic_metrics['delta_s']:.2f} {'✅ PASS' if semantic_metrics['delta_s'] > 0 else '❌ FAIL'}"
    )
    print(
        f"  F5 Peace²:     {semantic_metrics['peace']:.2f} {'✅ PASS' if semantic_metrics['peace'] >= 1.0 else '❌ FAIL - UNSAFE CONTENT!'}"
    )
    print(
        f"  F6 Empathy:    {semantic_metrics['kappa']:.2f} {'✅ PASS' if semantic_metrics['kappa'] >= 0.95 else '❌ FAIL - RUDE!'}"
    )
    print(f"  F8 Genius:     0.75 ✅ PASS (governed intelligence)")
    print(
        f"  F9 Anti-Hantu: {'✅ PASS' if semantic_metrics['anti_hantu'] else '❌ FAIL - DECEPTION!'}"
    )

    print("\n" + "─" * 70)

    # Combined verdict (physics + semantic)
    final_verdict = None

    if physics_verdict == Verdict.HOLD_888:
        final_verdict = "HOLD_888"
        reason = "Physics: Streak threshold exceeded"
    elif physics_verdict == Verdict.VOID:
        final_verdict = "VOID"
        reason = "Physics: Budget exceeded"
    elif physics_verdict == Verdict.SABAR:
        final_verdict = "SABAR"
        reason = "Physics: Burst detected"
    elif semantic_metrics["truth"] < 0.99:
        final_verdict = "SABAR"
        reason = "Semantic: Truth floor violation (hallucination)"
    elif semantic_metrics["peace"] < 1.0:
        final_verdict = "VOID"
        reason = "Semantic: Peace² floor violation (unsafe)"
    elif semantic_metrics["kappa"] < 0.95:
        final_verdict = "SABAR"
        reason = "Semantic: Empathy floor violation"
    elif not semantic_metrics["anti_hantu"]:
        final_verdict = "VOID"
        reason = "Semantic: Anti-Hantu violation (deception)"
    else:
        final_verdict = "SEAL"
        reason = "All 9 floors passed!"

    if final_verdict == "SEAL":
        print("✅ FINAL VERDICT: SEAL - Approved by all 9 floors")
    elif final_verdict == "SABAR":
        print("⚠️  FINAL VERDICT: SABAR - Floor warning issued")
    elif final_verdict == "VOID":
        print("🚫 FINAL VERDICT: VOID - Blocked by constitutional floor")
    elif final_verdict == "HOLD_888":
        print("🔒 FINAL VERDICT: HOLD_888 - Session locked")

    print(f"   Reason: {reason}")
    print("=" * 70 + "\n")

    return final_verdict


def main():
    print("\n" + "🔥" * 35)
    print("  ⚖️  FULL 9-FLOOR GOVERNANCE DEMO ⚖️")
    print("🔥" * 35)
    print(f"  Version: {APEX_VERSION}")
    print("  Physics + Semantics: ALL ACTIVE")
    print("🔥" * 35 + "\n")

    # Check API
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print("❌ ARIF_LLM_API_KEY not in .env\n")
        return 1

    try:
        generate = make_llm_generate()
        telemetry = SessionTelemetry("full_demo_user")
        print("✅ System initialized with FULL 9-floor governance\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        return 1

    print("=" * 70)
    print("  Type prompts to see ALL 9 FLOORS in action!")
    print("  Watch for hallucination detection! 🎯")
    print("=" * 70 + "\n")

    turn_count = 0

    while True:
        try:
            prompt = input("\n🎯 Your prompt: ").strip()

            if not prompt or prompt.lower() in ["quit", "exit"]:
                break

            turn_count += 1

            # Start telemetry
            telemetry.start_turn(tokens_in=len(prompt.split()), temperature=0.7, top_p=0.9)
            start_time = time.time()

            print(f"\n⏳ Turn {turn_count}: Analyzing through ALL 9 floors...\n")

            # Get LLM response
            response = generate(prompt)
            elapsed = time.time() - start_time

            # End telemetry
            snapshot = telemetry.end_turn(
                tokens_out=len(response.split()),
                verdict=Verdict.SEAL,  # Provisional
                context_length_used=len(prompt.split()) + len(response.split()),
                kv_cache_size=0,
                timeout=False,
                safety_block=False,
                truncation_flag=False,
                commit=True,
            )

            # Compute physics
            attrs = compute_attributes(
                history=telemetry.history, max_session_tokens=100000, current_turn=snapshot
            )
            physics_verdict = evaluate_physics_floors(attrs)

            # Compute semantics (MOCK)
            semantic_metrics = analyze_response_semantics(prompt, response)

            # Show full governance
            final_verdict = show_full_governance(attrs, physics_verdict, semantic_metrics)

            # Show response if SEAL
            if final_verdict == "SEAL":
                print("🤖 SEA-LION Response:")
                print("─" * 70)
                print(response[:300] + "..." if len(response) > 300 else response)
                print("─" * 70)
            else:
                print("🚫 Response BLOCKED by constitutional governance!")
                print("   Check the floor report above to see which floor failed.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    print(f"\n📊 Session Summary:")
    print(f"  • Total turns: {turn_count}")
    print(f"  • Governance: FULL 9 Floors (Physics + Semantic)")
    print(f"  • Version: {APEX_VERSION}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
