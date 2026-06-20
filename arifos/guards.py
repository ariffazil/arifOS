"""
guards.py — The 4 guards of the Band 1 cognition firewall.

Each guard is a function that takes a context and returns a Decision.
Designed to slot into any agent framework (OpenAI, Anthropic, custom).

prethink  — fires at LLM reasoning boundary, BEFORE any tool call
pretool   — fires before every tool call
posttool  — fires after every tool result (F2 auto-stamp)
seal      — fires at end of agent run (VAULT999 write)

The single Decision object flows through all 4 guards.
"""

from __future__ import annotations

from typing import Any

from arifos.actor import Actor
from arifos.client import ArifOSMCPClient
from arifos.decision import (
    ActionClass,
    CognitionLane,
    Decision,
    FloorVerdict,
    HOLD_TRIGGERS,
    RiskEnvelope,
)
from arifos.exceptions import (
    ArifDenied,
    ArifHold,
    ArifSealMissing,
)
from arifos.floors import (
    check_f1_reversibility,
    check_f2_truth,
    check_f7_humility,
    check_f11_audit,
    check_f13_sovereign,
)
from arifos.intent import Intent
from arifos.risk import BlastRadius, Reversibility


# ─────────────────────────────────────────────────────────────────────────────
# 1. prethink — Band 1 cognition firewall
# ─────────────────────────────────────────────────────────────────────────────


async def prethink(
    intent: Intent,
    client: ArifOSMCPClient | None = None,
) -> Decision:
    """
    Band 1 cognition firewall. MUST be called before any other tool.

    The agent declares its intent (via the Intent object). The kernel:
    1. Applies F1-F13 floor checks locally (belt + suspenders)
    2. Issues a kernel call for the full verdict
    3. Returns ALLOW / DENY / HOLD / DEGRADED

    No agent may form an executable plan until this returns ALLOW or
    DEGRADED. This is THE invariant of the arifOS kernel.
    """
    if client is None:
        client = ArifOSMCPClient(actor=intent.actor)

    # 1. Local floor checks
    action_class = ActionClass(intent.action_class)
    # Derive reversibility from action_class (the kernel's local view)
    rev = (
        Reversibility.IRREVERSIBLE.value
        if action_class in HOLD_TRIGGERS
        else Reversibility.REVERSIBLE.value
    )
    floor_verdicts = [
        check_f1_reversibility(action_class, reversibility=rev),
        check_f11_audit(intent.actor.actor_id),
        check_f13_sovereign(action_class, intent.blast_radius.value),
    ]

    # 2. Short-circuit on obvious FAIL/HOLD (no network call needed)
    failed = [f for f in floor_verdicts if f.verdict in ("FAIL", "HOLD")]
    if failed:
        return Decision(
            verdict="HOLD" if any(f.verdict == "HOLD" for f in failed) else "DENY",
            cognition_lane=CognitionLane(intent.lane),
            action_class=action_class,
            floor_verdicts=floor_verdicts,
            risk=RiskEnvelope(
                blast_radius=intent.blast_radius.value,
                reversibility=Reversibility.IRREVERSIBLE.value
                if action_class in HOLD_TRIGGERS
                else Reversibility.REVERSIBLE.value,
                human_ack_required=any(f.verdict == "HOLD" for f in failed),
            ),
            required_human_ack=any(f.verdict == "HOLD" for f in failed),
            reasons=[f.reason for f in failed],
            next_safe_action="Request 888 HOLD from sovereign" if any(f.verdict == "HOLD" for f in failed) else "Refuse action; revise intent",
            taint="UNTRUSTED",
        )

    # 3. Kernel call for full verdict
    try:
        result = await client.kernel_check_call(intent)
    except Exception as exc:
        # Fail-closed: kernel unreachable → HOLD, not ALLOW
        return Decision(
            verdict="HOLD",
            cognition_lane=CognitionLane(intent.lane),
            action_class=action_class,
            floor_verdicts=floor_verdicts + [
                FloorVerdict(
                    floor_id="F8",
                    verdict="FAIL",
                    reason=f"F8 LAW: kernel unreachable: {exc}",
                )
            ],
            risk=RiskEnvelope(
                blast_radius=intent.blast_radius.value,
                reversibility=Reversibility.REVERSIBLE.value,
                human_ack_required=True,
            ),
            required_human_ack=True,
            reasons=[f"kernel unreachable: {exc}"],
            next_safe_action="Cannot reach arifOS kernel — escalate to sovereign",
            taint="UNTRUSTED",
        )

    # 4. Translate kernel result
    verdict = result.get("verdict", "DENY")
    return Decision(
        verdict=verdict,  # type: ignore
        cognition_lane=CognitionLane(intent.lane),
        action_class=action_class,
        lease_id=result.get("lease_id"),
        floor_verdicts=floor_verdicts + result.get("floor_verdicts", []),
        risk=RiskEnvelope(**result.get("risk", {})),
        required_human_ack=verdict == "HOLD",
        reasons=result.get("reasons", []),
        next_safe_action=result.get("next_safe_action"),
        taint="TRUSTED" if verdict == "ALLOW" else "UNTRUSTED",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. pretool — Band 2 tool gate
# ─────────────────────────────────────────────────────────────────────────────


async def pretool(
    tool_name: str,
    tool_args: dict[str, Any],
    prior_decision: Decision,
    client: ArifOSMCPClient | None = None,
) -> Decision:
    """
    Band 2 tool gate. Fires before every tool call.

    Verifies:
    - prior decision is still ALLOW (not expired, not downgraded)
    - tool is in scope
    - lease is still valid (if held)
    - blast-radius hasn't expanded since prethink
    """
    if client is None:
        client = ArifOSMCPClient(actor=Actor(actor_id=prior_decision.lease_id or "arif"))

    # Quick checks on the prior decision
    if prior_decision.verdict in ("DENY", "HOLD"):
        raise ArifHold(prior_decision)

    if prior_decision.verdict == "DEGRADED" and prior_decision.required_human_ack:
        raise ArifHold(prior_decision)

    # Defensive value extraction
    lane_value = (
        prior_decision.cognition_lane.value
        if hasattr(prior_decision.cognition_lane, "value")
        else str(prior_decision.cognition_lane)
    )
    ac_value = (
        prior_decision.action_class.value
        if (prior_decision.action_class and hasattr(prior_decision.action_class, "value"))
        else (str(prior_decision.action_class) if prior_decision.action_class else "OBSERVE")
    )
    br_value = (
        prior_decision.risk.blast_radius
        if isinstance(prior_decision.risk.blast_radius, str)
        else prior_decision.risk.blast_radius
    )

    # Build intent for the kernel call
    intent = Intent(
        action=tool_name,
        action_class=ac_value,
        reason=f"pretool: {tool_name}",
        lane=lane_value,
        blast_radius=BlastRadius(br_value) if isinstance(br_value, str) else br_value,
        proposed_tools=[tool_name],
        actor=Actor(actor_id=prior_decision.lease_id or "arif"),
        session_id=prior_decision.lease_id,
    )

    try:
        result = await client.kernel_check_call(
            intent,
            parent_lease_id=prior_decision.lease_id,
        )
    except Exception as exc:
        raise ArifHold(
            Decision(
                verdict="HOLD",
                cognition_lane=prior_decision.cognition_lane,
                action_class=prior_decision.action_class,
                required_human_ack=True,
                reasons=[f"F8: kernel unreachable on pretool: {exc}"],
            )
        )

    verdict = result.get("verdict", "DENY")
    if verdict in ("DENY", "HOLD"):
        new_decision = Decision(
            verdict=verdict,  # type: ignore
            cognition_lane=prior_decision.cognition_lane,
            action_class=prior_decision.action_class,
            floor_verdicts=result.get("floor_verdicts", []),
            reasons=result.get("reasons", []),
            required_human_ack=verdict == "HOLD",
        )
        if verdict == "HOLD":
            raise ArifHold(new_decision)
        raise ArifDenied(new_decision)

    return Decision(
        verdict="ALLOW",
        cognition_lane=prior_decision.cognition_lane,
        action_class=prior_decision.action_class,
        lease_id=prior_decision.lease_id or result.get("lease_id"),
        floor_verdicts=result.get("floor_verdicts", []),
        reasons=result.get("reasons", []),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. posttool — F2 auto-stamp
# ─────────────────────────────────────────────────────────────────────────────


async def posttool(
    tool_name: str,
    tool_result: Any,
    prior_decision: Decision,
    confidence: float | None = None,
    source: str | None = None,
    client: ArifOSMCPClient | None = None,  # not used, kept for signature parity
) -> Decision:
    """
    Post-tool F2 stamp. Fires after every tool call.

    Applies F2 epistemic discipline + F7 humility check. The kernel-side
    F2 auto-stamper (shipped in commit bd1b6b63c) is the source of truth;
    this guard tracks the result's epistemic status locally.
    """
    f2 = check_f2_truth(taint="UNTRUSTED" if not source else "TRUSTED", source=source)
    f7 = check_f7_humility(confidence)

    return Decision(
        verdict="DEGRADED" if any(f.verdict == "WARN" for f in (f2, f7)) else "ALLOW",
        cognition_lane=prior_decision.cognition_lane,
        action_class=prior_decision.action_class,
        lease_id=prior_decision.lease_id,
        floor_verdicts=[f2, f7],
        risk=prior_decision.risk,
        reasons=[],
        taint="VERIFIED" if source and confidence is not None else prior_decision.taint,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. seal — run-end VAULT999 write
# ─────────────────────────────────────────────────────────────────────────────


async def seal(
    final_output: Any,
    decision_history: list[Decision],
    client: ArifOSMCPClient | None = None,
) -> Decision:
    """
    Run-end seal. Writes the final decision + output to VAULT999.

    Returns a Decision with a `seal_pointer`. Downstream consumers
    can trust the output ONLY if the seal_pointer is present.

    If any prior decision was DENY or HOLD, the seal is refused.
    """
    if client is None:
        last = decision_history[-1] if decision_history else None
        actor = Actor(actor_id=last.lease_id or "arif") if last else Actor(actor_id="arif")
        client = ArifOSMCPClient(actor=actor)

    # Refuse seal on any DENY in history
    if any(d.verdict == "DENY" for d in decision_history):
        return Decision(
            verdict="DENY",
            cognition_lane=CognitionLane.OBSERVE,
            reasons=["seal refused: prior decision was DENY"],
        )

    if any(d.verdict == "HOLD" for d in decision_history):
        return Decision(
            verdict="HOLD",
            cognition_lane=CognitionLane.OBSERVE,
            reasons=["seal refused: prior decision was HOLD — sovereign authority required"],
            required_human_ack=True,
        )

    # Issue the seal
    try:
        last_envelope = (
            decision_history[-1].to_envelope() if decision_history else {}
        )
        result = await client.kernel_seal(
            decision=last_envelope,
            output={"final_output": str(final_output)[:1000]},
        )
    except Exception as exc:
        raise ArifSealMissing(
            Decision(
                verdict="HOLD",
                cognition_lane=CognitionLane.OBSERVE,
                reasons=[f"F11: VAULT999 unreachable: {exc}"],
            )
        )

    seal_pointer = result.get("entry_id") or result.get("seal_pointer")
    if not seal_pointer:
        raise ArifSealMissing(
            Decision(
                verdict="HOLD",
                cognition_lane=CognitionLane.OBSERVE,
                reasons=["F11: kernel returned no seal_pointer"],
            )
        )

    last = decision_history[-1] if decision_history else None
    return Decision(
        verdict="ALLOW",
        cognition_lane=last.cognition_lane if last else CognitionLane.OBSERVE,
        action_class=last.action_class if last else None,
        floor_verdicts=last.floor_verdicts if last else [],
        risk=last.risk if last else RiskEnvelope(),
        reasons=["sealed to VAULT999"],
        seal_pointer=seal_pointer,
        taint="VERIFIED",
    )
