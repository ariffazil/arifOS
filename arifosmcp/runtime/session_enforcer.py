"""
arifosmcp/runtime/session_enforcer.py
════════════════════════════════════════
P0-1: SESSION ENFORCEMENT HARNESS

Ensures every MCP tool call carries a valid session_id.
No session_id → HOLD. Expired session → HOLD.
This is the FIRST gate in the governance pipeline.

F1 AMANAH: Additive, non-destructive. Wraps, never mutates.
F2 TRUTH: Session validity checked against live registry.
F11 AUTH: Anonymous calls blocked at the boundary.
F13 SOVEREIGN: Human sessions require explicit init.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger("arifosmcp.session_enforcer")

# ═══════════════════════════════════════════════════════════════
# SESSION ENFORCEMENT RESULT
# ═══════════════════════════════════════════════════════════════


class SessionVerdict(StrEnum):
    VALID = "VALID"
    MISSING = "MISSING"  # No session_id at all
    EXPIRED = "EXPIRED"  # Session past TTL
    UNVERIFIED = "UNVERIFIED"  # Session exists but identity not verified
    HOLD = "HOLD"  # Active hold on session
    REVOKED = "REVOKED"  # Session explicitly revoked


SESSION_TTL_HOURS = 24  # Sessions expire after 24h
REQUIRED_FOR_TIERS = {
    # Tier 1 tools (read-only) — can proceed with anonymous session
    "T1_READONLY": ["arif_ops_measure", "arif_sense_observe", "arif_evidence_fetch"],
    # Tier 2 tools (reasoning) — need valid session
    "T2_REASON": [
        "arif_mind_reason",
        "arif_heart_critique",
        "arif_reply_compose",
        "arif_memory_recall",
        "arif_kernel_route",
    ],
    # Tier 3 tools (governance) — need verified identity
    "T3_GOVERN": [
        "arif_session_init",
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_forge_execute",
        "arif_gateway_connect",
        "arif_lease_issue",
        "arif_lease_revoke",
        "arif_lease_inspect",
    ],
}


@dataclass
class SessionRecord:
    """In-process session state."""

    session_id: str
    actor_id: str = "anonymous"
    identity_verified: bool = False
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    hold_active: bool = False
    hold_reason: str = ""
    tool_calls: int = 0
    budget_consumed: float = 0.0


# In-process session registry (L1 ephemeral)
_SESSIONS: dict[str, SessionRecord] = {}


def register_session(
    session_id: str, actor_id: str = "anonymous", identity_verified: bool = False
) -> SessionRecord:
    """Register or update a session."""
    if session_id in _SESSIONS:
        rec = _SESSIONS[session_id]
        rec.last_active = time.time()
        if actor_id and actor_id != "anonymous":
            rec.actor_id = actor_id
        if identity_verified:
            rec.identity_verified = True
        return rec

    rec = SessionRecord(
        session_id=session_id,
        actor_id=actor_id,
        identity_verified=identity_verified,
    )
    _SESSIONS[session_id] = rec
    logger.info(f"[session_enforcer] Registered session {session_id} actor={actor_id}")
    return rec


def revoke_session(session_id: str, reason: str = "sovereign_revoke") -> bool:
    """Revoke a session."""
    if session_id in _SESSIONS:
        _SESSIONS[session_id].hold_active = True
        _SESSIONS[session_id].hold_reason = reason
        logger.info(f"[session_enforcer] Revoked session {session_id}: {reason}")
        return True
    return False


def get_session(session_id: str) -> SessionRecord | None:
    """Get a session record."""
    return _SESSIONS.get(session_id)


def _tool_tier(tool_name: str) -> str:
    """Determine the minimum session tier required for a tool."""
    for tier, tools in REQUIRED_FOR_TIERS.items():
        if tool_name in tools:
            return tier
    return "T2_REASON"  # Default: need valid session


def enforce_session(
    tool_name: str,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Enforce session requirements for a tool call.

    Returns:
        {"verdict": "VALID"|"MISSING"|"EXPIRED"|..., "session": SessionRecord|None, "reason": str}
    """
    tier = _tool_tier(tool_name)

    # T1 tools: can be anonymous
    if tier == "T1_READONLY":
        if not session_id or session_id in ("unknown", "None", "", "anonymous"):
            # Auto-create anonymous session for read-only tools
            import uuid

            sid = f"anon_{uuid.uuid4().hex[:12]}"
            rec = register_session(sid, actor_id="anonymous", identity_verified=False)
            return {
                "verdict": SessionVerdict.VALID,
                "session": rec,
                "reason": "auto_anonymous",
                "session_id": sid,
                "tier": tier,
            }

    # T2/T3 tools: MUST have valid session
    if not session_id or session_id in ("unknown", "None", "", "anonymous"):
        return {
            "verdict": SessionVerdict.MISSING,
            "session": None,
            "reason": f"Tool '{tool_name}' (tier={tier}) requires valid session_id",
            "session_id": None,
            "tier": tier,
        }

    rec = _SESSIONS.get(session_id)
    if not rec:
        return {
            "verdict": SessionVerdict.MISSING,
            "session": None,
            "reason": f"Session '{session_id}' not found in registry",
            "session_id": session_id,
            "tier": tier,
        }

    # Check expiry
    age_hours = (time.time() - rec.created_at) / 3600
    if age_hours > SESSION_TTL_HOURS:
        return {
            "verdict": SessionVerdict.EXPIRED,
            "session": rec,
            "reason": f"Session expired ({age_hours:.1f}h > {SESSION_TTL_HOURS}h TTL)",
            "session_id": session_id,
            "tier": tier,
        }

    # Check hold
    if rec.hold_active:
        return {
            "verdict": SessionVerdict.HOLD,
            "session": rec,
            "reason": f"Session on HOLD: {rec.hold_reason}",
            "session_id": session_id,
            "tier": tier,
        }

    # T3 tools: MUST have verified identity
    if tier == "T3_GOVERN" and not rec.identity_verified:
        return {
            "verdict": SessionVerdict.UNVERIFIED,
            "session": rec,
            "reason": f"Tool '{tool_name}' requires verified identity (F11 AUTH)",
            "session_id": session_id,
            "tier": tier,
        }

    # Update activity
    rec.last_active = time.time()
    rec.tool_calls += 1

    return {
        "verdict": SessionVerdict.VALID,
        "session": rec,
        "reason": "ok",
        "session_id": session_id,
        "tier": tier,
    }


def _self_check() -> dict[str, Any]:
    """Self-test — verify session enforcement logic."""
    results = []

    # Test 1: Missing session on T2 tool
    r = enforce_session("arif_mind_reason", session_id=None)
    results.append(
        ("T2_missing_session", r["verdict"] == SessionVerdict.MISSING, str(r["verdict"]))
    )

    # Test 2: Auto-anonymous on T1 tool
    r = enforce_session("arif_ops_measure", session_id=None)
    results.append(("T1_auto_anonymous", r["verdict"] == SessionVerdict.VALID, str(r["verdict"])))

    # Test 3: Valid session
    sid = "test_session_001"
    register_session(sid, actor_id="test_agent", identity_verified=True)
    r = enforce_session("arif_mind_reason", session_id=sid)
    results.append(("T2_valid_session", r["verdict"] == SessionVerdict.VALID, str(r["verdict"])))

    # Test 4: T3 needs verified identity
    sid2 = "test_session_002"
    register_session(sid2, actor_id="test_agent", identity_verified=False)
    r = enforce_session("arif_forge_execute", session_id=sid2)
    results.append(
        ("T3_unverified_blocked", r["verdict"] == SessionVerdict.UNVERIFIED, str(r["verdict"]))
    )

    # Test 5: T3 with verified identity
    r = enforce_session("arif_vault_seal", session_id=sid)
    results.append(("T3_verified_ok", r["verdict"] == SessionVerdict.VALID, str(r["verdict"])))

    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "session_enforcer",
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


# ── Integration point ──────────────────────────────────────────────
# Called by governance_pipeline.py Gate 0 (SESSION binding).
# Returns (allowed: bool, session_record, reason: str)
# ────────────────────────────────────────────────────────────────────


def gate_session(
    tool_name: str, session_id: str | None = None, actor_id: str | None = None
) -> tuple[bool, SessionRecord | None, str]:
    """Gate 0: Session binding check. Returns (allowed, record, reason)."""
    result = enforce_session(tool_name, session_id=session_id, actor_id=actor_id)
    allowed = result["verdict"] == SessionVerdict.VALID
    rec = result.get("session")
    reason = result.get("reason", "unknown")
    return allowed, rec, reason


__all__ = [
    "SessionVerdict",
    "SessionRecord",
    "register_session",
    "revoke_session",
    "get_session",
    "enforce_session",
    "gate_session",
    "_self_check",
    "REQUIRED_FOR_TIERS",
    "SESSION_TTL_HOURS",
]
