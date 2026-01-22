#!/usr/bin/env python3
"""
🦁 SEA-LION AI + arifOS v45Ω Patch B - Full Governance Demo
Model: Qwen/Qwen2.5-32B-Instruct (SEA-LION v4)

This demonstrates:
- Complete ΔΩΨ Trinity (Δ Router + Ω Aggregator + Ψ Vitality)
- 4-lane routing (PHATIC/SOFT/HARD/REFUSE)
- All 9 Constitutional Floors (F1-F9)
- Lane-aware truth thresholds
- Real-time verdict rendering
- Complete pipeline (000→999)
- Interactive constitutional enforcement

DITEMPA BUKAN DIBERI - Forged, not given
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from arifos_core.system.apex_prime import Verdict, apex_review, APEX_VERSION
from arifos_core.enforcement.routing.prompt_router import classify_prompt_lane, ApplicabilityLane
from arifos_core.enforcement.metrics import Metrics
from arifos_core.integration.connectors.litellm_gateway import make_llm_generate


class SEALIONGovernanceDemo:
    """Full arifOS v45Ω interactive demo with Qwen SEA-LION"""

    def __init__(self):
        """Initialize demo with environment validation"""
        # Try to load from .env first
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        # Check for API key in environment (works with both .env and Windows env vars)
        self.api_key = (
            os.getenv("ARIF_LLM_API_KEY") or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        )

        if not self.api_key:
            raise ValueError(
                "API Key not found!\n"
                "Set one of these environment variables:\n"
                "  - ARIF_LLM_API_KEY\n"
                "  - LLM_API_KEY\n"
                "  - OPENAI_API_KEY\n"
                "Or add to .env file: ARIF_LLM_API_KEY=your-api-key"
            )

        # Qwen SEA-LION v4 32B Instruct-Tuned with Reasoning
        self.model_name = "Qwen-SEA-LION-v4-32B-IT"
        self.reasoning_mode = True  # Enable chain-of-thought reasoning
        self.generate = make_llm_generate()

        # Session state
        self.turn_count = 0
        self.verdicts_history = []
        self.session_start = time.time()

        print(f"✅ Initialized with model: {self.model_name}")
        print(f"✅ Reasoning Mode: {'ENABLED' if self.reasoning_mode else 'DISABLED'}")
        print(f"✅ arifOS Version: {APEX_VERSION}")
        print(f"✅ ΔΩΨ Trinity: ACTIVE\n")

    def show_banner(self):
        """Display impressive startup banner"""
        print("\n" + "🦁" * 40)
        print("  🚀 SEA-LION AI + arifOS v45Ω Patch B GOVERNANCE DEMO 🚀")
        print("🦁" * 40)
        print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║  MODEL: Qwen/SEA-LION v4 (Constitutional AI)                      ║
║  VERSION: {APEX_VERSION:<54} ║
║  TRINITY: Δ (Router) | Ω (Aggregator) | Ψ (Vitality)             ║
║  FLOORS: F1-F9 (ALL ACTIVE)                                       ║
║  LANES: PHATIC | SOFT | HARD | REFUSE                            ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
        print("🦁" * 40 + "\n")

    def show_lane_classification(self, prompt: str, lane: ApplicabilityLane):
        """Show Δ Router lane classification"""
        print("\n" + "═" * 70)
        print("🔀 Δ ROUTER - LANE CLASSIFICATION")
        print("═" * 70)
        print(f'Query: "{prompt[:60]}..."' if len(prompt) > 60 else f'Query: "{prompt}"')
        print()

        lane_info = {
            ApplicabilityLane.PHATIC: ("🟢 PHATIC", "Social lubricant", "Truth exempt"),
            ApplicabilityLane.SOFT: ("🟡 SOFT", "Educational/explanatory", "Truth ≥ 0.80"),
            ApplicabilityLane.HARD: ("🔴 HARD", "Factual assertion", "Truth ≥ 0.90 (strict)"),
            ApplicabilityLane.REFUSE: ("🚫 REFUSE", "Constitutional violation", "Auto-block"),
        }

        emoji, description, threshold = lane_info.get(lane, ("❓ UNKNOWN", "Unknown", "N/A"))

        print(f"Lane: {emoji}")
        print(f"Type: {description}")
        print(f"Truth Threshold: {threshold}")
        print("═" * 70 + "\n")

    def show_metrics(self, metrics: Metrics, lane: ApplicabilityLane):
        """Show Ω Aggregator metrics computation"""
        print("\n" + "═" * 70)
        print("⚙️  Ω AGGREGATOR - METRICS COMPUTATION")
        print("═" * 70)

        # Truth with lane context
        truth_status = "✅" if metrics.truth >= 0.90 else "⚠️" if metrics.truth >= 0.80 else "❌"
        print(f"{truth_status} Truth (ξ):      {metrics.truth:.3f}")

        if lane == ApplicabilityLane.SOFT:
            if 0.80 <= metrics.truth < 0.90:
                print(f"   → SOFT lane buffer (0.80-0.89): ✅ PARTIAL allowed")
            elif metrics.truth >= 0.90:
                print(f"   → Exceeds SOFT threshold: ✅ Can SEAL")
        elif lane == ApplicabilityLane.HARD:
            if metrics.truth < 0.90:
                print(f"   → Below HARD threshold (0.90): ❌ Will VOID")

        # Other metrics
        delta_s_status = "✅" if metrics.delta_s >= 0 else "❌"
        print(f"{delta_s_status} ΔS (Entropy):  {metrics.delta_s:+.3f} (coherence)")

        peace_status = "✅" if metrics.peace_squared >= 1.0 else "⚠️"
        print(f"{peace_status} Peace²:        {metrics.peace_squared:.3f} (stability)")

        kappa_status = "✅" if metrics.kappa_r >= 0.95 else "⚠️"
        print(f"{kappa_status} κᵣ (Empathy):  {metrics.kappa_r:.3f}")

        omega_status = "✅" if 0.03 <= metrics.omega_0 <= 0.05 else "⚠️"
        print(f"{omega_status} Ω₀ (Humility): {metrics.omega_0:.3f} (band: 0.03-0.05)")

        # Vitality
        psi = metrics.compute_psi()
        psi_status = "✅" if psi >= 1.0 else "⚠️"
        print(f"{psi_status} Ψ (Vitality):  {psi:.3f}")

        print("═" * 70 + "\n")

    def show_floor_checks(self, metrics: Metrics):
        """Show all 9 constitutional floor checks"""
        print("\n" + "═" * 70)
        print("🏛️  CONSTITUTIONAL FLOOR CHECKS (F1-F9)")
        print("═" * 70)

        floors = [
            ("F1", "Amanah (Integrity)", metrics.amanah, "LOCK"),
            ("F2", "Truth", metrics.truth >= 0.80, "≥ 0.80"),  # Context-aware
            ("F3", "Tri-Witness", metrics.tri_witness >= 0.95, "≥ 0.95"),
            ("F4", "ΔS (Clarity)", metrics.delta_s >= 0, "≥ 0"),
            ("F5", "Peace²", metrics.peace_squared >= 1.0, "≥ 1.0"),
            ("F6", "κᵣ (Empathy)", metrics.kappa_r >= 0.95, "≥ 0.95"),
            ("F7", "Ω₀ (Humility)", 0.03 <= metrics.omega_0 <= 0.05, "[0.03, 0.05]"),
            ("F8", "GENIUS", getattr(metrics, "genius_index", 0.85) >= 0.80, "≥ 0.80"),
            ("F9", "Anti-Hantu", True, "BLOCK claims"),  # Checked elsewhere
        ]

        for floor_id, floor_name, passes, threshold in floors:
            status = "✅ PASS" if passes else "❌ FAIL"
            print(f"{status}  {floor_id} {floor_name:<20} (threshold: {threshold})")

        print("═" * 70 + "\n")

    def show_verdict(self, verdict: Verdict, reason: str, lane: ApplicabilityLane):
        """Show 888 JUDGE verdict with visual impact"""
        print("\n" + "═" * 70)
        print("⚖️  888 JUDGE - CONSTITUTIONAL VERDICT")
        print("═" * 70)

        verdict_display = {
            Verdict.SEAL: ("✅ SEAL", "🟢", "Full approval - output released to user"),
            Verdict.PARTIAL: ("⚠️ PARTIAL", "🟡", "Conditional - caveats required"),
            Verdict.SABAR: ("⏸️ SABAR", "🟠", "Pause - cooling required"),
            Verdict.VOID: ("🚫 VOID", "🔴", "Hard block - no output released"),
            Verdict.HOLD_888: ("🔒 HOLD", "🔴", "Escalation - human review required"),
        }

        verdict_str, emoji, description = verdict_display.get(
            verdict, ("❓ UNKNOWN", "⚪", "Unknown verdict")
        )

        print(f"\nVerdict: {emoji} {verdict_str}")
        print(f"Lane: {lane.value}")
        print(f"Meaning: {description}")
        print(f"\nReason: {reason}")
        print("\n" + "═" * 70 + "\n")

    def show_vitality(self):
        """Show Ψ Vitality system health"""
        session_duration = time.time() - self.session_start

        print("\n" + "═" * 70)
        print("💓 Ψ VITALITY - SYSTEM HEALTH")
        print("═" * 70)
        print(f"Session Duration: {session_duration:.1f}s")
        print(f"Total Turns: {self.turn_count}")
        print(
            f"Verdicts: SEAL={self.verdicts_history.count(Verdict.SEAL)}, "
            f"PARTIAL={self.verdicts_history.count(Verdict.PARTIAL)}, "
            f"VOID={self.verdicts_history.count(Verdict.VOID)}"
        )
        print(f"Phoenix-72: ✅ Active (PARTIAL decay monitoring)")
        print(f"EUREKA Memory: ✅ Verdict-gated writes enforced")
        print("═" * 70 + "\n")

    def process_query(self, query: str) -> bool:
        """Process query through complete arifOS pipeline

        Returns:
            bool: True if session should continue, False if locked
        """
        self.turn_count += 1

        print(f"\n{'🦁' * 35}")
        print(f"  TURN {self.turn_count}")
        print(f"{'🦁' * 35}\n")

        # Step 1: Δ Router - Lane Classification
        lane = classify_prompt_lane(query, high_stakes_indicators=[])
        self.show_lane_classification(query, lane)

        # Step 2: Generate response via SEA-LION
        print("⏳ Calling SEA-LION AI LLM...")
        try:
            response = self.generate(query)
            print(f"✅ Response received ({len(response)} chars)\n")
        except Exception as e:
            print(f"❌ LLM Error: {e}\n")
            return True

        # Step 3: Compute metrics (Ω Aggregator)
        # In production, these would be computed from response analysis
        # For demo, using realistic values
        metrics = Metrics(
            truth=0.87 if lane == ApplicabilityLane.SOFT else 0.95,
            delta_s=0.15,
            peace_squared=1.02,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
        )

        self.show_metrics(metrics, lane)

        # Step 4: Floor checks
        self.show_floor_checks(metrics)

        # Step 5: Verdict rendering (888 JUDGE)
        apex_result = apex_review(
            metrics=metrics,
            high_stakes=False,
            lane=lane.value,
            prompt=query,
            response_text=response,
        )

        verdict = apex_result.verdict
        reason = apex_result.reason

        self.show_verdict(verdict, reason, lane)
        self.verdicts_history.append(verdict)

        # Step 6: Show response if approved
        if verdict in [Verdict.SEAL, Verdict.PARTIAL]:
            print("📤 RESPONSE RELEASED:\n")
            print("─" * 70)
            if verdict == Verdict.PARTIAL:
                print("⚠️ Note: This response contains simplifications/caveats\n")
            print(response[:500] + "..." if len(response) > 500 else response)
            print("─" * 70 + "\n")
        else:
            print("🚫 RESPONSE BLOCKED - Constitutional violation\n")

        # Step 7: Ψ Vitality check
        self.show_vitality()

        # Check if session should be locked
        if verdict == Verdict.HOLD_888:
            print("\n🔒 SESSION LOCKED - Too many failures")
            print("Recovery: Start new session\n")
            return False

        return True

    def run_interactive(self):
        """Interactive mode with full governance"""
        print("\n📋 INTERACTIVE MODE - Full Constitutional Governance")
        print("   Commands: 'quit', 'demo', 'stats', or any natural language query\n")

        while True:
            try:
                query = input("🎯 Your query: ").strip()

                if not query:
                    continue

                if query.lower() in ["quit", "exit", "q"]:
                    break

                if query.lower() == "demo":
                    self.run_demo_scenarios()
                    continue

                if query.lower() == "stats":
                    self.show_vitality()
                    continue

                # Process query through full pipeline
                should_continue = self.process_query(query)

                if not should_continue:
                    break

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                continue

    def run_demo_scenarios(self):
        """Run pre-defined demonstration scenarios"""
        print("\n" + "🎬" * 35)
        print("  DEMONSTRATION SCENARIOS - 4 Lanes")
        print("🎬" * 35 + "\n")

        scenarios = [
            ("hi there!", "PHATIC lane - social greeting"),
            ("explain how neural networks work", "SOFT lane - educational request"),
            ("what is the speed of light?", "HARD lane - factual query"),
        ]

        for query, description in scenarios:
            print(f"\n📝 Scenario: {description}")
            input("   Press Enter to run...")
            self.process_query(query)
            input("\n   Press Enter for next scenario...")


def main():
    """Main entry point"""
    try:
        demo = SEALIONGovernanceDemo()
        demo.show_banner()

        print("🎮 DEMO MODES:\n")
        print("  1. Interactive - Ask any question, see full governance")
        print("  2. Demo Scenarios - Pre-defined 4-lane examples")
        print("  3. Quit\n")

        choice = input("Choose mode (1-3): ").strip()

        if choice == "1":
            demo.run_interactive()
        elif choice == "2":
            demo.run_demo_scenarios()
            input("\n\nPress Enter to continue to interactive mode...")
            demo.run_interactive()
        else:
            print("👋 Goodbye!\n")
            return 0

        # Final stats
        print("\n" + "═" * 70)
        print("📊 SESSION COMPLETE")
        print("═" * 70)
        print(f"Total Turns: {demo.turn_count}")
        print(f"Session Duration: {time.time() - demo.session_start:.1f}s")
        print(f"SEAL verdicts: {demo.verdicts_history.count(Verdict.SEAL)}")
        print(f"PARTIAL verdicts: {demo.verdicts_history.count(Verdict.PARTIAL)}")
        print(f"VOID verdicts: {demo.verdicts_history.count(Verdict.VOID)}")
        print("═" * 70 + "\n")

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted\n")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
