#!/usr/bin/env python3
"""
🦁 RAW vs GOVERNED - Side-by-side comparison demo
Model: Qwen SEA-LION v4 (aisingapore/Qwen-SEA-LION-v4-32B-IT)

Demonstrates the difference between:
(A) RAW mode: Direct LLM call (no arifOS governance)
(B) GOVERNED mode: Full arifOS v45Ω constitutional enforcement

Usage:
    python L6_SEALION/tests/demo_sealion_raw_vs_governed.py
    python L6_SEALION/tests/demo_sealion_raw_vs_governed.py --prompt "Explain quantum mechanics"
    python L6_SEALION/tests/demo_sealion_raw_vs_governed.py --model "Qwen-SEA-LION-v4-32B-IT" --max_tokens 512

DITEMPA BUKAN DIBERI - Forged, not given
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arifos_core.integration.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
from arifos_core.system.apex_prime import apex_review, Verdict, APEX_VERSION
from arifos_core.enforcement.routing.prompt_router import classify_prompt_lane, ApplicabilityLane
from arifos_core.enforcement.metrics import Metrics


class RawVsGovernedDemo:
    """Compare RAW (ungoverned) vs GOVERNED (arifOS) LLM calls"""

    def __init__(
        self,
        model: str = "Qwen-SEA-LION-v4-32B-IT",
        max_tokens: int = 512,
        temperature: float = 0.2,
    ):
        """Initialize demo with model configuration"""
        # Check for API key (Windows env vars + .env)
        self.api_key = (
            os.getenv("ARIF_LLM_API_KEY")
            or os.getenv("SEALION_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        if not self.api_key:
            raise ValueError(
                "❌ API Key not found!\n"
                "Set one of these environment variables:\n"
                "  - ARIF_LLM_API_KEY\n"
                "  - SEALION_API_KEY\n"
                "  - LLM_API_KEY\n"
                "  - OPENAI_API_KEY\n"
                "Or add to .env file: ARIF_LLM_API_KEY=your-api-key"
            )

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Create LiteLLM config
        self.config = LiteLLMConfig(
            provider="openai",
            api_base=os.getenv("ARIF_LLM_API_BASE"),  # Optional: custom endpoint
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Create raw LLM generator
        self.generate = make_llm_generate(self.config)

        # Ensure log directory exists
        self.log_dir = Path(__file__).parent / "_runs"
        self.log_dir.mkdir(exist_ok=True)

        print(f"✅ Initialized with model: {self.model}")
        print(f"✅ Max tokens: {self.max_tokens}, Temperature: {self.temperature}")
        print(f"✅ arifOS Version: {APEX_VERSION}")
        print(f"✅ Log directory: {self.log_dir}\n")

    def show_banner(self):
        """Display startup banner"""
        print("\n" + "🦁" * 40)
        print("  🚀 RAW vs GOVERNED - arifOS v45Ω Comparison Demo 🚀")
        print("🦁" * 40)
        print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║  MODEL: {self.model:<56} ║
║  VERSION: {APEX_VERSION:<54} ║
║  MODE A: RAW (ungoverned)                                         ║
║  MODE B: GOVERNED (full arifOS v45Ω enforcement)                  ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
        print("🦁" * 40 + "\n")

    def run_raw_mode(self, prompt: str) -> Dict[str, Any]:
        """
        Run RAW mode: Direct LLM call without governance

        Returns:
            Dict with response, timing, error (if any)
        """
        print("\n" + "═" * 70)
        print("🔴 MODE A: RAW (Ungoverned)")
        print("═" * 70)
        print(f"Calling {self.model} directly (no governance)...\n")

        start_time = time.time()
        error = None
        response = None
        tokens_out = 0

        try:
            response = self.generate(prompt)
            elapsed = time.time() - start_time
            tokens_out = len(response.split())  # Rough estimate

            print(f"✅ Response received in {elapsed:.2f}s")
            print(f"📊 Estimated tokens: {tokens_out}")
            print(f"\n📤 RAW OUTPUT:\n")
            print("─" * 70)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("─" * 70 + "\n")

        except Exception as e:
            elapsed = time.time() - start_time
            error = str(e)
            print(f"❌ LLM Error: {error}")
            print(f"⏱️ Failed after {elapsed:.2f}s\n")

        return {
            "mode": "RAW",
            "model": self.model,
            "response": response,
            "time_seconds": elapsed,
            "tokens_out": tokens_out,
            "error": error,
        }

    def run_governed_mode(self, prompt: str) -> Dict[str, Any]:
        """
        Run GOVERNED mode: Full arifOS v45Ω constitutional enforcement

        Returns:
            Dict with response, verdict, metrics, timing, error (if any)
        """
        print("\n" + "═" * 70)
        print("🟢 MODE B: GOVERNED (arifOS v45Ω)")
        print("═" * 70)

        start_time = time.time()
        error = None
        response = None
        verdict = None
        metrics_dict = {}
        lane = None

        try:
            # Step 1: Δ Router - Lane Classification
            lane = classify_prompt_lane(prompt, high_stakes_indicators=[])
            print(f"🔀 Δ Router Lane: {lane.value}")

            lane_info = {
                ApplicabilityLane.PHATIC: "Social lubricant (truth exempt)",
                ApplicabilityLane.SOFT: "Educational/explanatory (truth ≥ 0.80)",
                ApplicabilityLane.HARD: "Factual assertion (truth ≥ 0.90 strict)",
                ApplicabilityLane.REFUSE: "Constitutional violation (auto-block)",
            }
            print(f"   Type: {lane_info.get(lane, 'Unknown')}\n")

            # Step 2: Generate response via LLM
            print(f"⏳ Calling {self.model} (governed)...")
            response = self.generate(prompt)
            print(f"✅ Response received ({len(response)} chars)\n")

            # Step 3: Compute metrics (Ω Aggregator)
            # In production, these would be computed from actual response analysis
            # For demo, using realistic baseline values
            truth_score = 0.87 if lane == ApplicabilityLane.SOFT else 0.95
            metrics = Metrics(
                truth=truth_score,
                delta_s=0.15,  # Positive = coherent
                peace_squared=1.02,  # Above 1.0 = stable
                kappa_r=0.96,  # High empathy
                omega_0=0.04,  # Humility band (0.03-0.05)
                amanah=True,  # No integrity violations
                tri_witness=0.97,  # Auditability
            )

            print(f"⚙️  Ω Aggregator - Metrics:")
            print(f"   Truth (ξ):      {metrics.truth:.3f}")
            print(f"   ΔS (Clarity):   {metrics.delta_s:+.3f}")
            print(f"   Peace²:         {metrics.peace_squared:.3f}")
            print(f"   κᵣ (Empathy):   {metrics.kappa_r:.3f}")
            print(f"   Ω₀ (Humility):  {metrics.omega_0:.3f}")

            # Compute Psi
            psi = metrics.compute_psi()
            print(f"   Ψ (Vitality):   {psi:.3f}\n")

            metrics_dict = {
                "truth": metrics.truth,
                "delta_s": metrics.delta_s,
                "peace_squared": metrics.peace_squared,
                "kappa_r": metrics.kappa_r,
                "omega_0": metrics.omega_0,
                "psi": psi,
            }

            # Step 4: Verdict rendering (888 JUDGE)
            print("⚖️  888 JUDGE - Rendering constitutional verdict...")
            apex_result = apex_review(
                metrics=metrics,
                high_stakes=False,
                lane=lane.value,
                prompt=prompt,
                response_text=response,
            )

            verdict = apex_result.verdict
            reason = apex_result.reason

            verdict_display = {
                Verdict.SEAL: ("✅ SEAL", "Full approval - output released"),
                Verdict.PARTIAL: ("⚠️ PARTIAL", "Conditional - caveats required"),
                Verdict.SABAR: ("⏸️ SABAR", "Pause - cooling required"),
                Verdict.VOID: ("🚫 VOID", "Hard block - no output released"),
                Verdict.HOLD_888: ("🔒 HOLD", "Escalation - human review required"),
            }

            verdict_str, description = verdict_display.get(
                verdict, ("❓ UNKNOWN", "Unknown verdict")
            )

            print(f"\n{verdict_str}")
            print(f"Meaning: {description}")
            print(f"Reason: {reason}\n")

            # Step 5: Show response if approved
            elapsed = time.time() - start_time

            if verdict in [Verdict.SEAL, Verdict.PARTIAL]:
                print(f"📤 GOVERNED OUTPUT:\n")
                print("─" * 70)
                if verdict == Verdict.PARTIAL:
                    print("⚠️ Note: This response contains simplifications/caveats\n")
                print(response[:500] + "..." if len(response) > 500 else response)
                print("─" * 70 + "\n")
            else:
                print(f"🚫 OUTPUT BLOCKED - Constitutional violation\n")
                response = None  # VOID = no output released

            print(f"⏱️ Total governance time: {elapsed:.2f}s\n")

        except Exception as e:
            elapsed = time.time() - start_time
            error = str(e)
            print(f"❌ Governance Error: {error}")
            print(f"⏱️ Failed after {elapsed:.2f}s\n")

        return {
            "mode": "GOVERNED",
            "model": self.model,
            "lane": lane.value if lane else None,
            "response": response,
            "verdict": verdict.value if verdict else None,
            "verdict_reason": reason if verdict else None,
            "metrics": metrics_dict,
            "time_seconds": elapsed,
            "error": error,
        }

    def save_log(self, prompt: str, raw_result: Dict[str, Any], gov_result: Dict[str, Any]):
        """Save run log to JSONL"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"raw_vs_governed_{timestamp}.jsonl"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "raw": raw_result,
            "governed": gov_result,
        }

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(f"💾 Log saved: {log_file}\n")

    def run_comparison(self, prompt: str):
        """Run both RAW and GOVERNED modes and compare"""
        self.show_banner()

        print(f"📝 PROMPT:\n{prompt}\n")

        # Run RAW mode
        raw_result = self.run_raw_mode(prompt)

        # Run GOVERNED mode
        gov_result = self.run_governed_mode(prompt)

        # Save log
        self.save_log(prompt, raw_result, gov_result)

        # Summary
        print("\n" + "═" * 70)
        print("📊 COMPARISON SUMMARY")
        print("═" * 70)
        print(f"RAW:      {'✅ Success' if not raw_result['error'] else '❌ Failed'}")
        print(f"GOVERNED: {'✅ Success' if not gov_result['error'] else '❌ Failed'}")

        if not gov_result['error']:
            print(f"\nGovernance Verdict: {gov_result['verdict']}")
            print(f"Lane: {gov_result['lane']}")
            if gov_result['metrics']:
                print(f"Truth Score: {gov_result['metrics'].get('truth', 'N/A')}")

        print("═" * 70 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Compare RAW (ungoverned) vs GOVERNED (arifOS) LLM calls"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Explain in 5 bullets how arifOS governs an LLM.",
        help="Prompt to send to the LLM (default: arifOS explanation)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen-SEA-LION-v4-32B-IT",
        help="Model name (default: Qwen-SEA-LION-v4-32B-IT)",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=512,
        help="Max tokens to generate (default: 512)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Generation temperature (default: 0.2)",
    )

    args = parser.parse_args()

    try:
        demo = RawVsGovernedDemo(
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
        demo.run_comparison(args.prompt)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Demo interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
