"""
exceptions.py — Kernel exceptions.

These are the ONLY exceptions an arifOS-wrapped agent can raise for
governance reasons. They map directly to Decision verdicts.
"""

from __future__ import annotations

from arifos.decision import Decision


class ArifGovernanceError(Exception):
    """Base class for all arifOS governance exceptions."""

    def __init__(self, message: str, decision: Decision):
        super().__init__(message)
        self.decision = decision


class ArifHold(ArifGovernanceError):
    """888 HOLD — agent must pause for human authority (F13 SOVEREIGN)."""

    def __init__(self, decision: Decision):
        super().__init__(
            f"888 HOLD: {decision.verdict} — "
            f"{decision.reasons[0] if decision.reasons else 'no reason given'}",
            decision,
        )


class ArifDenied(ArifGovernanceError):
    """DENY — floor failure. Hard stop. Not recoverable."""

    def __init__(self, decision: Decision):
        super().__init__(
            f"DENY: {decision.reasons[0] if decision.reasons else 'no reason given'}",
            decision,
        )


class ArifSealMissing(ArifGovernanceError):
    """F11: result has no seal_pointer — cannot trust unsealed output."""

    def __init__(self, decision: Decision):
        super().__init__(
            "F11: result has no seal_pointer — cannot trust unsealed output",
            decision,
        )
