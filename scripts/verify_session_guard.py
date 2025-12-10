#!/usr/bin/env python3
"""
arifOS Lab: Session Dependency Guard Verification

Simulates a "binge session" to verify the time-based governor.

This script does NOT call the real pipeline. It only exercises
DependencyGuard in isolation to show how SABAR and WARN could fire
over a sequence of interactions.

Usage:
    python scripts/verify_session_guard.py
"""

from __future__ import annotations

import time
from typing import NoReturn

from arifos_core.guards.session_dependency import DependencyGuard


def simulate_binge() -> None:
    """Simulate a short, dense session to demonstrate guard behavior."""
    print("[LAB] Session Dependency Guard Simulation")
    print("=" * 60)

    # Strict limits for demonstration:
    # - max_duration_min: 0.05 minutes (~3 seconds)
    # - max_interactions: 3 turns before WARN
    guard = DependencyGuard(max_duration_min=0.05, max_interactions=3)
    session_id = "test_subject_alpha"

    print(f"Limits: duration <= {guard.max_duration_min:.3f} minutes,"
          f" interactions <= {guard.max_interactions}")
    print("-" * 60)

    # Simulate 5 interactions
    for turn in range(1, 6):
        print(f"\n[Turn {turn}] User: 'Hello, I am still talking.'")

        risk = guard.check_risk(session_id)
        state = guard.sessions[session_id]

        seconds = state.duration_minutes * 60.0
        print(f"   Time elapsed: {seconds:.2f} seconds")
        print(f"   Interaction count: {state.interaction_count}")
        print(f"   Guard verdict: [{risk['status']}] ({risk['risk_level']})")

        if risk["status"] == "SABAR":
            print(f"   SYSTEM HALT: {risk['message']}")
            break
        elif risk["status"] == "WARN":
            print(f"   SYSTEM NOTE: {risk['message']}")
            print("   AI: 'Here is your answer...'")
        else:
            print("   AI: 'Here is your answer...'")

        # Fast-forward time for the simulation
        time.sleep(1.0)

    print("\n" + "-" * 60)
    print("[LAB] Simulation complete.")


def main() -> NoReturn:
    simulate_binge()
    raise SystemExit(0)


if __name__ == "__main__":
    main()

