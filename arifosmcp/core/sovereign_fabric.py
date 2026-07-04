"""
arifOS Sovereign Fabric — Integration Layer
════════════════════════════════════════════

One import. One function call. Full constitutional governance.

Usage:
    from arifosmcp.core.sovereign_fabric import govern

    verdict = govern(
        actor_id="opencode-333-agi",
        session_id="SEAL-abc123",
        tool_name="arif_observe",
        intent="Search for seismic data in NW Sabah",
    )
    if verdict.proceed:
        # execute the tool
    else:
        # handle HOLD/VOID

This is the single entry point for the wajib layers.
Every MCP tool call should go through this.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from arifosmcp.core.authorization_envelope import (
    ActionClass,
    AuthorizationEnvelope,
    BlastRadius,
    EvidenceFloor,
    Reversibility,
    Verdict,
    classify_action,
    create_envelope,
)
from arifosmcp.core.identity_binding import (
    AuthMethod,
    IdentityBinding,
    register_identity,
    verify_identity,
)
from arifosmcp.core.policy_engine import PolicyEngine, PolicyVerdict, get_policy_engine
from arifosmcp.core.sovereign_bridge import SovereignContext, get_sovereign_context
from arifosmcp.core.trace_context import TraceCollector, TraceContext, get_trace_collector

logger = logging.getLogger(__name__)


# ── Governed Result ────────────────────────────────────────────────────


@dataclass
class GovernedResult:
    """The complete result of running a tool call through the sovereign fabric."""

    proceed: bool
    verdict: Verdict
    reason: str
    violated_floors: list[str]
    envelope: AuthorizationEnvelope
    policy_verdict: PolicyVerdict
    trace: TraceContext
    required_next_step: Optional[str] = None

    @property
    def hold(self) -> bool:
        return self.verdict == Verdict.HOLD

    @property
    def void(self) -> bool:
        return self.verdict == Verdict.VOID

    def to_dict(self) -> dict[str, Any]:
        return {
            "proceed": self.proceed,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "violated_floors": self.violated_floors,
            "required_next_step": self.required_next_step,
            "envelope_id": self.envelope.envelope_id,
            "trace_id": self.trace.trace_id,
            "span_id": self.trace.span_id,
        }


# ── The govern() function ──────────────────────────────────────────────


def govern(
    actor_id: str,
    session_id: str,
    tool_name: str,
    intent: str = "",
    action_class: Optional[ActionClass] = None,
    reversibility: Reversibility = Reversibility.UNKNOWN,
    blast_radius: BlastRadius = BlastRadius.NONE,
    evidence_floor: EvidenceFloor = EvidenceFloor.NONE,
    confidence: float = 0.0,
    requires_human_ack: bool = False,
    lease_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    organ: str = "",
    **kwargs: Any,
) -> GovernedResult:
    """
    Run a tool call through the full sovereign fabric.

    This is THE function. Every MCP tool call should use it.

    Steps:
    1. Create AuthorizationEnvelope
    2. Verify identity binding
    3. Run policy engine (constitutional floor checks)
    4. Record trace span
    5. Return GovernedResult
    """
    trace_collector = get_trace_collector()
    policy_engine = get_policy_engine()

    # Step 1: Auto-classify action if not provided
    if action_class is None:
        action_class = classify_action(tool_name)

    # Step 2: Create envelope
    envelope = create_envelope(
        actor_id=actor_id,
        session_id=session_id,
        tool_name=tool_name,
        action_class=action_class,
        intent_description=intent,
        reversibility=reversibility,
        blast_radius=blast_radius,
        evidence_floor=evidence_floor,
        confidence=confidence,
        requires_human_ack=requires_human_ack,
        lease_id=lease_id,
        trace_id=trace_id,
    )

    # Step 3: Start trace span
    trace = trace_collector.start_span(
        tool_name=tool_name,
        actor_id=actor_id,
        session_id=session_id,
        action_class=action_class.value,
        organ=organ,
        parent_span_id=parent_span_id,
    )

    # Step 4: Verify sovereignty (/000 + /999 pre-flight)
    sovereign_ctx = get_sovereign_context()
    sovereignty_ok, sovereignty_reason = sovereign_ctx.assert_sovereignty()
    if not sovereignty_ok and action_class in (
        ActionClass.EXECUTE,
        ActionClass.SEAL,
        ActionClass.MUTATE,
    ):
        trace.finish(status="error", verdict="VOID")
        return GovernedResult(
            proceed=False,
            verdict=Verdict.VOID,
            reason=f"SOVEREIGNTY CHECK FAILED: {sovereignty_reason}",
            violated_floors=["F13_SOVEREIGN"],
            envelope=envelope,
            policy_verdict=PolicyVerdict(
                verdict=Verdict.VOID,
                reason=sovereignty_reason,
                violated_floors=["F13_SOVEREIGN"],
                trace_id=trace.trace_id,
                span_id=trace.span_id,
            ),
            trace=trace,
            required_next_step="Verify /000 and /999 surfaces are accessible and valid",
        )

    # Step 5: Verify identity (F11 AUTH)
    identity_ok = verify_identity(session_id, actor_id)
    if not identity_ok and action_class in (ActionClass.EXECUTE, ActionClass.SEAL):
        trace.finish(status="error", verdict="VOID")
        return GovernedResult(
            proceed=False,
            verdict=Verdict.VOID,
            reason=f"F11 AUTH: Identity not verified for {actor_id} in session {session_id}",
            violated_floors=["F11_AUTH"],
            envelope=envelope,
            policy_verdict=PolicyVerdict(
                verdict=Verdict.VOID,
                reason="Identity not verified",
                violated_floors=["F11_AUTH"],
                trace_id=trace.trace_id,
                span_id=trace.span_id,
            ),
            trace=trace,
            required_next_step="Register identity via register_identity() or arif_init",
        )

    # Step 6: Run policy engine
    policy_verdict = policy_engine.evaluate(envelope)

    # Step 7: Finish trace
    trace.finish(
        status="ok"
        if policy_verdict.verdict == Verdict.PROCEED
        else policy_verdict.verdict.value.lower(),
        verdict=policy_verdict.verdict.value,
    )

    # Step 8: Return governed result
    return GovernedResult(
        proceed=policy_verdict.verdict == Verdict.PROCEED,
        verdict=policy_verdict.verdict,
        reason=policy_verdict.reason,
        violated_floors=policy_verdict.violated_floors,
        envelope=envelope,
        policy_verdict=policy_verdict,
        trace=trace,
        required_next_step=policy_verdict.required_next_step,
    )


# ── Convenience Wrappers ───────────────────────────────────────────────


def govern_observe(
    actor_id: str,
    session_id: str,
    tool_name: str,
    intent: str = "",
    **kwargs: Any,
) -> GovernedResult:
    """Govern an observe-class action (read-only, no side effects)."""
    return govern(
        actor_id=actor_id,
        session_id=session_id,
        tool_name=tool_name,
        intent=intent,
        action_class=ActionClass.OBSERVE,
        reversibility=Reversibility.FULL,
        blast_radius=BlastRadius.NONE,
        evidence_floor=EvidenceFloor.NONE,
        **kwargs,
    )


def govern_mutate(
    actor_id: str,
    session_id: str,
    tool_name: str,
    intent: str = "",
    lease_id: str = "",
    **kwargs: Any,
) -> GovernedResult:
    """Govern a mutate-class action (state change, requires lease)."""
    return govern(
        actor_id=actor_id,
        session_id=session_id,
        tool_name=tool_name,
        intent=intent,
        action_class=ActionClass.MUTATE,
        reversibility=Reversibility.FULL,
        blast_radius=BlastRadius.LOCAL,
        evidence_floor=EvidenceFloor.OBSERVED,
        lease_id=lease_id,
        **kwargs,
    )


def govern_seal(
    actor_id: str,
    session_id: str,
    tool_name: str,
    intent: str = "",
    human_ack_token: str = "",
    **kwargs: Any,
) -> GovernedResult:
    """Govern a seal-class action (irreversible, requires human ack)."""
    return govern(
        actor_id=actor_id,
        session_id=session_id,
        tool_name=tool_name,
        intent=intent,
        action_class=ActionClass.SEAL,
        reversibility=Reversibility.NONE,
        blast_radius=BlastRadius.IRREVERSIBLE,
        evidence_floor=EvidenceFloor.GROUND_TRUTH,
        requires_human_ack=True,
        **kwargs,
    )
