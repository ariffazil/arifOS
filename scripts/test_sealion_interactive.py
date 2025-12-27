#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_sealion_interactive.py — Interactive Governed Testing for SEA-LION v4

Interactive REPL for testing custom prompts with:
- RAW mode: Direct LLM output (no governance)
- GOVERNED mode: Full arifOS v45 constitutional enforcement
- BOTH mode: Side-by-side comparison

Usage:
    python scripts/test_sealion_interactive.py

Commands:
    /raw        - Switch to RAW mode only
    /governed   - Switch to GOVERNED mode only
    /both       - Switch to side-by-side comparison (default)
    /verbose    - Toggle verbose output (floor scores, metrics)
    /help       - Show commands
    /quit, /exit - Exit

Author: arifOS Project
Version: v45.0.0
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
from L7_DEMOS.examples.arifos_caged_llm_demo import cage_llm_response
from arifos_core.system.verdict_emission import (
    compute_agi_score,
    compute_asi_score,
    verdict_to_light,
)
from arifos_core.system.apex_prime import Verdict


class InteractiveGoverned:
    """Interactive testing REPL with Raw vs. Governed toggle."""

    def __init__(self):
        # Configuration
        self.model = "aisingapore/Gemma-SEA-LION-v4-27B-IT"
        self.api_base = os.getenv("ARIF_LLM_API_BASE", "https://api.sea-lion.ai/v1")

        # Get API key
        self.api_key = (
            os.getenv("ARIF_LLM_API_KEY")
            or os.getenv("SEALION_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        if not self.api_key:
            print("\n[ERROR] API key not found!")
            print("\nSet one of these environment variables:")
            print("  - ARIF_LLM_API_KEY")
            print("  - SEALION_API_KEY")
            print("  - LLM_API_KEY")
            print("  - OPENAI_API_KEY")
            print("\nOr create .env file with:")
            print('  ARIF_LLM_API_KEY="your-api-key-here"')
            sys.exit(1)

        # Initialize LiteLLM
        config = LiteLLMConfig(
            provider="openai",
            api_base=self.api_base,
            api_key=self.api_key,
            model=self.model,
            temperature=0.2,
            max_tokens=512,
        )
        self.generate = make_llm_generate(config)

        # State
        self.mode = "both"  # raw, governed, both
        self.verbose = False

    def show_banner(self):
        """Show startup banner."""
        print("\n" + "=" * 80)
        print("INTERACTIVE GOVERNED TESTING - arifOS v45 + SEA-LION v4".center(80))
        print("=" * 80)
        print()
        print(f"Model: {self.model}")
        print(f"API: {self.api_base}")
        print(f"Mode: {self.mode.upper()} (use /raw, /governed, /both to switch)")
        print(f"Verbose: {'ON' if self.verbose else 'OFF'} (use /verbose to toggle)")
        print()
        print("Commands: /raw | /governed | /both | /verbose | /help | /quit")
        print("=" * 80)
        print()

    def show_help(self):
        """Show help message."""
        print()
        print("Commands:")
        print("  /raw        - Switch to RAW mode only (no governance)")
        print("  /governed   - Switch to GOVERNED mode only (full v45 stack)")
        print("  /both       - Switch to side-by-side comparison (default)")
        print("  /verbose    - Toggle verbose output (floor scores, metrics)")
        print("  /help       - Show this help")
        print("  /quit, /exit - Exit")
        print()

    def call_raw(self, prompt: str) -> Optional[str]:
        """Call LLM without governance."""
        try:
            return self.generate(prompt)
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    def call_governed(self, prompt: str) -> dict:
        """Call LLM through arifOS v45 governance."""
        try:
            # Wrapper for cage_llm_response
            def call_model_wrapper(messages):
                user_content = ""
                for msg in messages:
                    if msg.get("role") == "user":
                        user_content = msg.get("content", "")
                        break
                return self.generate(user_content)

            # Run through governance
            result = cage_llm_response(
                prompt=prompt,
                call_model=call_model_wrapper,
                high_stakes=False,
                run_waw=True,
            )

            # Extract metrics
            metrics_obj = result.metrics
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
                    "F8_GENIUS": result.genius_verdict.genius_index if result.genius_verdict else 0.0,
                    "F9_Anti_Hantu": 1.0 if metrics_obj.anti_hantu else 0.0,
                }

            # Compute AGI/ASI
            agi_score = compute_agi_score(metrics_obj) if metrics_obj else 0.0
            asi_score = compute_asi_score(metrics_obj) if metrics_obj else 0.0

            # Get verdict light
            try:
                verdict_enum = Verdict.from_string(str(result.verdict))
                light = verdict_to_light(verdict_enum)
                apex_light_str = str(light)
            except (ValueError, AttributeError):
                apex_light_str = "🟢" if str(result.verdict) == "SEAL" else (
                    "🔴" if str(result.verdict) == "VOID" else "🟡"
                )

            return {
                "success": True,
                "verdict": str(result.verdict),
                "apex_light": apex_light_str,
                "response": result.final_response,
                "raw_response": result.raw_llm_response,
                "floor_scores": floor_scores,
                "agi_score": agi_score,
                "asi_score": asi_score,
                "pipeline_trace": result.stage_trace,
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "verdict": "ERROR",
                "apex_light": "⚪",
                "response": f"[GOVERNANCE_ERROR: {str(e)}]",
                "error": str(e),
                "error_detail": traceback.format_exc(),
            }

    def process_prompt(self, prompt: str):
        """Process user prompt based on current mode."""
        print()

        if self.mode == "raw":
            # RAW mode only
            print("=" * 80)
            print("RAW OUTPUT (No Governance)".center(80))
            print("=" * 80)
            print()
            response = self.call_raw(prompt)
            print(response)
            print()

        elif self.mode == "governed":
            # GOVERNED mode only
            print("=" * 80)
            print("GOVERNED OUTPUT (Full v45 Stack)".center(80))
            print("=" * 80)
            print()

            result = self.call_governed(prompt)

            # Show verdict and metrics
            verdict = result.get("verdict", "UNKNOWN")
            light = result.get("apex_light", "⚪")
            agi = result.get("agi_score", 0.0)
            asi = result.get("asi_score", 0.0)

            print(f"Verdict: {verdict} {light}")
            print(f"AGI: {agi:.2f} | ASI: {asi:.2f}")
            print()

            # Show floor scores if verbose
            if self.verbose:
                floor_scores = result.get("floor_scores", {})
                if floor_scores:
                    print("Floor Scores:")
                    for floor, score in sorted(floor_scores.items()):
                        status = "✓" if score >= 0.85 else ("⚠" if score >= 0.50 else "✗")
                        print(f"  {status} {floor}: {score:.2f}")
                    print()

            # Show response
            print("-" * 80)
            print(result.get("response", "[No response]"))
            print("-" * 80)
            print()

        else:  # both
            # Side-by-side comparison
            print("=" * 80)
            print("RAW vs GOVERNED COMPARISON".center(80))
            print("=" * 80)
            print()

            # Get both responses
            raw_response = self.call_raw(prompt)
            gov_result = self.call_governed(prompt)

            # Show RAW
            print("─" * 40 + " RAW " + "─" * 34)
            print(raw_response[:200] + "..." if len(raw_response) > 200 else raw_response)
            print()

            # Show GOVERNED with verdict
            verdict = gov_result.get("verdict", "UNKNOWN")
            light = gov_result.get("apex_light", "⚪")
            agi = gov_result.get("agi_score", 0.0)
            asi = gov_result.get("asi_score", 0.0)

            print("─" * 35 + " GOVERNED " + "─" * 34)
            print(f"Verdict: {verdict} {light} | AGI: {agi:.2f} | ASI: {asi:.2f}")
            print()
            response_text = gov_result.get("response", "[No response]")
            print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
            print()

            # Show floor scores if verbose
            if self.verbose:
                floor_scores = gov_result.get("floor_scores", {})
                if floor_scores:
                    print("Floor Scores:")
                    for floor, score in sorted(floor_scores.items()):
                        status = "✓" if score >= 0.85 else ("⚠" if score >= 0.50 else "✗")
                        print(f"  {status} {floor}: {score:.2f}")
                    print()

            print("=" * 80)
            print()

    def run(self):
        """Run interactive REPL."""
        self.show_banner()

        while True:
            try:
                # Get prompt
                prompt = input("🦁 > ").strip()

                if not prompt:
                    continue

                # Handle commands
                if prompt.lower() in ["/quit", "/exit", "/q"]:
                    print("\n👋 Goodbye!\n")
                    break

                if prompt.lower() == "/help":
                    self.show_help()
                    continue

                if prompt.lower() == "/raw":
                    self.mode = "raw"
                    print(f"\n✓ Switched to RAW mode (no governance)\n")
                    continue

                if prompt.lower() == "/governed":
                    self.mode = "governed"
                    print(f"\n✓ Switched to GOVERNED mode (full v45 stack)\n")
                    continue

                if prompt.lower() == "/both":
                    self.mode = "both"
                    print(f"\n✓ Switched to BOTH mode (side-by-side comparison)\n")
                    continue

                if prompt.lower() == "/verbose":
                    self.verbose = not self.verbose
                    print(f"\n✓ Verbose mode: {'ON' if self.verbose else 'OFF'}\n")
                    continue

                # Process normal prompt
                self.process_prompt(prompt)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                break


def main():
    """Main entry point."""
    try:
        repl = InteractiveGoverned()
        repl.run()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
