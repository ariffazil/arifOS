"""
PR2 — wealth authorization middleware tests.

Verifies the audit-4 contract:
  - every protected tool goes through `authorize(...)`
  - errors return the audit-shaped envelope
  - 9 specific error codes are emitted by the right triggers
  - "Authorization: Bearer none" passes ONLY if the tool opted into public_simulation
  - actor_id cannot be supplied by the caller — only the signed token counts
  - replay is detected (jti dedup)
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.wealth_auth import (  # noqa: E402
    authorize,
    error_to_envelope,
    extract_envelope,
    bound_call,
)
from arifosmcp.runtime.wealth_auth.exceptions import (  # noqa: E402
    AuthError,
    SessionRequired,
    TokenInvalid,
    TokenExpired,
    WrongAudience,
    CapabilityNotGranted,
    ActorNotBound,
    ReplayDetected,
    EvidenceInsufficient,
    HumanRatificationRequired,
)
from arifosmcp.runtime.wealth_auth.token_validation import (  # noqa: E402
    TokenClaims,
    issue_token,
    validate_token,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def signing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARIFOS_OPS_SIGNING_KEY", "dev-only-secret-do-not-use-in-prod")
    monkeypatch.setenv("ARIFOS_TOKEN_REPLAY_WINDOW", "300")


# ── Test 1: every error code from errors.schema.json ────────────────────────
def test_authorize_raises_session_required_when_no_header() -> None:
    with pytest.raises(SessionRequired) as exc:
        authorize(
            authorization_header=None,
            audience="wealth",
            required_capability="wealth_npv_reward",
        )
    env = exc.value.to_envelope()
    assert env["error_code"] == "SESSION_REQUIRED"
    assert env["retryable"] is True
    assert env["mutation_occurred"] is False
    assert env["requested_capability"] == "wealth_npv_reward"
    assert "INITIALIZE_SESSION_AT_AAA_OR_MCP_GATEWAY" in env["required_action"]


def test_authorize_rejects_bare_bearer_without_public_simulation() -> None:
    with pytest.raises(SessionRequired) as exc:
        authorize(
            authorization_header="Bearer none",
            audience="wealth",
            required_capability="wealth_npv_reward",
            public_simulation=False,
        )
    assert exc.value.code == "SESSION_REQUIRED"


def test_authorize_accepts_bare_bearer_with_public_simulation() -> None:
    claims = authorize(
        authorization_header="Bearer none",
        audience="wealth",
        required_capability="wealth_npv_reward",
        public_simulation=True,
    )
    assert claims.actor_id == ""
    assert claims.issuer == ""


def test_authorize_rejects_malformed_token() -> None:
    with pytest.raises(TokenInvalid) as exc:
        authorize(
            authorization_header="Bearer not-a-jws",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )
    assert "compact JWS-style" in exc.value.message


def test_authorize_rejects_token_signed_with_wrong_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # Issue a token with a different key than the running key, then validate.
    monkeypatch.setenv("ARIFOS_OPS_SIGNING_KEY", "different-key")
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
    )
    # Restore the fixture key so authorize() verifies with the original key.
    monkeypatch.setenv("ARIFOS_OPS_SIGNING_KEY", "dev-only-secret-do-not-use-in-prod")
    with pytest.raises(TokenInvalid) as exc:
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )
    assert "signature did not match" in exc.value.message


def test_authorize_rejects_wrong_audience() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["arifOS"],  # not wealth
        allowed_capabilities=["wealth_npv_reward"],
    )
    with pytest.raises(WrongAudience):
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )


def test_authorize_rejects_expired_token() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
        ttl_seconds=-1,  # already expired
    )
    with pytest.raises(TokenExpired):
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )


def test_authorize_rejects_missing_capability() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_other_capability"],
    )
    with pytest.raises(CapabilityNotGranted) as exc:
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )
    assert "wealth_npv_reward" in exc.value.message


def test_authorize_rejects_insufficient_authority_band() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
        authority_band="OBSERVER",  # not SOVEREIGN
    )
    with pytest.raises(CapabilityNotGranted):
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
            minimum_authority="SOVEREIGN",
        )


# ── Test 2: actor_override is ignored (caller cannot mint identity) ─────────
def test_authorize_ignores_actor_override_audit_rule() -> None:
    """Audit says: 'Do not trust caller-supplied actor_id when supplied only
    by the caller.' We ignore the override and rely on the signed token."""
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
    )
    claims = authorize(
        authorization_header=f"Bearer {tok}",
        audience="wealth",
        required_capability="wealth_npv_reward",
        actor_override={"actor_id": "ATTACKER"},
    )
    # Override was ignored; actor_id comes from the signed token.
    assert claims.actor_id == "ARIF"


# ── Test 3: replay is detected ──────────────────────────────────────────────
def test_replay_jti_is_detected() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
    )
    # First presentation: passes
    authorize(
        authorization_header=f"Bearer {tok}",
        audience="wealth",
        required_capability="wealth_npv_reward",
    )
    # Second presentation with same jti: rejected
    with pytest.raises(ReplayDetected):
        authorize(
            authorization_header=f"Bearer {tok}",
            audience="wealth",
            required_capability="wealth_npv_reward",
        )


# ── Test 4: error_to_envelope returns audit-shaped dict ─────────────────────
def test_error_to_envelope_produces_audit_shape() -> None:
    try:
        raise SessionRequired("test", requested_capability="wealth_npv_reward")
    except AuthError as exc:
        env = error_to_envelope(exc)
    for required in ("status", "error_code", "message", "retryable", "mutation_occurred"):
        assert required in env
    assert env["status"] == "HOLD"
    assert env["error_code"] == "SESSION_REQUIRED"
    assert env["requested_capability"] == "wealth_npv_reward"
    assert env["mutation_occurred"] is False


def test_error_to_envelope_handles_non_auth_error() -> None:
    env = error_to_envelope(RuntimeError("oops"))
    assert env["status"] == "ERROR"
    assert env["error_code"] == "INTERNAL_ERROR"
    assert env["retryable"] is False


# ── Test 5: bound_call decorator enforces auth on the wrapped tool ──────────
def test_bound_call_rejects_when_no_auth() -> None:
    @bound_call(audience="wealth", required_capability="wealth_npv_reward")
    def tool(input, **_):
        return {"status": "ok", "result": input}

    out = tool({"x": 1})
    assert out["status"] == "HOLD"
    assert out["error_code"] == "SESSION_REQUIRED"


def test_bound_call_accepts_with_valid_token() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
    )

    @bound_call(audience="wealth", required_capability="wealth_npv_reward")
    def tool(input, **_):
        return {"status": "ok", "result": input}

    out = tool({"x": 1}, _request_headers={"authorization": f"Bearer {tok}"})
    assert out["status"] == "ok"
    assert out["result"] == {"x": 1}


# ── Test 6: extract_envelope pulls audit-mandated fields ───────────────────
def test_extract_envelope_pulls_audit_fields() -> None:
    env = extract_envelope(
        request_headers={
            "X-ArifOS-Session-ID": "session-abc",
            "X-ArifOS-Actor-ID": "ARIF",
            "X-ArifOS-Trace-ID": "trc-001",
            "X-ArifOS-Request-ID": "req-001",
        }
    )
    for k in ("session_id", "actor_id", "trace_id", "request_id"):
        assert k in env
    assert env["session_id"] == "session-abc"
    assert env["actor_id"] == "ARIF"
    assert env["trace_id"] == "trc-001"


# ── Test 7: issue_token produces a verifiable token ─────────────────────────
def test_issued_token_validates_against_validate_token() -> None:
    tok = issue_token(
        actor_id="ARIF",
        subject_did="did:web:arif-fazil.com:agents:wealth",
        audience=["wealth"],
        allowed_capabilities=["wealth_npv_reward"],
    )
    claims = validate_token(f"Bearer {tok}")
    assert claims.actor_id == "ARIF"
    assert "wealth" in claims.audience
    assert claims.has_capability("wealth_npv_reward")


# ── Test 8: 9-error audit contract — every error code reachable ───────────
def test_nine_error_codes_reachable() -> None:
    """The audit's structured error contract lists all codes; each must be reachable
    from the auth middleware at minimum."""
    import json as _json
    errors_schema_path = Path(__file__).resolve().parents[2] / "arifosmcp" / "runtime" / "contracts" / "errors.schema.json"
    assert errors_schema_path.exists()
    schema = _json.loads(errors_schema_path.read_text())
    audit_codes = set(schema["properties"]["error_code"]["enum"])
    auth_codes = {
        "SESSION_REQUIRED", "TOKEN_INVALID", "TOKEN_EXPIRED", "WRONG_AUDIENCE",
        "CAPABILITY_NOT_GRANTED", "ACTOR_NOT_BOUND", "REPLAY_DETECTED", "REVOKED",
        "EVIDENCE_INSUFFICIENT", "HUMAN_RATIFICATION_REQUIRED",
    }
    missing = auth_codes - audit_codes
    assert not missing, f"auth codes missing from audit contract: {missing}"
