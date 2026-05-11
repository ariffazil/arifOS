"""Governance Interceptor — arifOS Command Center v0.3.

Mandatory governance middleware for all CC tool calls.
Every call is gated by:

  1. Session gate     — valid, non-expired session required
  2. Identity gate    — actor_id must be non-anonymous for consequential actions
  3. Plan gate        — for actions that require an approved plan
  4. Judge gate       — SEAL verdict required before Forge/Vault execution
  5. Human ack gate   — irreversible actions require explicit ack

Usage:
    from arifosmcp.apps.command_center.interceptor import governance_guard

    result = governance_guard(
        action="forge_dry_run",
        actor_id="arif",
        session_id="SEAL-abc",
        payload={"manifest": "..."},
        require_plan=True,
        require_judge_seal=True,
    )
    if result["status"] == "blocked":
        return result  # return blocked result to caller
    # proceed with action

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InterceptorResult(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    HOLD = "hold"


# ─────────────────────────────────────────────────────────────────────────────
# Action classifications
# ─────────────────────────────────────────────────────────────────────────────

# Actions that require a valid session + actor
_ACTOR_GATED = {
    "arif_cc_judge_action",
    "arif_cc_forge_dry_run",
    "arif_cc_vault_dry_seal",
    "arif_cc_gateway_handshake",
}

# Actions that require an approved plan (plan_state == approved)
_PLAN_GATED = {"arif_cc_forge_dry_run", "arif_cc_vault_dry_seal"}

# Actions that require a SEAL verdict
_SEAL_GATED = {"arif_cc_forge_dry_run", "arif_cc_vault_dry_seal"}

# Actions that require explicit human acknowledgment
_IRREVERSIBLE_GATED = {"arif_cc_forge_dry_run"}


@dataclass
class GovernanceCheck:
    status: InterceptorResult
    action: str
    reason: str = ""
    required_next: str | None = None
    gate: str = ""  # which gate blocked: session | identity | plan | judge | ack


def governance_guard(
    action: str,
    actor_id: str,
    session_id: str,
    payload: dict[str, Any] | None = None,
    plan_state: str = "draft",
    judge_verdict: str | None = None,
    judge_state_hash: str | None = None,
    approved_plan_id: str | None = None,
    ack_irreversible: bool = False,
    session_expired: bool = False,
    session_token_valid: bool = True,
) -> dict[str, Any]:
    """Gate every CC tool call through mandatory governance checks.

    Returns a dict:
      {
        "status": "allowed" | "blocked" | "hold",
        "action": str,
        "reason": str,
        "gate": str,
        "required_next": str | None,
      }
    """
    if payload is None:
        payload = {}

    # ── Gate 1: Session validity ──────────────────────────────────────────
    if not session_id or session_id == "uninitialized":
        return {
            "status": "blocked",
            "action": action,
            "reason": "No valid session. Initialize a session first.",
            "gate": "session",
            "required_next": "arif_cc_session_status",
        }

    if session_expired or not session_token_valid:
        return {
            "status": "blocked",
            "action": action,
            "reason": "Session expired or token invalid. Reinitialize.",
            "gate": "session",
            "required_next": "arif_cc_session_status",
        }

    # ── Gate 2: Identity ──────────────────────────────────────────────────
    if action in _ACTOR_GATED and actor_id in ("anonymous", "", None):
        return {
            "status": "blocked",
            "action": action,
            "reason": f"{action} requires a declared actor identity. F11/F13.",
            "gate": "identity",
            "required_next": "arif_cc_session_status",
        }

    # ── Gate 3: Plan state ───────────────────────────────────────────────
    if action in _PLAN_GATED:
        if plan_state == "draft":
            return {
                "status": "blocked",
                "action": action,
                "reason": "Plan is in DRAFT state. Submit intent to advance to PLANNED.",
                "gate": "plan",
                "required_next": "arif_cc_judge_action",
            }
        if plan_state == "blocked":
            return {
                "status": "blocked",
                "action": action,
                "reason": "Plan is BLOCKED. Create a new plan.",
                "gate": "plan",
                "required_next": "arif_cc_session_status",
            }
        if plan_state not in ("approved", "executed"):
            return {
                "status": "hold",
                "action": action,
                "reason": f"Plan is {plan_state}. Advance to APPROVED before {action}.",
                "gate": "plan",
                "required_next": "arif_cc_judge_action",
            }

    # ── Gate 4: Judge SEAL ───────────────────────────────────────────────
    if action in _SEAL_GATED:
        if not judge_state_hash:
            return {
                "status": "hold",
                "action": action,
                "reason": "No judge verdict yet. Route through 888_JUDGE first.",
                "gate": "judge",
                "required_next": "arif_cc_judge_action",
            }
        if judge_verdict not in ("SEAL", "SABAR"):
            return {
                "status": "blocked",
                "action": action,
                "reason": f"Verdict is {judge_verdict}. Only SEAL or SABAR can proceed.",
                "gate": "judge",
                "required_next": None,
            }

    # ── Gate 5: Human acknowledgment for irreversible ────────────────────
    if action in _IRREVERSIBLE_GATED:
        is_irreversible = payload.get("irreversible", False)
        if is_irreversible and not ack_irreversible:
            return {
                "status": "hold",
                "action": action,
                "reason": "Irreversible action requires explicit ack_irreversible=true.",
                "gate": "ack",
                "required_next": "human_approval",
            }

    # All gates passed
    return {
        "status": "allowed",
        "action": action,
        "reason": "All governance gates passed.",
        "gate": "",
        "required_next": None,
    }
