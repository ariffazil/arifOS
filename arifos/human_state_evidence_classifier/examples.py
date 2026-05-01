"""Example invocations of the Human-State Evidence Classifier.

These demonstrate correct and incorrect usage.
Run: python -m arifos.human_state_evidence_classifier.examples
"""

from .labels import StateDomain
from .witness_fusion import estimate_human_state


# ── Example 1: Audit-style text, no telemetry, no confirmation ──────────────
audit_text = """
Good audit. Ground the facts and claims.
The two WELL states are mutually exclusive.
Do not treat tool-reported telemetry as biological fact.
Cannot have both — verify the contradiction.
"""


def run_examples():
    print("=" * 70)
    print("HUMAN-STATE EVIDENCE CLASSIFIER — Example Runs")
    print("=" * 70)

    for domain in StateDomain:
        estimate = estimate_human_state(
            text=audit_text,
            domain=domain,
            well_telemetry=None,
            user_confirmed=None,
        )

        print(f"\n{'─' * 70}")
        print(f"  DOMAIN: {domain.value.upper()}")
        print(f"  Status:     {estimate.status.value}")
        print(f"  Confidence: {estimate.confidence.value}")
        print(f"  Signals:    {estimate.textual_signals}")
        print(f"  Bio:        {estimate.biological_signals}")
        print(f"  Confirm?:   {'YES' if estimate.human_confirmation_required else 'NO'}")
        print(f"\n  SAFE: {estimate.safe_statement}")
        if estimate.forbidden_claims:
            print(f"  FORBIDDEN: {estimate.forbidden_claims[:2]}")

    # ── Example 2: Body with dirty telemetry ────────────────────────────────
    print(f"\n{'─' * 70}")
    print("  DOMAIN: body + VOID telemetry")
    result = estimate_human_state(
        text="I feel tired today.",
        domain=StateDomain.BODY,
        well_telemetry={"truth_status": "VOID", "operator_confirmed": False},
    )
    print(f"  Status:     {result.status.value}")
    print(f"  Confidence: {result.confidence.value}")
    print(f"  SAFE: {result.safe_statement}")

    # ── Example 3: User confirmation overrides ────────────────────────────
    print(f"\n{'─' * 70}")
    print("  DOMAIN: amanah + user_confirmed=True")
    result = estimate_human_state(
        text="Truth preservation is critical in this context.",
        domain=StateDomain.AMANAH,
        user_confirmed=True,
    )
    print(f"  Status:     {result.status.value}")
    print(f"  Confidence: {result.confidence.value}")
    print(f"  SAFE: {result.safe_statement}")

    # ── Example 4: User contradiction overrides ───────────────────────────
    print(f"\n{'─' * 70}")
    print("  DOMAIN: akal + user_confirmed=False")
    result = estimate_human_state(
        text="The contradiction is clear — verify before proceeding.",
        domain=StateDomain.AKAL,
        user_confirmed=False,
    )
    print(f"  Status:     {result.status.value}")
    print(f"  Confidence: {result.confidence.value}")
    print(f"  SAFE: {result.safe_statement}")

    print(f"\n{'=' * 70}")
    print("All examples complete.")


if __name__ == "__main__":
    run_examples()
