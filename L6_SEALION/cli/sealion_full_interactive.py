#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEA-LION v4 Full Interactive - RAW vs FULL arifOS Pipeline

Complete 000→999 pipeline with:
- Real metrics computation from LLM responses
- Full APEX PRIME measurement
- W@W Federation (@LAW, @GEOX, @WELL, @RIF)
- GENIUS metrics (G, C_dark)
- Wisdom-Gated Release (Budi v45Ω)

Usage:
    python scripts/sealion_full_interactive.py

Commands:
    /raw        - Show only RAW output
    /governed   - Show only GOVERNED output (full pipeline)
    /both       - Show both side-by-side (default)
    /verbose    - Toggle verbose mode (show all stages)
    /help       - Show commands
    /quit       - Exit

Requires:
    $env:ARIF_LLM_API_KEY = "your-sealion-api-key"
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
from L7_DEMOS.examples.arifos_caged_llm_demo import cage_llm_response
from arifos_core.system.apex_prime import Verdict


class SEALIONFullInteractive:
    """Full arifOS pipeline interactive tester"""

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
            print("\nSet environment variable:")
            print("  $env:ARIF_LLM_API_KEY = 'your-sealion-api-key'")
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
        print("SEA-LION v4 FULL PIPELINE - RAW vs GOVERNED (v45Ω)".center(80))
        print("=" * 80)
        print()
        print(f"Model: {self.model}")
        print(f"API: {self.api_base}")
        print(f"Pipeline: 000→111→333→444→555→666→888→999 (Full Stack)")
        print(f"Mode: {self.mode.upper()}")
        print(f"Verbose: {'ON' if self.verbose else 'OFF'}")
        print()
        print("Commands: /raw | /governed | /both | /verbose | /help | /quit")
        print("=" * 80)
        print()

    def show_help(self):
        """Show help"""
        print()
        print("Commands:")
        print("  /raw        - RAW output only (no governance)")
        print("  /governed   - GOVERNED output only (full pipeline)")
        print("  /both       - Side-by-side comparison (default)")
        print("  /verbose    - Toggle verbose (show all pipeline stages)")
        print("  /help       - Show this help")
        print("  /quit       - Exit")
        print()
        print("Pipeline Stages (Full 000→999):")
        print("  000 VOID     - Session initialization")
        print("  111 SENSE    - Context gathering")
        print("  333 REASON   - Logic generation")
        print("  444 EVIDENCE - Claim validation")
        print("  555 EMPATHY  - Empathy check")
        print("  666 ALIGN    - Constitutional alignment")
        print("  888 JUDGE    - APEX PRIME verdict")
        print("  999 SEAL     - Final release")
        print()
        print("Wisdom-Gated Release (Budi v45Ω):")
        print("  PHATIC: Truth exempt (greetings)")
        print("  SOFT:   Truth ≥ 0.80 (educational)")
        print("  HARD:   Truth ≥ 0.90 (factual)")
        print()

    def call_raw(self, prompt: str) -> str:
        """Call LLM without governance"""
        try:
            return self.generate(prompt)
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    def call_governed(self, prompt: str) -> dict:
        """Call LLM through FULL arifOS pipeline"""
        try:
            # Wrapper for cage_llm_response
            def call_model_wrapper(messages):
                user_content = ""
                for msg in messages:
                    if msg.get("role") == "user":
                        user_content = msg.get("content", "")
                        break
                return self.generate(user_content)

            # Run through FULL pipeline (000→999)
            result = cage_llm_response(
                prompt=prompt,
                call_model=call_model_wrapper,
                high_stakes=False,
                run_waw=True,  # Enable W@W Federation
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
                    "F9_Anti_Hantu": 1.0 if metrics_obj.anti_hantu else 0.0,
                }

            # Compute Psi (if available)
            psi = metrics_obj.psi if metrics_obj and metrics_obj.psi else 0.0

            # Extract lane information (v45Ω Patch B)
            # Lane is stored in CagedResult or pipeline state
            from arifos_core.enforcement.metrics import get_lane_truth_threshold
            lane = "UNKNOWN"
            # Try to get from result attributes
            if hasattr(result, '_raw_state') and hasattr(result._raw_state, 'applicability_lane'):
                lane = result._raw_state.applicability_lane

            # Get lane-specific truth threshold
            lane_threshold = get_lane_truth_threshold(lane)

            # GENIUS metrics
            genius_index = 0.0
            dark_cleverness = 0.0
            if result.genius_verdict:
                genius_index = result.genius_verdict.genius_index
                dark_cleverness = result.genius_verdict.dark_cleverness

            # Verdict
            verdict_str = str(result.verdict)
            if hasattr(result.verdict, 'verdict'):
                verdict_str = str(result.verdict.verdict.value)

            return {
                "success": True,
                "verdict": verdict_str,
                "response": result.final_response,
                "raw_response": result.raw_llm_response,
                "floor_scores": floor_scores,
                "psi": psi,
                "genius_index": genius_index,
                "dark_cleverness": dark_cleverness,
                "stage_trace": result.stage_trace,
                "waw_verdict": str(result.waw_verdict) if result.waw_verdict else None,
                "eye_blocking": result.eye_blocking,
                "lane": lane,  # v45Ω Patch B
                "lane_threshold": lane_threshold,  # v45Ω Patch B
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "verdict": "ERROR",
                "response": f"[PIPELINE_ERROR: {str(e)}]",
                "error": str(e),
                "error_detail": traceback.format_exc(),
            }

    def process_prompt(self, prompt: str):
        """Process prompt based on mode"""
        print()

        if self.mode == "raw":
            # RAW mode
            print("=" * 80)
            print("RAW OUTPUT (No Governance)".center(80))
            print("=" * 80)
            print()
            print("⏳ Calling LLM...")
            start_time = time.time()
            response = self.call_raw(prompt)
            elapsed = time.time() - start_time
            print(f"✅ Response ({elapsed:.2f}s, {len(response)} chars)\n")
            print(response)
            print("\n" + "=" * 80 + "\n")

        elif self.mode == "governed":
            # GOVERNED mode
            print("=" * 80)
            print("GOVERNED (Full Pipeline 000→999)".center(80))
            print("=" * 80)
            print()

            print("⏳ Running full pipeline...")
            start_time = time.time()
            result = self.call_governed(prompt)
            elapsed = time.time() - start_time
            print(f"✅ Pipeline complete ({elapsed:.2f}s)\n")

            # Show pipeline trace if verbose
            if self.verbose and "stage_trace" in result:
                stages = result.get("stage_trace", [])
                if stages:
                    print("Pipeline Stages:")
                    for stage in stages:
                        print(f"  → {stage}")
                    print()

            # Show lane classification (v45Ω Patch B)
            lane = result.get("lane", "UNKNOWN")
            lane_threshold = result.get("lane_threshold", 0.99)
            lane_emoji = {
                "PHATIC": "🟢",
                "SOFT": "🟡",
                "HARD": "🔴",
                "REFUSE": "🚫",
            }.get(lane, "❓")
            print(f"🔀 LANE: {lane_emoji} {lane} (Truth threshold: {lane_threshold:.2f})")

            # Show verdict
            verdict = result.get("verdict", "UNKNOWN")
            verdict_emoji = "🟢" if verdict == "SEAL" else (
                "🟡" if verdict in ["PARTIAL", "SABAR"] else "🔴"
            )
            print(f"⚖️  VERDICT: {verdict} {verdict_emoji}")

            # Show metrics
            psi = result.get("psi", 0.0)
            g = result.get("genius_index", 0.0)
            c_dark = result.get("dark_cleverness", 0.0)
            print(f"⚙️  Ψ (Vitality): {psi:.3f}")
            print(f"⚙️  G (GENIUS): {g:.2f}")
            print(f"⚙️  C_dark: {c_dark:.2f}")
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

                # W@W verdict
                waw = result.get("waw_verdict")
                if waw:
                    print(f"W@W Federation: {waw}")
                    print()

            # Show response
            if verdict in ["SEAL", "PARTIAL"]:
                print("─" * 80)
                print("📤 GOVERNED OUTPUT:")
                print()
                print(result.get("response", "[No response]"))
                print("\n" + "─" * 80 + "\n")
            else:
                print("🚫 OUTPUT BLOCKED\n")

        else:  # both
            # Side-by-side
            print("=" * 80)
            print("RAW vs GOVERNED (Full Pipeline)".center(80))
            print("=" * 80)
            print()

            # RAW
            print("⏳ Calling RAW LLM...")
            start_time = time.time()
            raw_response = self.call_raw(prompt)
            raw_elapsed = time.time() - start_time
            print(f"✅ RAW complete ({raw_elapsed:.2f}s)")

            # GOVERNED
            print("⏳ Running full pipeline...")
            start_time = time.time()
            gov_result = self.call_governed(prompt)
            gov_elapsed = time.time() - start_time
            print(f"✅ Pipeline complete ({gov_elapsed:.2f}s)")
            print()

            # Show RAW
            print("─" * 35 + " RAW " + "─" * 40)
            raw_preview = raw_response[:200] + "..." if len(raw_response) > 200 else raw_response
            print(raw_preview)
            print()

            # Show GOVERNED
            verdict = gov_result.get("verdict", "UNKNOWN")
            verdict_emoji = "🟢" if verdict == "SEAL" else (
                "🟡" if verdict in ["PARTIAL", "SABAR"] else "🔴"
            )
            psi = gov_result.get("psi", 0.0)
            g = gov_result.get("genius_index", 0.0)
            c_dark = gov_result.get("dark_cleverness", 0.0)
            lane = gov_result.get("lane", "UNKNOWN")
            lane_threshold = gov_result.get("lane_threshold", 0.99)
            lane_emoji = {
                "PHATIC": "🟢",
                "SOFT": "🟡",
                "HARD": "🔴",
                "REFUSE": "🚫",
            }.get(lane, "❓")

            print("─" * 30 + " GOVERNED " + "─" * 39)
            print(f"Lane: {lane_emoji} {lane} (threshold: {lane_threshold:.2f})")
            print(f"Verdict: {verdict} {verdict_emoji} | Ψ: {psi:.3f} | G: {g:.2f} | C_dark: {c_dark:.2f}")
            print()

            if verdict in ["SEAL", "PARTIAL"]:
                response_text = gov_result.get("response", "[No response]")
                gov_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(gov_preview)
            else:
                print("🚫 BLOCKED")
            print()

            # Verbose details
            if self.verbose:
                # Pipeline stages
                stages = gov_result.get("stage_trace", [])
                if stages:
                    print("Pipeline: " + " → ".join(stages))
                    print()

                # Floor scores
                floor_scores = gov_result.get("floor_scores", {})
                if floor_scores:
                    print("Floors: ", end="")
                    for floor, score in sorted(floor_scores.items()):
                        status = "✓" if score >= 0.85 else ("⚠" if score >= 0.50 else "✗")
                        print(f"{status}{floor[-5:]}:{score:.2f} ", end="")
                    print("\n")

            print("=" * 80)
            print()

    def run(self):
        """Run interactive REPL"""
        self.show_banner()

        print("Type your prompt to see RAW vs GOVERNED comparison")
        print("Commands: /help | /raw | /governed | /both | /verbose | /quit")
        print("─" * 80 + "\n")

        while True:
            try:
                prompt = input("🦁 > ").strip()

                if not prompt:
                    continue

                # Commands
                if prompt.lower() in ["/quit", "/exit", "/q"]:
                    print("\n👋 Goodbye!\n")
                    break

                if prompt.lower() == "/help":
                    self.show_help()
                    continue

                if prompt.lower() == "/raw":
                    self.mode = "raw"
                    print("\n✓ RAW mode\n")
                    continue

                if prompt.lower() == "/governed":
                    self.mode = "governed"
                    print("\n✓ GOVERNED mode (full pipeline)\n")
                    continue

                if prompt.lower() == "/both":
                    self.mode = "both"
                    print("\n✓ BOTH mode (side-by-side)\n")
                    continue

                if prompt.lower() == "/verbose":
                    self.verbose = not self.verbose
                    print(f"\n✓ Verbose: {'ON' if self.verbose else 'OFF'}\n")
                    continue

                # Process
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
        tester = SEALIONFullInteractive()
        tester.run()
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
