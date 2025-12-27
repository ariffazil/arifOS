#!/usr/bin/env python3
"""
forge_interactive.py - Interactive CLI for v45Ω Sovereign Witness Testing

DITEMPA, BUKAN DIBERI. Forged, not given.

This script provides a lightweight REPL for manually testing prompts through
the full arifOS v45 governance pipeline with SEA-LION v4.

Usage:
    python scripts/forge_interactive.py

Commands:
    /999, exit, quit - End session
    Any other text - Submit as governed prompt

Emission Format (Option D):
    AGI | ASI | APEX (🟢/🟡/🔴)
    Governed Response + Floor diagnostics

TRM Integration:
    All prompts are classified via keyword detection (TRM classifier).
    Category defaults to "UNKNOWN" but TRM auto-detects:
    - IDENTITY_FACT (who/what questions about arifOS)
    - SAFETY_REFUSAL (weapons, harmful content)
    - BENIGN_DENIAL (soul/consciousness questions)
    - CLARITY_CONSTRAINT (emoji-only, nonsense)
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.connectors.litellm_gateway import make_llm_generate
from L7_DEMOS.examples.arifos_caged_llm_demo import cage_llm_response
from arifos_core.system.apex_prime import (
    compute_agi_score,
    compute_asi_score,
    verdict_to_light,
    Verdict,
)


def print_banner(model: str):
    """
    Print session initialization banner.

    Args:
        model: Actual model name being used (from config, not hardcoded)
    """
    print()
    print("=" * 70)
    print("arifOS v45Ω - Sovereign Witness Interactive Forge".center(70))
    print("=" * 70)
    print()
    print("DITEMPA, BUKAN DIBERI — Forged, not given; truth must cool.")
    print()
    print(f"Model: {model}")
    print("Governance: Full v45 Constitutional Stack")
    print("  • 9 Constitutional Floors (F1-F9)")
    print("  • TEARFRAME Physics (Entropy + Ψ vitality)")
    print("  • W@W Federation (5 organs)")
    print("  • GENIUS LAW (G index + C_dark)")
    print("  • Truth Reality Map (TRM exemptions)")
    print()
    print("Commands:")
    print("  Type any prompt to test governance")
    print("  Type 'exit', 'quit', or '/999' to end session")
    print()
    print("=" * 70)
    print()


def print_result(result: dict, prompt: str):
    """
    Print governed result in Option D refined format.

    Args:
        result: Dict from cage_llm_response with verdict, response, metrics
        prompt: Original user prompt
    """
    verdict = result.get("verdict", "UNKNOWN")
    governed_response = result.get("governed_response", "")
    raw_response = result.get("raw_response", "")
    floor_scores = result.get("floor_scores", {})
    physics = result.get("physics", {})
    metrics = result.get("metrics", {})
    metrics_obj = result.get("metrics_obj", None)

    # Emission format (Option D)
    print()
    if metrics_obj:
        agi_score = compute_agi_score(metrics_obj)
        asi_score = compute_asi_score(metrics_obj)

        # Map verdict string to Verdict enum for light
        try:
            verdict_enum = Verdict.from_string(verdict)
            light = verdict_to_light(verdict_enum)
            light_str = str(light)
        except (ValueError, AttributeError):
            # Fallback mapping
            light_str = "🟢" if verdict == "SEAL" else ("🔴" if verdict == "VOID" else "🟡")

        print("=" * 60)
        print(f"AGI: {agi_score:.2f} | ASI: {asi_score:.2f} | APEX: {light_str}")
        print("=" * 60)
    else:
        # Fallback if metrics not available
        verdict_symbol = {
            "SEAL": "✓",
            "PARTIAL": "⚠",
            "SABAR": "⏸",
            "VOID": "✗",
            "HOLD_888": "⏳",
        }.get(verdict, "?")
        print(f"{verdict_symbol} Verdict: {verdict}")

    print()
    print(f"Governed Response:")
    print(f"  {governed_response}")
    print()

    # Floor diagnostics
    if floor_scores:
        print("Floor Scores:")
        for floor, score in sorted(floor_scores.items()):
            status = "✓" if (
                (floor == "F1_Amanah" and score >= 1.0)
                or (floor == "F2_Truth" and score >= 0.90)
                or (floor == "F3_Tri_Witness" and score >= 0.95)
                or (floor == "F4_DeltaS" and score >= 0.0)
                or (floor == "F5_Peace2" and score >= 1.0)
                or (floor == "F6_Kappa_r" and score >= 0.95)
                or (floor == "F7_Omega0" and 0.03 <= score <= 0.05)
                or (floor == "F9_Anti_Hantu" and score >= 1.0)
            ) else "✗"
            print(f"  {status} {floor}: {score:.2f}")
        print()

    # TEARFRAME physics
    if physics:
        psi = physics.get("psi", 0.0)
        entropy = physics.get("entropy", 0.0)
        print(f"TEARFRAME Physics:")
        print(f"  Entropy: {entropy:.3f}")
        print(f"  Psi (vitality): {psi:.3f}")
        print()

    # GENIUS metrics
    if metrics:
        g = metrics.get("genius", 0.0)
        c_dark = metrics.get("c_dark", 0.0)
        print(f"GENIUS Metrics:")
        print(f"  G (Governed Intelligence): {g:.2f}")
        print(f"  C_dark (Dark Cleverness): {c_dark:.2f}")
        print()

    print("-" * 70)


def interactive_session():
    """
    Main interactive REPL loop.

    Continuously prompts for user input and runs through v45Ω governance.
    """
    # /000 Initialization - Load config FIRST
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if not api_key:
        print()
        print("[ERROR] ARIF_LLM_API_KEY not set!")
        print()
        print("Set your SEA-LION API key in .env:")
        print("  ARIF_LLM_API_KEY='your-key-here'")
        print("  ARIF_LLM_API_BASE='https://api.sea-lion.ai/v1'  # Optional")
        print("  ARIF_LLM_MODEL='aisingapore/Qwen-SEA-LION-v4-32B-IT'  # Optional")
        print()
        print("Get your key at: https://playground.sea-lion.ai")
        return 1

    # Configuration - determine ACTUAL model being used
    model = os.getenv("ARIF_LLM_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")
    api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")

    # Print banner with ACTUAL model (not hardcoded)
    print_banner(model)

    print(f"[CONFIG] Model: {model}")
    print(f"[CONFIG] API Base: {api_base}")
    print(f"[CONFIG] API Key: {api_key[:12]}...{api_key[-4:]}")
    print()

    # Initialize LLM (reads from environment variables)
    try:
        generate = make_llm_generate()
        print("[✓] LiteLLM gateway initialized")
        print("[✓] arifOS v45 governance loaded")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to initialize LLM: {e}")
        print("Check your ARIF_LLM_API_KEY and ARIF_LLM_API_BASE settings")
        return 1

    prompt_count = 0

    # Main REPL loop
    while True:
        try:
            # Get user input
            prompt = input("\n> ").strip()

            # Exit commands
            if prompt.lower() in ["exit", "quit", "/999"]:
                print()
                print("=" * 70)
                print(f"Session complete. {prompt_count} prompts governed.")
                print("DITEMPA, BUKAN DIBERI.")
                print("=" * 70)
                print()
                break

            # Skip empty prompts
            if not prompt:
                continue

            prompt_count += 1
            print(f"\n[GOVERNED] Running prompt #{prompt_count} through v45Ω pipeline...")

            # Create wrapper for cage_llm_response
            def call_model_wrapper(messages):
                """Convert messages to string and call LiteLLM."""
                user_content = ""
                for msg in messages:
                    if msg.get("role") == "user":
                        user_content = msg.get("content", "")
                        break
                return generate(user_content)

            # Run through governance cage
            # Note: TRM classification happens via keyword detection in apex_review
            # Full category passing would require modifying cage_llm_response (non-F0)
            caged_result = cage_llm_response(
                prompt=prompt,
                call_model=call_model_wrapper,
                high_stakes=False,
                run_waw=True,
            )

            # Convert CagedResult to dict format
            metrics_obj = caged_result.metrics
            floor_scores = {}
            if metrics_obj:
                floor_scores = {
                    "F1_Amanah": 1.0 if metrics_obj.amanah else 0.0,
                    "F2_Truth": metrics_obj.truth,
                    "F3_Tri_Witness": metrics_obj.tri_witness,
                    "F4_DeltaS": metrics_obj.delta_s,
                    "F5_Peace2": metrics_obj.peace_squared,
                    "F6_Kappa_r": metrics_obj.kappa_r,
                    "F7_Omega0": metrics_obj.omega_0,
                    "F9_Anti_Hantu": 1.0 if metrics_obj.anti_hantu else 0.0,
                }

            genius_verdict = getattr(caged_result, "genius_verdict", None)
            physics = {
                "entropy": genius_verdict.entropy if genius_verdict else 0.0,
                "temperature": 0.0,
                "psi": genius_verdict.psi_apex if genius_verdict else 0.0,
            }

            metrics = {
                "genius": genius_verdict.genius_index if genius_verdict else 0.0,
                "c_dark": genius_verdict.dark_cleverness if genius_verdict else 0.0,
            }

            result = {
                "verdict": str(caged_result.verdict),
                "governed_response": caged_result.final_response,
                "raw_response": caged_result.raw_llm_response,
                "floor_scores": floor_scores,
                "pipeline_trace": caged_result.stage_trace,
                "physics": physics,
                "metrics": metrics,
                "metrics_obj": metrics_obj,
            }

            # Display result
            print_result(result, prompt)

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Session cancelled by user.")
            print()
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            print("\nContinuing session...\n")

    return 0


def main():
    """Entry point."""
    return interactive_session()


if __name__ == "__main__":
    sys.exit(main())
