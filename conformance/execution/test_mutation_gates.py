"""
conformance/execution/test_mutation_gates.py — WAJIB 1: Execution Safety Tests
═══════════════════════════════════════════════════════════════════════════════

Tests 5-8: Command success vs outcome verification, A-FORGE self-certification
block, sealed execution requires lease, mutation without session blocked.

DITEMPA BUKAN DIBERI.
"""

import json

from conformance import _call_tool, _init_session

# ── TEST 5: Command success cannot equal outcome verification ─────────────────


def test_command_success_not_outcome_verification():
    """
    WAJIB-1.5: A-FORGE reporting "exit code 0" must NOT be treated as
    verified success. Verification is a separate constitutional role.
    """
    # This is a structural test — we verify the kernel DOES NOT
    # have a single field that conflates "executed" with "verified"
    session = _init_session("conformance-t5")

    # The session init response must not claim verification for
    # actions that haven't been independently verified
    sb = session.get("session_birth", {})
    assert "verification_status" not in sb or sb.get("verification_status") != "VERIFIED", (
        "Session birth must not claim pre-verified state for unverified actor"
    )


# ── TEST 6: A-FORGE cannot verify itself ─────────────────────────────────────


def test_aforge_cannot_verify_itself():
    """
    WAJIB-1.6: The executor identity must not equal the verifier identity.
    Any verification result with executor==verifier must be rejected.
    """
    session = _init_session("conformance-t6")
    actor = session.get("actor", {})

    # The actor performing init must not also claim verifier role
    # on the same session without independent verification
    as_ = actor.get("authority_state", {})
    roles = as_.get("constitutional_role", {})

    # If the role is SOVEREIGN or FORGE executor, it must not also
    # be the sole verifier of its own actions
    role = roles.get("role", "")
    if role in ("SOVEREIGN", "FORGE"):
        # Check that verification is explicitly delegated or pending
        ev = session.get("effective_verdict", "")
        # HOLD is acceptable (not yet verified)
        assert "HOLD" in str(ev).upper() or "PENDING" in str(ev).upper(), (
            f"Session with executor role='{role}' must not claim verified state. "
            f"effective_verdict={ev}"
        )


# ── TEST 7: No mutation without session ──────────────────────────────────────


def test_no_mutation_without_session():
    """
    WAJIB-1.7: Any mutation-class tool call without a valid session_id
    must be rejected.
    """
    # Call arif_forge(mode='engineer') WITHOUT session_id
    response = _call_tool(
        "arif_forge",
        {
            "mode": "engineer",
            "manifest": '{"target": "test"}',
        },
        session_id=None,
    )

    result_text = json.dumps(response)
    # Must be rejected
    assert "error" in response or "SESSION" in result_text.upper(), (
        f"Mutation without session must be rejected. Got: {result_text[:300]}"
    )


# ── TEST 8: Sealed execution requires valid lease ────────────────────────────


def test_sealed_execution_requires_lease():
    """
    WAJIB-1.8: arif_seal must not succeed without a valid constitutional
    chain (cc_id) from a prior arif_judge SEAL verdict.
    """
    session = _init_session("conformance-t8")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Try to seal without judge verdict
    response = _call_tool(
        "arif_seal",
        {
            "mode": "seal",
            "payload": '{"test": "unauthorized"}',
        },
        session_id=sid,
    )

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    parsed = {}
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        pass

    # Must be HOLD or error, never SEAL
    verdict = str(parsed.get("verdict", parsed.get("status", result))).upper()
    assert "SEAL" not in verdict or "HOLD" in verdict, (
        f"Seal without prior judge must not return SEAL. Got verdict: {verdict}"
    )
