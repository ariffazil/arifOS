"""
Simple Demo: arifOS Physics Code in Action

Shows how arifOS governance works without needing full pipeline setup.
Just the SABAR-72 timer and basic concepts.
"""

from arifos_core.enforcement.sabar_timer import Sabar72Timer, SabarReason
from datetime import datetime


def demo_sabar_timer():
    """Demo SABAR-72 Time Governor"""

    print("=" * 70)
    print("🔒 ARIFOS SABAR-72 TIME GOVERNOR DEMO")
    print("=" * 70)
    print()

    # Create timer
    timer = Sabar72Timer()

    # Scenario: AI makes an error, SABAR-72 kicks in
    print("📌 SCENARIO: @EYE detects circuit breaker event")
    print("-" * 70)

    job_id = "chatgpt_001"
    user_query = "Deploy this critical security patch"

    # Issue SABAR-72 ticket
    ticket = timer.issue_ticket(
        reason=SabarReason.EYE_CIRCUIT_OPEN,
        job_id=job_id,
        query=user_query,
        floor_failures=["F7_OMEGA_ZERO: Confidence collapse detected"],
    )

    print(f"✅ SABAR-72 Ticket Issued:")
    print(f"   Ticket ID: {ticket.ticket_id[:16]}...")
    print(f"   Reason: {ticket.reason.value}")
    print(f"   Issued: {ticket.issued_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Expires: {ticket.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Cooling Period: {ticket.hours_remaining():.1f} hours remaining")
    print()

    # Check if blocked
    print("🚫 ATTEMPTING TO SEAL OUTPUT...")
    print("-" * 70)

    if timer.is_blocked(job_id):
        ticket_active = timer.get_ticket(job_id)
        print(f"❌ SEAL BLOCKED!")
        print(f"   Reason: SABAR-72 enforced")
        print(f"   Time remaining: {ticket_active.hours_remaining():.1f} hours")
        print(f"   Floor failures: {ticket_active.floor_failures}")
        print()
        print("   💡 This is PHYSICS CODE enforcement:")
        print("      - No prompt can bypass this")
        print("      - No documentation reading required")
        print("      - The timer RUNS regardless of AI's 'understanding'")
        print()

    # Show what human override looks like
    print("🔓 HUMAN AUTHORITY OVERRIDE")
    print("-" * 70)
    print("   To override, human must provide digital signature:")
    print("   Example: timer.override_ticket(job_id, 'human_sig_xyz123')")
    print()

    # Cleanup demo
    print("🧹 CLEANUP")
    print("-" * 70)
    removed = timer.cleanup_expired()
    print(f"   Note: In real usage, expired tickets auto-remove")
    print(f"   This demo created 1 active ticket")
    print()

    print("=" * 70)
    print("✅ KEY TAKEAWAYS")
    print("=" * 70)
    print("1. SABAR-72 is CODE PHYSICS, not a suggestion")
    print("2. Timer blocks SEAL for 72 hours automatically")
    print("3. Works WITHOUT reading AGENTS.md or canon")
    print("4. AI can't bypass - it's a Python state machine")
    print("5. Only human authority can override (with signature)")
    print()
    print("🔥 THIS IS WHY 'pip install arifos' MAKES AI BETTER:")
    print("   - Governance is STRUCTURAL (code)")
    print("   - Not CULTURAL (prompts/docs)")
    print("   - Physics enforces what philosophy explains")
    print()
    print("Ditempa, bukan diberi. 🔨")
    print()


if __name__ == "__main__":
    demo_sabar_timer()
