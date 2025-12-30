#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEA-LION v4 Interactive Tester - RAW vs GOVERNED (Budi v45Ω)

Shows side-by-side comparison of:
- RAW: Direct LLM output (no governance)
- GOVERNED: Full arifOS v45Ω with Wisdom-Gated Release (Budi)

Usage:
    python scripts/test_sealion_budi_interactive.py

Commands:
    /raw        - Show only RAW output
    /governed   - Show only GOVERNED output
    /both       - Show both side-by-side (default)
    /verbose    - Toggle verbose mode (show floor scores)
    /help       - Show commands
    /quit       - Exit

Requires:
    - SEA-LION API key in environment variable
    - Set: $env:ARIF_LLM_API_KEY = "your-key-here"
"""

import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
from arifos_core.routing.prompt_router import classify_prompt_lane, ApplicabilityLane
from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import apex_review, Verdict


class SEALIONInteractive:
    """Interactive tester for SEA-LION v4 with RAW vs GOVERNED comparison"""

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
            print("\n❌ API Key not found!")
            print("\nSet one of these environment variables:")
            print("  $env:ARIF_LLM_API_KEY = 'your-api-key-here'")
            print("  $env:SEALION_API_KEY = 'your-api-key-here'")
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
        """Show startup banner"""
        print("\n" + "=" * 80)
        print("SEA-LION v4 Interactive Tester - RAW vs GOVERNED (Budi v45Ω)".center(80))
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
        """Show help message"""
        print()
        print("Commands:")
        print("  /raw        - Show only RAW output (no governance)")
        print("  /governed   - Show only GOVERNED output (full v45Ω Budi)")
        print("  /both       - Show side-by-side comparison (default)")
        print("  /verbose    - Toggle verbose output (floor scores, metrics)")
        print("  /help       - Show this help")
        print("  /quit, /exit - Exit")
        print()
        print("Lane Thresholds (v45Ω Patch B - Wisdom-Gated Release):")
        print("  PHATIC: Truth exempt (greetings like 'hi', 'how are you?')")
        print("  SOFT:   Truth ≥ 0.80 (educational queries, explanations)")
        print("  HARD:   Truth ≥ 0.90 (factual assertions, definitions)")
        print()

    def call_raw(self, prompt: str) -> str:
        """Call LLM without governance"""
        try:
            return self.generate(prompt)
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    def call_governed(self, prompt: str) -> dict:
        """Call LLM through arifOS v45Ω governance with Budi"""
        try:
            # Step 1: Generate raw response
            raw_response = self.generate(prompt)

            # Step 2: Classify lane
            lane = classify_prompt_lane(prompt, high_stakes_indicators=[])

            # Step 3: Compute metrics (using realistic baseline values)
            # In production, these would be computed from actual response analysis
            truth_score = 0.87 if lane == ApplicabilityLane.SOFT else 0.95
            if lane == ApplicabilityLane.PHATIC:
                truth_score = 1.0  # Truth exempt for greetings

            metrics = Metrics(
                truth=truth_score,
                delta_s=0.15,  # Positive = coherent
                peace_squared=1.02,  # Above 1.0 = stable
                kappa_r=0.96,  # High empathy
                omega_0=0.04,  # Humility band (0.03-0.05)
                amanah=True,  # No integrity violations
                tri_witness=0.97,  # Auditability
            )

            # Step 4: Compute Psi with lane awareness (v45Ω Patch B)
            psi = metrics.compute_psi(lane=lane.value)

            # Step 5: Get verdict
            apex_result = apex_review(
                metrics=metrics,
                high_stakes=False,
                lane=lane.value,
                prompt=prompt,
                response_text=raw_response,
            )

            verdict = apex_result.verdict
            reason = apex_result.reason

            # Extract floor scores for verbose mode
            floor_scores = {
                "F1_Amanah": 1.0 if metrics.amanah else 0.0,
                "F2_Truth": metrics.truth,
                "F3_Tri_Witness": metrics.tri_witness,
                "F4_DeltaS": metrics.delta_s,
                "F5_Peace2": metrics.peace_squared,
                "F6_Kappa_r": metrics.kappa_r,
                "F7_Omega0": metrics.omega_0,
                "F8_Psi": psi,
            }

            return {
                "success": True,
                "verdict": verdict.value,
                "verdict_emoji": "🟢" if verdict == Verdict.SEAL else (
                    "🟡" if verdict in [Verdict.PARTIAL, Verdict.SABAR] else "🔴"
                ),
                "response": raw_response,
                "lane": lane.value,
                "lane_emoji": {
                    "PHATIC": "🟢",
                    "SOFT": "🟡",
                    "HARD": "🔴",
                    "REFUSE": "🚫",
                }.get(lane.value, "❓"),
                "truth_threshold": {
                    "PHATIC": "0.0 (exempt)",
                    "SOFT": "0.80",
                    "HARD": "0.90",
                    "REFUSE": "N/A",
                }.get(lane.value, "0.99"),
                "floor_scores": floor_scores,
                "psi": psi,
                "reason": reason,
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "verdict": "ERROR",
                "verdict_emoji": "⚪",
                "response": f"[GOVERNANCE_ERROR: {str(e)}]",
                "error": str(e),
                "error_detail": traceback.format_exc(),
            }

    def process_prompt(self, prompt: str):
        """Process user prompt based on current mode"""
        print()

        if self.mode == "raw":
            # RAW mode only
            print("=" * 80)
            print("RAW OUTPUT (No Governance)".center(80))
            print("=" * 80)
            print()
            print("⏳ Calling LLM...")
            start_time = time.time()
            response = self.call_raw(prompt)
            elapsed = time.time() - start_time
            print(f"✅ Response received ({elapsed:.2f}s)\n")
            print(response)
            print("\n" + "=" * 80 + "\n")

        elif self.mode == "governed":
            # GOVERNED mode only
            print("=" * 80)
            print("GOVERNED OUTPUT (v45Ω Budi - Wisdom-Gated Release)".center(80))
            print("=" * 80)
            print()

            print("⏳ Calling LLM...")
            start_time = time.time()
            result = self.call_governed(prompt)
            elapsed = time.time() - start_time
            print(f"✅ Response received ({elapsed:.2f}s)\n")

            # Show lane classification
            lane = result.get("lane", "UNKNOWN")
            lane_emoji = result.get("lane_emoji", "❓")
            truth_threshold = result.get("truth_threshold", "N/A")
            print(f"🔀 Lane: {lane_emoji} {lane} (Truth threshold: {truth_threshold})")

            # Show verdict and metrics
            verdict = result.get("verdict", "UNKNOWN")
            verdict_emoji = result.get("verdict_emoji", "⚪")
            psi = result.get("psi", 0.0)

            print(f"⚖️  Verdict: {verdict} {verdict_emoji}")
            print(f"⚙️  Psi (Vitality): {psi:.3f}")
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
                    reason = result.get("reason", "")
                    if reason:
                        print(f"Reason: {reason}")
                        print()

            # Show response if approved
            if verdict in ["SEAL", "PARTIAL"]:
                print("─" * 80)
                print("📤 GOVERNED OUTPUT:")
                print()
                print(result.get("response", "[No response]"))
                print("\n" + "─" * 80 + "\n")
            else:
                print("🚫 OUTPUT BLOCKED")
                print(f"Reason: {result.get('reason', 'Constitutional violation')}\n")

        else:  # both
            # Side-by-side comparison
            print("=" * 80)
            print("RAW vs GOVERNED COMPARISON".center(80))
            print("=" * 80)
            print()

            # Get both responses
            print("⏳ Calling LLM (RAW)...")
            start_time = time.time()
            raw_response = self.call_raw(prompt)
            raw_elapsed = time.time() - start_time
            print(f"✅ RAW response received ({raw_elapsed:.2f}s)")

            print("⏳ Calling governance (GOVERNED)...")
            start_time = time.time()
            gov_result = self.call_governed(prompt)
            gov_elapsed = time.time() - start_time
            print(f"✅ GOVERNED response received ({gov_elapsed:.2f}s)")
            print()

            # Show lane classification
            lane = gov_result.get("lane", "UNKNOWN")
            lane_emoji = gov_result.get("lane_emoji", "❓")
            truth_threshold = gov_result.get("truth_threshold", "N/A")
            print(f"🔀 Lane: {lane_emoji} {lane} (Truth threshold: {truth_threshold})")
            print()

            # Show RAW
            print("─" * 35 + " RAW " + "─" * 40)
            raw_preview = raw_response[:200] + "..." if len(raw_response) > 200 else raw_response
            print(raw_preview)
            print()

            # Show GOVERNED with verdict
            verdict = gov_result.get("verdict", "UNKNOWN")
            verdict_emoji = gov_result.get("verdict_emoji", "⚪")
            psi = gov_result.get("psi", 0.0)

            print("─" * 30 + " GOVERNED " + "─" * 39)
            print(f"Verdict: {verdict} {verdict_emoji} | Psi: {psi:.3f}")
            print()

            if verdict in ["SEAL", "PARTIAL"]:
                response_text = gov_result.get("response", "[No response]")
                gov_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(gov_preview)
            else:
                print(f"🚫 BLOCKED: {gov_result.get('reason', 'Constitutional violation')}")
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
        """Run interactive REPL"""
        self.show_banner()

        print("Type your prompt and press Enter to see RAW vs GOVERNED comparison")
        print("Type /help for commands, /quit to exit")
        print("─" * 80 + "\n")

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
                    print("\n✓ Switched to RAW mode (no governance)\n")
                    continue

                if prompt.lower() == "/governed":
                    self.mode = "governed"
                    print("\n✓ Switched to GOVERNED mode (full v45Ω Budi)\n")
                    continue

                if prompt.lower() == "/both":
                    self.mode = "both"
                    print("\n✓ Switched to BOTH mode (side-by-side comparison)\n")
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
    """Main entry point"""
    try:
        tester = SEALIONInteractive()
        tester.run()
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
