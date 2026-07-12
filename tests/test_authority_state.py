"""
Workstream 1 — Canonical Authority Ontology tests.
Tests the compute_authority_state() function and AuthorityState model.
"""

from __future__ import annotations

from arifosmcp.runtime.sct import compute_authority_state
from arifosmcp.schemas.kernel_envelope import AuthorityState, ConstitutionalRole, RuntimeGrantLevel


def test_authority_state_model_exists():
    """Verify the AuthorityState model has all required fields."""
    fields = list(AuthorityState.model_fields.keys())
    assert "identity" in fields
    assert "constitutional_role" in fields
    assert "runtime_grant" in fields
    assert "session" in fields
    assert "effective_action_authority" in fields

    # Verify nested field structure
    state = AuthorityState()
    assert state.identity["claimed_actor_id"] == ""
    assert state.constitutional_role["role"] == "ANONYMOUS"
    assert state.runtime_grant["level"] == "OBSERVE_ONLY"
    assert state.session["bound"] is False
    assert state.effective_action_authority["authorized"] is False


def test_anonymous_observer():
    """Anonymous (unverified) actor gets OBSERVE_ONLY grant."""
    state = compute_authority_state(
        actor_id="",
        actor_verified=False,
        signature_verified=False,
        is_sovereign_principal=False,
        session_id="sess_anon",
        session_bound=True,
        actor_bound=False,
    )
    assert state["constitutional_role"]["role"] == "ANONYMOUS"
    assert state["runtime_grant"]["level"] == "OBSERVE_ONLY"
    assert state["runtime_grant"]["mutation_allowed"] is False
    assert state["runtime_grant"]["seal_allowed"] is False
    assert state["effective_action_authority"]["authorized"] is False
    assert state["effective_action_authority"]["reason_code"] == "identity_not_verified"
    assert state["identity"]["claim_recognized"] is False
    assert state["identity"]["cryptographically_verified"] is False


def test_sovereign_with_crypto():
    """Sovereign with cryptographic proof gets FULL grant + SOVEREIGN role."""
    state = compute_authority_state(
        actor_id="arif",
        actor_verified=True,
        signature_verified=True,
        is_sovereign_principal=True,
        session_id="sess_king",
        session_bound=True,
        actor_bound=True,
        authority_band="FULL",
        verification_method="signature",
        verification_reason="cryptographically_verified",
    )
    assert state["constitutional_role"]["role"] == "SOVEREIGN"
    assert state["runtime_grant"]["level"] == "FULL"
    assert state["runtime_grant"]["mutation_allowed"] is True
    assert state["runtime_grant"]["seal_allowed"] is True
    assert state["effective_action_authority"]["authorized"] is True
    assert state["effective_action_authority"]["reason_code"] == "authorized"
    assert state["identity"]["claim_recognized"] is True
    assert state["identity"]["cryptographically_verified"] is True
    assert state["identity"]["verification_method"] == "signature"


def test_verified_operator():
    """Verified non-sovereign actor gets OPERATOR role + LIMITED_MUTATE grant."""
    state = compute_authority_state(
        actor_id="openclaw",
        actor_verified=True,
        signature_verified=False,
        is_sovereign_principal=False,
        session_id="sess_op",
        session_bound=True,
        actor_bound=True,
        authority_band="LIMITED_MUTATE",
        verification_method="identity_claim",
        verification_reason="identity_claim_accepted",
    )
    assert state["constitutional_role"]["role"] == "OPERATOR"
    assert state["runtime_grant"]["level"] == "LIMITED_MUTATE"
    assert state["runtime_grant"]["mutation_allowed"] is True
    assert state["runtime_grant"]["seal_allowed"] is False  # LIMITED_MUTATE cannot seal
    assert state["effective_action_authority"]["authorized"] is True
    assert state["identity"]["cryptographically_verified"] is False


def test_sovereign_band_normalized_to_full():
    """SOVEREIGN authority band is normalized to FULL grant level."""
    state = compute_authority_state(
        actor_id="arif",
        actor_verified=True,
        signature_verified=True,
        is_sovereign_principal=True,
        session_id="sess_sov",
        session_bound=True,
        actor_bound=True,
        authority_band="SOVEREIGN",
    )
    # SOVEREIGN is a role, not a grant level — normalized to FULL
    assert state["runtime_grant"]["level"] == "FULL"
    assert state["runtime_grant"]["seal_allowed"] is True


def test_no_session_not_bound():
    """Without session binding, effective authority is not authorized."""
    state = compute_authority_state(
        actor_id="arif",
        actor_verified=True,
        signature_verified=True,
        is_sovereign_principal=True,
        session_id="",
        session_bound=False,
        actor_bound=False,
        authority_band="FULL",
    )
    assert state["session"]["bound"] is False
    assert state["effective_action_authority"]["authorized"] is False
    # Session not bound — effective result is no effective authority
    assert state["effective_action_authority"]["reason_code"] in (
        "no_session",
        "actor_not_bound_to_session",
    )


def test_verbs_never_contain_arif_act():
    """allowed_verbs must never leak the internal alias arif_act."""
    for verified in (False, True):
        state = compute_authority_state(
            actor_id="test" if verified else "",
            actor_verified=verified,
            signature_verified=False,
            is_sovereign_principal=False,
            session_id="sess_test",
            session_bound=True,
            actor_bound=verified,
            authority_band="LIMITED_MUTATE" if verified else None,
        )
        verbs = state["runtime_grant"]["allowed_verbs"]
        assert "arif_act" not in verbs, f"arif_act leaked in verbs: {verbs}"
        if verified:
            assert "arif_forge" in verbs


def test_auto_derive_band():
    """When no authority_band provided, derive from identity signals."""
    # Unverified → OBSERVE_ONLY
    s1 = compute_authority_state(
        actor_id="",
        actor_verified=False,
        signature_verified=False,
        is_sovereign_principal=False,
        session_id="s1",
        session_bound=True,
        actor_bound=False,
    )
    assert s1["runtime_grant"]["level"] == "OBSERVE_ONLY"

    # Verified non-sovereign → LIMITED_MUTATE
    s2 = compute_authority_state(
        actor_id="agent",
        actor_verified=True,
        signature_verified=False,
        is_sovereign_principal=False,
        session_id="s2",
        session_bound=True,
        actor_bound=True,
    )
    assert s2["runtime_grant"]["level"] == "LIMITED_MUTATE"

    # Sovereign with signature → FULL
    s3 = compute_authority_state(
        actor_id="arif",
        actor_verified=True,
        signature_verified=True,
        is_sovereign_principal=True,
        session_id="s3",
        session_bound=True,
        actor_bound=True,
    )
    assert s3["runtime_grant"]["level"] == "FULL"
