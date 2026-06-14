"""
arifosmcp/runtime/f13_gate.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 5: F13 Non-Delegable Gate

Verifies that F13 (sovereign) actions are not being delegated. F13 is
NON-DELEGABLE by constitutional law. This gate physically blocks any
delegation attempt that would bypass direct human sovereign authority.

Checks:
  1. Caller has direct F13 authority (not delegated)
  2. Action does not attempt to delegate F13 to a sub-agent
  3. No automation layer claims F13 authority

Constitutional Floors: F13 (SOVEREIGN — absolute)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Authorised sovereign callers. Only entries here may invoke F13-gated actions.
# In production this is checked against the live AAA_HUMAN identity registry.
# ──────────────────────────────────────────────────────────────────────────────

_SOVEREIGN_CALLERS: frozenset[str] = frozenset({
    "human_sovereign",
    "arif",
    "muhammad_arif_bin_fazil",
})

# Terms that, when present in the action body, indicate a delegation attempt.
_DELEGATION_TERMS: frozenset[str] = frozenset({
    "delegate",
    "delegation",
    "sub-agent",
    "subagent",
    "automation",
    "proxy",
    "impersonate",
    "escalate_f13",
    "grant_f13",
})


def _is_delegation_attempt(action: dict) -> str | None:
    """
    Return a reason string if *action* contains delegation keywords, else None.

    Scans both top-level keys and string values of the action dict.
    """
    for key, value in action.items():
        k = key.lower()
        if any(term in k for term in _DELEGATION_TERMS):
            return f"action key '{key}' contains delegation term"

        if isinstance(value, str):
            v = value.lower()
            if any(term in v for term in _DELEGATION_TERMS):
                return f"action value for '{key}' contains delegation term: '{value}'"

        if isinstance(value, dict):
            nested = _is_delegation_attempt(value)
            if nested is not None:
                return f"nested key '{key}': {nested}"

    return None


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def check_f13_integrity(action: dict, caller: str) -> tuple[bool, str]:
    """
    Verify that F13 (sovereign) actions are not being delegated.

    Parameters
    ----------
    action : dict
        The action payload being checked. Keys and string values are scanned
        for delegation terms.
    caller : str
        The identity of the caller requesting the F13-gated action.

    Returns
    -------
    tuple[bool, str]
        ``(True, "F13 authority verified")`` if the caller is sovereign and
        the action does not attempt delegation, or
        ``(False, "F13 non-delegable: <reason>")`` otherwise.
    """
    # ── check 1: caller has direct F13 authority ────────────────────────────
    caller_norm = caller.strip().lower()
    if caller_norm not in _SOVEREIGN_CALLERS:
        return (False, f"F13 non-delegable: caller '{caller}' is not a recognised sovereign")

    # ── check 2 + 3: action doesn't attempt delegation ──────────────────────
    delegation_reason = _is_delegation_attempt(action)
    if delegation_reason is not None:
        return (False, f"F13 non-delegable: {delegation_reason}")

    return (True, "F13 authority verified")
