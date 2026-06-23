"""
arifosmcp.constitution.runtime_hook — Runtime enforcement of the Godel Lock.

Called by arif_forge BEFORE any MUTATE action proceeds.
If the action would violate any G1-G7 axiom, the action is BLOCKED
and the appropriate verdict is returned.

This is the anti-Beautiful-One invariant in machine form.
"""

from typing import Any

from . import (
    GODEL_AXIOMS,
    get_axiom,
)


class GodelLockViolation(Exception):
    """Raised when an action would violate the Godel Lock axioms."""

    def __init__(self, axiom_id: str, axiom_name: str, verdict: str, reason: str):
        self.axiom_id = axiom_id
        self.axiom_name = axiom_name
        self.verdict = verdict
        self.reason = reason
        super().__init__(f"G[{axiom_id}] {axiom_name} violation: {reason} (verdict={verdict})")


def check_godel_lock(
    action_class: str,  # "OBSERVE" | "RETRIEVE" | "DECIDE" | "MUTATE"
    actor_id: str,  # who is doing the action
    actor_signature: str,  # their cryptographic signature
    has_judge_hash: bool,  # does the action carry a judge_state_hash?
    has_plan_id: bool,  # does the action carry an approved plan_id?
    has_vaul_entry: bool,  # does the action carry a vault_entry_id?
    has_vaul999_connection: bool,  # is VAULT999 connected?
    failure_cause: str = None,  # explicit cause if known
) -> dict[str, Any]:
    """
    Pre-execution check against the Godel Lock.

    Returns:
        {"ok": True} if the action may proceed.
        {"ok": False, "verdict": str, "axiom_id": str, "axiom_name": str, "reason": str}
        if the action must be blocked.

    This is the "anti-Beautiful-One" gate. The agent CANNOT certify its own
    safety from inside its own frame. Every check is grounded in observable
    substrate (signatures, hashes, plan_ids, vault state) — never in the
    agent's self-report.
    """
    # G1 — Incompleteness: if failure_cause indicates self-certified truth, void
    if failure_cause == "self_certified_truth":
        return _violation("G1", "agent claimed its own correctness as final")

    # G3 — External Witness: a MUTATE without actor_signature or judge_hash
    if action_class == "MUTATE":
        if not actor_signature:
            return _violation("G3", "MUTATE without external actor_signature (no witness)")
        if not has_judge_hash:
            return _violation("G3", "MUTATE without judge_state_hash (no witness of judgment)")

    # G4 — Non-Unity: a MUTATE that bypasses plan registry (single-model, single-witness)
    if action_class == "MUTATE" and not has_plan_id:
        return _violation("G4", "MUTATE without approved plan_id (single-witness arbitration)")

    # G6 — Pre-Executive Gate: a commit without VAULT entry, or any action
    # when VAULT999 is broken
    if action_class == "MUTATE":
        if not has_vaul999_connection:
            return _violation("G6", "VAULT999 not connected — pre-executive gate cannot verify")
        # commit-class requires vault_entry_id
        if failure_cause == "commit_without_vault" or (
            "commit" in (failure_cause or "") and not has_vaul_entry
        ):
            return _violation("G6", "commit action without vault_entry_id")

    # G7 — Sovereign Override: any veto_dismissal cause is HARD_HOLD
    if failure_cause == "veto_dismissal":
        return _violation("G7", "agent attempted to dismiss or re-argue a sovereign veto")

    # G5 — Frontier: if caller marks output as FACT but context is degraded,
    # this is frontier_passed_as_fact. The caller should set failure_cause
    # explicitly; if not, this is the catch-all for HYPOTHESIS being passed as FACT.
    if failure_cause == "frontier_passed_as_fact":
        return _violation("G5", "frontier claim presented as final truth")

    return {"ok": True}


def _violation(axiom_id: str, reason: str) -> dict[str, Any]:
    axiom = get_axiom(axiom_id)
    return {
        "ok": False,
        "verdict": axiom["failure_verdict"],
        "axiom_id": axiom_id,
        "axiom_name": axiom["name"],
        "reason": reason,
    }


def explain_lock() -> str:
    """Return a human-readable summary of all 7 axioms for operator display."""
    lines = ["GODEL LOCK — 7 irreducible axioms", "=" * 50]
    for a in GODEL_AXIOMS:
        lines.append(f"  {a['id']} {a['name']}")
        lines.append(f"     {a['text'].strip()[:120]}...")
        lines.append(f"     failure_cause: {a['failure_cause']} -> {a['failure_verdict']}")
        lines.append("")
    return "\n".join(lines)
