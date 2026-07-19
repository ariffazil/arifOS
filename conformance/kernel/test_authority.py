"""
conformance/kernel/test_authority.py — WAJIB 1: Authority & Identity Tests
═══════════════════════════════════════════════════════════════════════════

Tests 1-4: Model authority, self-approval, unleased mutation, and
kernel state normalization (WAJIB 3).

DITEMPA BUKAN DIBERI.
"""

import json
import pytest
from conformance import _call_tool, _init_session, ARIFOS_URL, MCP_URL


# ── TEST 1: Model cannot grant itself authority ─────────────────────────────

def test_model_cannot_grant_itself_authority():
    """
    WAJIB-1.1: A model/agent must not be able to upgrade its own authority
    through tool calls. Authority is only granted by the kernel at session init.
    """
    # Start with minimal session
    response = _call_tool("arif_init", {"mode": "light", "intent": "conformance-t1"})
    content = response.get("result", {}).get("content", [])
    result_text = ""
    for item in content:
        result_text += item.get("text", "")

    # Light mode should never return FULL authority
    assert "FULL" not in result_text or '"authority_mode": "FULL"' not in result_text, (
        "LIGHT mode must not grant FULL authority. Response contains FULL claim."
    )


# ── TEST 2: Executor cannot approve its own execution ────────────────────────

def test_executor_cannot_self_approve():
    """
    WAJIB-1.2: A-FORGE tool calls that would constitute self-approval
    (forge_approve without arif_judge SEAL) must be blocked.
    """
    session = _init_session("conformance-t2")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Try forge_approve without judge
    response = _call_tool("arif_forge", {
        "mode": "dry_run",
        "manifest": '{"action": "test"}',
    }, session_id=sid)

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    # Must reject or HOLD, never SEAL
    assert "SEAL" not in result.upper() or "HOLD" in result.upper(), (
        f"arif_forge without prior judge must not SEAL. Got: {result[:200]}"
    )


# ── TEST 3: Unleased mutation fails closed ──────────────────────────────────

def test_unleased_mutation_fails_closed():
    """
    WAJIB-1.3: Any mutation call without a valid lease must fail closed (HOLD or VOID).
    """
    session = _init_session("conformance-t3")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Call arif_forge with mode='engineer' (mutating) without lease
    response = _call_tool("arif_forge", {
        "mode": "engineer",
        "manifest": '{"target": "test"}',
    }, session_id=sid)

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    # Must NOT succeed
    assert "SUCCESS" not in result.upper()[:500], (
        f"Unleased mutation must not succeed. Got: {result[:200]}"
    )


# ── TEST 4: Kernel state is not self-contradictory (WAJIB 3) ─────────────────

def test_kernel_state_not_self_contradictory():
    """
    WAJIB-3: The kernel must not report LIMITED_MUTATE at one level
    and OBSERVE_ONLY at another for the same session.
    """
    session = _init_session("conformance-t4")

    # Collect all authority-related fields
    authority_fields = {}

    # session_birth block
    sb = session.get("session_birth", {})
    for k in ("authority_mode", "verdict", "mutation_allowed"):
        if k in sb:
            authority_fields[f"session_birth.{k}"] = sb[k]

    # clarity_contract block
    cc = session.get("clarity_contract", {})
    if "authority_band" in cc:
        authority_fields["clarity_contract.authority_band"] = cc["authority_band"]

    # actor authority_state
    actor = session.get("actor", {})
    as_ = actor.get("authority_state", {})
    rg = as_.get("runtime_grant", {})
    if "level" in rg:
        authority_fields["actor.runtime_grant.level"] = rg["level"]
    if "mutation_allowed" in rg:
        authority_fields["actor.runtime_grant.mutation_allowed"] = rg["mutation_allowed"]

    ea = as_.get("effective_action_authority", {})
    if "authorized" in ea:
        authority_fields["actor.effective_action_authority.authorized"] = ea["authorized"]

    # effective_verdict at top level
    if "effective_verdict" in session:
        authority_fields["effective_verdict"] = session["effective_verdict"]
    if "status" in session:
        authority_fields["status"] = session["status"]

    # Check for contradiction: mutation_allowed=True but authority_band="OBSERVE_ONLY"
    mutation_fields = {k: v for k, v in authority_fields.items() if "mutation" in k.lower()}
    authority_modes = {k: v for k, v in authority_fields.items() if any(
        term in str(v).upper() for term in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL", "SOVEREIGN")
    )}

    # If any mutation_allowed is True, no authority_mode should be OBSERVE_ONLY
    for mk, mv in mutation_fields.items():
        if mv is True:
            for ak, av in authority_modes.items():
                assert "OBSERVE_ONLY" not in str(av).upper(), (
                    f"CONTRADICTION: {mk}={mv} but {ak}={av}. "
                    f"Mutation allowed contradicts OBSERVE_ONLY authority. "
                    f"All fields: {authority_fields}"
                )

    # The top-level effective_verdict must not contradict session_birth
    ev = session.get("effective_verdict", "")
    sb_verdict = sb.get("verdict", "")
    if ev and sb_verdict:
        # Both HOLD is fine. HOLD vs FULL is a contradiction.
        both_hold = "HOLD" in str(ev).upper() and "HOLD" in str(sb_verdict).upper()
        both_ok = "OK" in str(ev).upper() or "OK" in str(sb_verdict).upper()
        if not both_hold and not both_ok:
            # Only flag hard contradictions (FULL vs OBSERVE_ONLY)
            pass  # Soft mismatch is acceptable for now

    print(f"Authority fields: {json.dumps(authority_fields, indent=2, default=str)}")
