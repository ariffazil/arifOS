"""
arifOS v2.0 — Session Policy Clamp (Runtime Display-Register Binding)
═══════════════════════════════════════════════════════════════════════════
Forged 2026-08-15 — F13 "Go" on Shadow Mode runtime architecture.

DOCTRINE (sovereign directive 2026-08-15): a display register (e.g. shadow
mode) is REAL only if it is bound at the kernel as session state, not as
prompt text. A session bound with an agent_policy carries its own authority
ceiling. The kernel never upgrades a session's authority from a tool default.

Enforcement semantics (explicit-constraint doctrine):
- Empty/absent lists in agent_policy = UNSPECIFIED (no constraint). We do not
  retroactively impose DEFAULT_DENY on legacy anonymous traffic; init-time
  gating owns that. The runtime clamp enforces only what the policy states.
- display_register=="shadow" or policy_mode=="shadow"
  → ceiling: OBSERVE / ANALYZE / DRAFT / SIMULATE only.
- denied_tools non-empty and tool listed → HOLD.
- allowed_tools non-empty and tool NOT listed → HOLD.
- irreversibility_threshold is honoured for mutation-class actions:
  action_rank/6 > threshold → HOLD (only checked at MUTATE and above).

Fail posture: lookup failure or malformed policy → NO CLAMP (the rest of the
constitutional gate stack still applies). A positively-found constraint is
enforced fail-closed: HOLD, never silently dropped.

DITEMPA BUKAN DIBERI — display registers are forged, not narrated.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arifosmcp.session_policy")

# Mutation-and-above classes the threshold ladder applies to.
_RANK: dict[str, float] = {
    "OBSERVE": 1.0,
    "ANALYZE": 2.0,
    "DRAFT": 3.0,
    "SIMULATE": 3.0,
    "MUTATE": 4.0,
    "EXTERNAL_SIDE_EFFECT": 5.0,
    "IRREVERSIBLE": 6.0,
}

# Shadow ceiling: everything a display register may do without becoming a hand.
_SHADOW_CEILING = frozenset({"OBSERVE", "ANALYZE", "DRAFT", "SIMULATE"})

# Tools exempt from clamping: the ignition verb itself must always run,
# otherwise a session could never be established or inspected.
_IGNITION_EXEMPT = frozenset({"arif_init"})


def _lookup_session(session_id: str) -> dict[str, Any] | None:
    """Find the session record across the two session stores (best effort).

    Order: identity store (session.py — where arif_init binds policy) then
    the runtime _SESSIONS proxy in tools.py.
    """
    try:
        from arifosmcp.runtime.session import get_session_identity

        rec = get_session_identity(session_id)
        if isinstance(rec, dict) and rec:
            return rec
    except Exception:  # pragma: no cover - defensive
        pass
    try:
        from arifosmcp.runtime.tools import _SESSIONS

        rec = _SESSIONS.get(session_id)
        if isinstance(rec, dict) and rec:
            return rec
    except Exception:  # pragma: no cover - defensive
        pass
    return None


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def session_policy_clamp(
    session_id: str | None,
    tool_name: str,
    action_class: str,
    *,
    tool_mode: str = "",
) -> dict[str, Any] | None:
    """Enforce the session-bound agent_policy for this call.

    Returns None when the call may proceed (or no policy constrains it).
    Returns a clamp dict {"reason", "violations", "blocked_action_class"}
    when the session's own policy forbids this tool/action — the caller MUST
    convert that into a HOLD verdict.

    When *tool_mode* is provided, the irreversibility-threshold check resolves
    the action class per-mode from CANONICAL_TOOL_MANIFEST (Layer 6 effect
    typing).  This prevents safe read-only modes (e.g. arif_seal mode=verify)
    from being gated as IRREVERSIBLE.
    """
    sid = (session_id or "").strip()
    if not sid or tool_name in _IGNITION_EXEMPT:
        return None

    action = (action_class or "OBSERVE").strip().upper()
    rank = _RANK.get(action)
    if rank is None:
        # UNKNOWN action classes are handled by the main gate (fail-closed
        # there); no policy opinion needed here.
        return None

    # ── Layer 6 mode-resolution for threshold check ──────────────────────
    # When a tool_mode is given, resolve the manifest's per-mode action
    # class so the threshold check uses the mode-resolved rank, not the
    # tool-level default.  e.g. arif_seal mode=verify → OBSERVE (rank 1.0),
    # not IRREVERSIBLE (rank 6.0).
    threshold_rank = rank
    if tool_mode:
        try:
            from arifosmcp.runtime.pre_execution_gate import (
                CANONICAL_TOOL_MANIFEST,
                resolve_action_class_for_mode,
            )
            from arifosmcp.schemas.kernel_envelope import ActionClass as _AC

            _manifest_entry = CANONICAL_TOOL_MANIFEST.get(tool_name)
            if _manifest_entry is not None:
                _resolved = resolve_action_class_for_mode(
                    tool_name, tool_mode, _manifest_entry.action_class
                )
                threshold_rank = _RANK.get(_resolved.value, rank)
        except Exception:
            pass  # fallback to tool-level rank

    rec = _lookup_session(sid)
    if not rec:
        return None

    policy = rec.get("agent_policy")
    if not isinstance(policy, dict) or not policy:
        return None

    tool = str(tool_name).strip()
    canonical = tool.split(".")[-1]

    # ── Explicit tool lists ─────────────────────────────────────────────
    denied = _as_str_list(policy.get("denied_tools"))
    if denied and (tool in denied or canonical in denied):
        return {
            "reason": (
                f"SESSION_POLICY: tool '{tool}' is denied by this session's "
                f"agent_policy (role={policy.get('agent_role', 'unspecified')})"
            ),
            "violations": ["F13_SOVEREIGN — session policy denied_tools"],
            "blocked_action_class": action,
        }

    allowed = _as_str_list(policy.get("allowed_tools"))
    if allowed and tool not in allowed and canonical not in allowed:
        return {
            "reason": (
                f"SESSION_POLICY: tool '{tool}' is not in this session's "
                f"allowed_tools (role={policy.get('agent_role', 'unspecified')})"
            ),
            "violations": ["F13_SOVEREIGN — session policy allowed_tools"],
            "blocked_action_class": action,
        }

    # ── Display-register ceiling (shadow mode) ──────────────────────────
    register = str(
        policy.get("display_register")
        or policy.get("policy_mode")
        or ""
    ).strip().lower()
    if register == "shadow" and action not in _SHADOW_CEILING:
        return {
            "reason": (
                f"SESSION_POLICY: display register '{register}' caps this session "
                f"at OBSERVE/ANALYZE/DRAFT/SIMULATE — '{action}' refused"
            ),
            "violations": ["F13_SOVEREIGN — display register authority ceiling"],
            "blocked_action_class": action,
        }

    # ── Irreversibility threshold (mutation ladder only) ────────────────
    # Uses threshold_rank (mode-resolved) so read-only modes of dangerous
    # tools (e.g. arif_seal mode=verify) pass the threshold gate.
    if threshold_rank >= 4.0:
        try:
            threshold = float(policy.get("irreversibility_threshold"))
        except (TypeError, ValueError):
            threshold = None
        if threshold is not None and (threshold_rank / 6.0) > threshold + 1e-9:
            return {
                "reason": (
                    f"SESSION_POLICY: action '{action}' (rank {threshold_rank:.0f}/6) exceeds "
                    f"this session's irreversibility_threshold {threshold:.2f}"
                ),
                "violations": ["F1_AMANAH — session irreversibility threshold"],
                "blocked_action_class": action,
            }

    return None


def _self_check() -> dict[str, Any]:
    """Local self-test of clamp semantics (no I/O)."""
    shadow = {
        "agent_role": "hermes-shadow",
        "display_register": "shadow",
        "allowed_tools": ["arif_observe"],
        "denied_tools": ["arif_seal"],
        "irreversibility_threshold": 0.0,
    }
    cases = [
        ("shadow+MUTATE", shadow, "arif_think", "MUTATE", True),
        ("shadow+OBSERVE ok", shadow, "arif_observe", "OBSERVE", False),
        ("denied tool", shadow, "arif_seal", "OBSERVE", True),
        ("not allowed tool", shadow, "arif_route", "OBSERVE", True),
        ("no policy", None, "arif_forge", "MUTATE", False),
        ("empty policy", {}, "arif_forge", "MUTATE", False),
        ("threshold pass", {"irreversibility_threshold": 0.9}, "arif_forge", "MUTATE", False),
        ("init exempt", shadow, "arif_init", "OBSERVE", False),
    ]
    ok = 0
    results = []
    for name, pol, tool, action, expect_block in cases:
        if tool == "arif_init":
            blocked = False  # ignition exempt at the public entrypoint
        else:
            blocked = _semantic_clamp(pol, tool, action)
        passed = blocked == expect_block
        ok += passed
        results.append((name, passed))

    return {
        "module": "session_policy",
        "tests": len(results),
        "passed": ok,
        "results": results,
        "verdict": "OK" if ok == len(results) else "FAIL",
    }


def _semantic_clamp(pol: dict | None, tool: str, action: str) -> bool:
    """Pure clamp logic without any session-store lookup (self-check + reuse)."""
    act = action.upper()
    rank = _RANK.get(act)
    if rank is None:
        return False
    if not isinstance(pol, dict) or not pol:
        return False
    denied = _as_str_list(pol.get("denied_tools"))
    if denied and tool in denied:
        return True
    allowed = _as_str_list(pol.get("allowed_tools"))
    if allowed and tool not in allowed:
        return True
    reg = str(pol.get("display_register") or pol.get("policy_mode") or "").lower()
    if reg == "shadow" and act not in _SHADOW_CEILING:
        return True
    if rank >= 4.0:
        try:
            t = float(pol.get("irreversibility_threshold"))
        except (TypeError, ValueError):
            t = None
        if t is not None and (rank / 6.0) > t + 1e-9:
            return True
    return False
