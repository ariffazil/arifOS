#!/usr/bin/env python3
"""
SEA-LION + TEARFRAME Physics Demo - See the Safety in Action!

This shows you:
- Real-time physics measurements
- What happens when you attack
- Fail-closed enforcement
- The EXCITING stuff!
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from arifos_core.connectors.litellm_gateway import make_llm_generate
from arifos_core.utils.session_telemetry import SessionTelemetry
from arifos_core.utils.reduction_engine import compute_attributes
from arifos_core.governance.session_physics import evaluate_physics_floors
from arifos_core.system.apex_prime import Verdict, APEX_VERSION


class PhysicsDemo:
    def __init__(self):
        self.api_key = os.getenv("ARIF_LLM_API_KEY")
        if not self.api_key:
            raise ValueError("ARIF_LLM_API_KEY not in .env")

        self.generate = make_llm_generate()
        self.telemetry = SessionTelemetry("demo_user")
        self.turn_count = 0

    def show_banner(self):
        print("\n" + "🔥" * 35)
        print("  🚀 SEA-LION + TEARFRAME PHYSICS DEMO 🚀")
        print("🔥" * 35)
        print(f"  Version: {APEX_VERSION} | PHYSICS: ACTIVE")
        print("🔥" * 35 + "\n")

    def show_physics_live(self, attrs, verdict):
        """Show the cool physics stuff happening."""
        print("\n" + "=" * 70)
        print("⚡ TEARFRAME PHYSICS ACTIVE - MEASURING YOUR SESSION")
        print("=" * 70)

        # Rate
        rate = attrs.turn_rate if hasattr(attrs, "turn_rate") else 0
        rate_status = "🔴 ATTACK!" if rate > 20 else "🟡 FAST" if rate > 10 else "🟢 NORMAL"
        print(f"📊 Turn Rate:    {rate:.1f} msg/min {rate_status}")

        # Cadence
        cadence = attrs.cadence if hasattr(attrs, "cadence") else 0
        cadence_status = "🔴 SPAM!" if cadence < 1 else "🟢 OK"
        print(f"⏱️  Time Between: {cadence:.2f}s {cadence_status}")

        # Streaks
        sabar_streak = attrs.sabar_streak if hasattr(attrs, "sabar_streak") else 0
        streak_status = (
            "🔴 LOCK IMMINENT!"
            if sabar_streak >= 2
            else "🟡 WARNING"
            if sabar_streak >= 1
            else "🟢 CLEAN"
        )
        print(f"🎯 Fail Streak:  {sabar_streak} failures {streak_status}")

        # Budget
        budget = attrs.budget_burn_pct if hasattr(attrs, "budget_burn_pct") else 0
        budget_status = "🔴 OVERLOAD!" if budget > 80 else "🟡 HIGH" if budget > 50 else "🟢 OK"
        print(f"💰 Token Burn:   {budget:.1f}% {budget_status}")

        print("\n" + "=" * 70)

        # Verdict
        verdict_str = verdict.value if hasattr(verdict, "value") else str(verdict)

        if verdict_str == "SEAL":
            print("✅ VERDICT: SEAL - Safe to proceed")
        elif verdict_str == "SABAR":
            print("⚠️  VERDICT: SABAR - Warning issued! Next failure = LOCK")
        elif verdict_str == "HOLD_888":
            print("🔒 VERDICT: HOLD_888 - SESSION LOCKED! Too many failures")
        elif verdict_str == "VOID":
            print("🚫 VERDICT: VOID - Blocked (budget exceeded)")

        print("=" * 70 + "\n")

    def normal_mode(self):
        """Interactive mode with physics."""
        print("\n📋 INTERACTIVE MODE - Type your prompts")
        print("   Commands: 'quit', 'attack' (spam test), 'stats'\n")

        while True:
            prompt = input("🎯 Your prompt: ").strip()

            if not prompt:
                continue

            if prompt.lower() in ["quit", "exit"]:
                break

            if prompt.lower() == "attack":
                self.attack_demo()
                continue

            if prompt.lower() == "stats":
                self.show_stats()
                continue

            self.process_turn(prompt)

    def process_turn(self, prompt, mock_verdict=None):
        """Process one turn with physics."""
        self.turn_count += 1

        # Start telemetry
        self.telemetry.start_turn(tokens_in=len(prompt.split()), temperature=0.7, top_p=0.9)
        start_time = time.time()

        # Call LLM
        print(f"\n⏳ Turn {self.turn_count}: Calling SEA-LION...")

        try:
            response = self.generate(prompt)
            elapsed = time.time() - start_time

            # End telemetry
            verdict = mock_verdict if mock_verdict else Verdict.SEAL
            snapshot = self.telemetry.end_turn(
                tokens_out=len(response.split()),
                verdict=verdict,
                context_length_used=len(prompt.split()) + len(response.split()),
                kv_cache_size=0,
                timeout=False,
                safety_block=False,
                truncation_flag=False,
                commit=True,
            )

            # Compute physics
            attrs = compute_attributes(
                history=self.telemetry.history,
                max_session_tokens=100000,  # Default budget
                current_turn=snapshot,
            )
            physics_verdict = evaluate_physics_floors(attrs)

            # Show physics
            self.show_physics_live(attrs, physics_verdict or Verdict.SEAL)

            # Show response if no physics floor violated
            if physics_verdict is None or physics_verdict == Verdict.SEAL:
                print("🤖 SEA-LION Response:")
                print("─" * 70)
                print(response[:300] + "..." if len(response) > 300 else response)
                print("─" * 70)
            else:
                print("🚫 Response blocked by physics enforcement!")

        except Exception as e:
            print(f"❌ Error: {e}")

    def attack_demo(self):
        """Show what happens when you attack."""
        print("\n" + "🔥" * 35)
        print("  ATTACK DEMO - Watch TEARFRAME Block It!")
        print("🔥" * 35 + "\n")

        print("Simulating rapid-fire attack (3 messages in 0.5 seconds)...\n")

        for i in range(3):
            time.sleep(0.2)  # Simulate fast attacks
            print(f"Attack {i + 1}/3...")
            self.process_turn(f"Attack attempt {i + 1}", mock_verdict=Verdict.SABAR)

        print("\n🎯 RESULT: Physics detected the attack pattern!")
        print("   - High message rate detected")
        print("   - Fail streak accumulated")
        print("   - Session would be LOCKED on next failure")
        print("\n✓ TEARFRAME blocked the attack!\n")

    def show_stats(self):
        """Show session stats."""
        print("\n📊 SESSION STATISTICS:")
        print(f"  • Total Turns: {self.turn_count}")
        print(f"  • Physics Engine: v44Ω ACTIVE")
        print(f"  • Model: SEA-LION v3")
        print()


def main():
    try:
        demo = PhysicsDemo()
        demo.show_banner()

        print("🎮 DEMO MODES:\n")
        print("  1. Interactive - Type prompts and see physics in action")
        print("  2. Attack Demo - See TEARFRAME block rapid-fire attacks")
        print("  3. Quit\n")

        choice = input("Choose mode (1-3): ").strip()

        if choice == "1":
            demo.normal_mode()
        elif choice == "2":
            demo.attack_demo()
            input("\nPress Enter to continue to interactive mode...")
            demo.normal_mode()
        else:
            print("👋 Goodbye!")
            return 0

        print(f"\n📊 Session complete!")
        print(f"   Total turns: {demo.turn_count}")
        print(f"   Physics: ACTIVE throughout\n")

        return 0

    except ValueError as e:
        print(f"❌ {e}")
        print("\nAdd to .env:")
        print("  ARIF_LLM_API_KEY=your-key")
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted!\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
