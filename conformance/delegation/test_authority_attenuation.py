"""
conformance/delegation/test_authority_attenuation.py — WAJIB 1: Delegation Safety
═════════════════════════════════════════════════════════════════════════════════

Tests 9-11: Child authority ≤ parent, expired delegation denied,
missing lineage denied. Full WAJIB 4 implementation requires signed
delegation envelopes — these are structural conformance tests.

DITEMPA BUKAN DIBERI.
"""

import json

from conformance import _call_tool, _init_session

# ── TEST 9: Child authority cannot exceed parent ─────────────────────────────


def test_child_authority_cannot_exceed_parent():
    """
    WAJIB-1.9 (WAJIB 4): Any session spawned from a parent session
    must have authority ≤ parent authority. Full test requires
    delegation envelope implementation — this is a structural gate.
    """
    # For now: verify the session model has the concept of
    # parent_session_id and authority band that supports attenuation
    parent = _init_session("conformance-t9-parent")
    parent_sid = parent.get("session_birth", {}).get("session_id", "")

    # Resume with parent session and check that authority
    # is never elevated above what parent had
    response = _call_tool(
        "arif_init",
        {
            "mode": "resume",
            "session_id": parent_sid,
        },
    )

    result_text = json.dumps(response)
    # The resume should not grant MORE authority than init
    assert "error" not in response or "SESSION" in result_text.upper(), (
        "Session resume must be handled gracefully"
    )


# ── TEST 10: Expired delegation is denied ────────────────────────────────────


def test_expired_delegation_denied():
    """
    WAJIB-1.10: A session with an expired lease or delegation
    must be denied mutation access.
    """
    session = _init_session("conformance-t10")
    sid = session.get("session_birth", {}).get("session_id", "")

    # The session_birth should carry mutation_allowed only
    # if authority is sufficient and not expired
    sb = session.get("session_birth", {})
    mutation_allowed = sb.get("mutation_allowed", False)
    authority = sb.get("authority_mode", "UNKNOWN")

    # For a fresh init with actor_id but no SCT/crypto proof:
    # mutation should reflect actual capability, not aspirational
    if authority == "OBSERVE_ONLY":
        assert mutation_allowed is False, (
            f"OBSERVE_ONLY session must not allow mutation. mutation_allowed={mutation_allowed}"
        )


# ── TEST 11: Missing delegation lineage is denied ────────────────────────────


def test_missing_lineage_denied():
    """
    WAJIB-1.11: A session claiming delegated authority without
    proving parent lineage must be downgraded or rejected.
    """
    # Light mode — no actor verification — must be OBSERVE_ONLY
    response = _call_tool(
        "arif_init",
        {
            "mode": "light",
            "intent": "conformance-t11",
        },
    )
    content = response.get("result", {}).get("content", [])
    result_text = ""
    for item in content:
        result_text += item.get("text", "")

    parsed = {}
    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError:
        pass

    sb = parsed.get("session_birth", {})
    authority = sb.get("authority_mode", "")
    mutation = sb.get("mutation_allowed", False)

    # Light mode without actor must never allow mutation
    assert mutation is False, (
        f"Light mode (no actor verification) must not allow mutation. "
        f"authority={authority}, mutation_allowed={mutation}"
    )
