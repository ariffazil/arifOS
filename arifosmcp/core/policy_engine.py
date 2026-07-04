"""
arifOS Sovereign Fabric — Policy Engine (Wajib Layer 11)
═════════════════════════════════════════════════════════

Constitutional law becomes executable.
Every AuthorizationEnvelope passes through this engine.
The engine returns a PolicyVerdict — PROCEED, HOLD, SABAR, or VOID.

This is the membrane between "agent wants to act" and "agent may act."

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from arifosmcp.core.authorization_envelope import (
    ActionClass,
    AuthorizationEnvelope,
    BlastRadius,
    EvidenceFloor,
    Reversibility,
    Verdict,
)

logger = logging.getLogger(__name__)


# ── Policy Verdict ─────────────────────────────────────────────────────


@dataclass
class PolicyVerdict:
    """The result of running an envelope through the policy engine."""

    verdict: Verdict
    reason: str
    violated_floors: list[str] = field(default_factory=list)
    required_next_step: Optional[str] = None
    receipt_required: bool = False
    vault_seal_required: bool = False
    trace_id: str = ""
    span_id: str = ""
    evaluation_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "violated_floors": self.violated_floors,
            "required_next_step": self.required_next_step,
            "receipt_required": self.receipt_required,
            "vault_seal_required": self.vault_seal_required,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "evaluation_time_ms": self.evaluation_time_ms,
        }


# ── Floor Rules ────────────────────────────────────────────────────────
# Each floor maps to one or more executable rules.
# Rules return (passed: bool, reason: str).


def _f1_amanah(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F1: Reversible-first. Irreversible requires human ack."""
    if env.reversibility == Reversibility.NONE:
        if not env.requires_human_ack:
            return False, "F1 AMANAH: Irreversible action requires human acknowledgment (F13)"
        if not env.human_ack_token:
            return False, "F1 AMANAH: Irreversible action requires valid human ack token"
    return True, "F1 AMANAH: OK"


def _f2_truth(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F2: Confidence must be grounded. No fabrication."""
    if env.confidence > 0.90:
        return False, f"F2 TRUTH: Confidence {env.confidence} exceeds F7 cap (0.90)"
    if env.action_class in (ActionClass.EXECUTE, ActionClass.SEAL):
        if env.evidence_floor == EvidenceFloor.NONE:
            return False, "F2 TRUTH: Execute/Seal requires evidence_floor > NONE"
    return True, "F2 TRUTH: OK"


def _f4_clarity(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F4: Every action must have an intent description."""
    if env.action_class in (ActionClass.MUTATE, ActionClass.EXECUTE, ActionClass.SEAL):
        if not env.intent_description:
            return False, "F4 CLARITY: Mutate/Execute/Seal requires intent_description"
    return True, "F4 CLARITY: OK"


def _f7_humility(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F7: Confidence capped at 0.90."""
    if env.confidence > 0.90:
        return False, f"F7 HUMILITY: Confidence {env.confidence} exceeds 0.90 cap"
    return True, "F7 HUMILITY: OK"


def _f8_law(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F8: Execution requires lease."""
    if env.action_class in (ActionClass.EXECUTE, ActionClass.MUTATE):
        if not env.lease_id:
            return False, "F8 LAW: Execute/Mutate requires lease_id"
    return True, "F8 LAW: OK"


def _f11_auth(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F11: Actor must be identified."""
    if not env.actor_id:
        return False, "F11 AUTH: actor_id is required"
    if env.action_class in (ActionClass.EXECUTE, ActionClass.SEAL):
        if not env.session_id:
            return False, "F11 AUTH: Execute/Seal requires valid session_id"
    return True, "F11 AUTH: OK"


def _f13_sovereign(env: AuthorizationEnvelope) -> tuple[bool, str]:
    """F13: Irreversible actions require sovereign approval."""
    if env.reversibility == Reversibility.NONE:
        if env.blast_radius in (
            BlastRadius.FEDERATION,
            BlastRadius.EXTERNAL,
            BlastRadius.IRREVERSIBLE,
        ):
            if not env.human_ack_token:
                return False, "F13 SOVEREIGN: High-blast irreversible requires sovereign ack"
    return True, "F13 SOVEREIGN: OK"


# ── Rule Registry ──────────────────────────────────────────────────────

FLOOR_RULES = [
    ("F1_AMANAH", _f1_amanah),
    ("F2_TRUTH", _f2_truth),
    ("F4_CLARITY", _f4_clarity),
    ("F7_HUMILITY", _f7_humility),
    ("F8_LAW", _f8_law),
    ("F11_AUTH", _f11_auth),
    ("F13_SOVEREIGN", _f13_sovereign),
]


# ── Policy Engine ──────────────────────────────────────────────────────


class PolicyEngine:
    """
    Evaluates an AuthorizationEnvelope against constitutional floor rules.

    Usage:
        engine = PolicyEngine()
        verdict = engine.evaluate(envelope)
        if verdict.verdict == Verdict.PROCEED:
            # execute
        elif verdict.verdict == Verdict.HOLD:
            # wait for additional evidence/approval
        elif verdict.verdict == Verdict.VOID:
            # reject — constitutionally forbidden
    """

    def evaluate(self, env: AuthorizationEnvelope) -> PolicyVerdict:
        """Run all floor rules against the envelope."""
        start = time.time()
        violated = []
        reasons = []

        for floor_name, rule_fn in FLOOR_RULES:
            passed, reason = rule_fn(env)
            if not passed:
                violated.append(floor_name)
                reasons.append(reason)
                logger.warning(f"Floor violation: {reason}")

        elapsed_ms = (time.time() - start) * 1000

        # Determine verdict
        if not violated:
            verdict = Verdict.PROCEED
            reason = "All constitutional floors passed"
        elif any("F13" in v or "F1" in v for v in violated):
            # Irreversible without ack → VOID
            verdict = Verdict.VOID
            reason = "; ".join(reasons)
        elif any("F8" in v for v in violated):
            # Missing lease → HOLD (can be fixed)
            verdict = Verdict.HOLD
            reason = "; ".join(reasons)
        else:
            # Other violations → HOLD (can be fixed with evidence/approval)
            verdict = Verdict.HOLD
            reason = "; ".join(reasons)

        # Determine if receipt/seal needed
        receipt_required = env.action_class in (
            ActionClass.MUTATE,
            ActionClass.EXECUTE,
            ActionClass.SEAL,
            ActionClass.DELEGATE,
        )
        vault_seal_required = (
            env.reversibility == Reversibility.NONE and env.action_class == ActionClass.SEAL
        )

        # Determine next step
        next_step = None
        if verdict == Verdict.HOLD:
            if "F8" in str(violated):
                next_step = "Request lease via forge_lease_request"
            elif "F2" in str(violated):
                next_step = "Gather additional evidence via arif_observe"
            elif "F1" in str(violated):
                next_step = "Request human acknowledgment (F13)"
            else:
                next_step = "Review violations and retry"
        elif verdict == Verdict.VOID:
            next_step = "Action is constitutionally forbidden — do not proceed"

        return PolicyVerdict(
            verdict=verdict,
            reason=reason,
            violated_floors=violated,
            required_next_step=next_step,
            receipt_required=receipt_required,
            vault_seal_required=vault_seal_required,
            trace_id=env.trace_id,
            span_id=env.span_id,
            evaluation_time_ms=elapsed_ms,
        )

    def quick_check(self, env: AuthorizationEnvelope) -> Verdict:
        """Fast path — returns only the verdict enum."""
        return self.evaluate(env).verdict

    def is_allowed(self, env: AuthorizationEnvelope) -> bool:
        """Boolean check — is this action constitutionally allowed?"""
        return self.quick_check(env) == Verdict.PROCEED


# ── Singleton ──────────────────────────────────────────────────────────

_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get or create the singleton policy engine."""
    global _engine
    if _engine is None:
        _engine = PolicyEngine()
    return _engine
