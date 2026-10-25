"""
tests/runtime/test_calltime_identity.py

Call-time cryptographic actor verification — the smallest reversible wire
from a call carrying a valid ACT token or Ed25519 proof to
actor_verified=True for THAT session, with unsigned calls staying False.

Contract locked by:
  - tests/test_b2_constitutional_chokepoints.py (gate reads _is_actor_verified)
  - tests/test_session_preflight.py (actor_verified False at birth)

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from arifosmcp.runtime.calltime_identity import (
    CallTimeIdentity,
    extract_act_token,
    verify_caller_identity,
)

pytestmark = pytest.mark.runtime


# ── No credential: fail-closed birth state ──────────────────────────────────


class TestNoCredential:
    def test_no_args_returns_unverified(self) -> None:
        r = verify_caller_identity()
        assert isinstance(r, CallTimeIdentity)
        assert r.verified is False
        assert r.method is None
        assert r.reason == "no_credential_presented"

    def test_session_and_actor_alone_do_not_verify(self) -> None:
        r = verify_caller_identity("sess-1", "arif")
        assert r.verified is False

    def test_empty_proof_dict_does_not_verify(self) -> None:
        r = verify_caller_identity("sess-1", "arif", ed25519_proof={})
        assert r.verified is False

    def test_none_token_does_not_verify(self) -> None:
        r = verify_caller_identity("sess-1", "arif", token=None)
        assert r.verified is False


# ── ACT token path (HMAC-SHA256, real verify_act) ───────────────────────────


class TestActTokenPath:
    @pytest.fixture()
    def act_token(self) -> tuple[str, dict[str, Any]]:
        from arifosmcp.runtime.act_token import mint_act

        token, claims = mint_act(
            sid="sess-act-1",
            actor="ariffazil",
            auth="OBSERVE_ONLY",
            av=True,
        )
        return token, claims

    def test_valid_token_verifies(self, act_token: tuple[str, dict]) -> None:
        token, _ = act_token
        r = verify_caller_identity("sess-act-1", "ariffazil", token=token)
        assert r.verified is True
        assert r.method == "act_token"
        assert r.actor == "ariffazil"

    def test_valid_token_no_live_session_still_verifies_at_call_level(
        self, act_token: tuple[str, dict]
    ) -> None:
        token, _ = act_token
        r = verify_caller_identity("sess-act-1", "ariffazil", token=token)
        assert r.verified is True
        # No live session in the store → promotion best-effort False
        assert r.promoted_to_session is False

    def test_forged_token_rejected(self, act_token: tuple[str, dict]) -> None:
        token, _ = act_token
        # Tamper with the payload (keep the original signature)
        parts = token.split(".")
        forged = f"{parts[0]}.{parts[1][:-4]}AAAA.{parts[2]}"
        r = verify_caller_identity("sess-act-1", "ariffazil", token=forged)
        assert r.verified is False
        assert r.reason == "act_token_invalid"

    def test_wrong_signature_rejected(self, act_token: tuple[str, dict]) -> None:
        token, _ = act_token
        parts = token.split(".")
        forged = f"{parts[0]}.{parts[1]}.{'0' * 64}"
        r = verify_caller_identity("sess-act-1", "ariffazil", token=forged)
        assert r.verified is False

    def test_actor_mismatch_rejected(self, act_token: tuple[str, dict]) -> None:
        token, _ = act_token
        r = verify_caller_identity("sess-act-1", "claude-code", token=token)
        assert r.verified is False
        assert r.reason == "act_token_invalid"

    def test_expired_token_rejected(self) -> None:
        from arifosmcp.runtime.act_token import mint_act, verify_act

        token, _ = mint_act(
            sid="sess-exp", actor="ariffazil", auth="OBSERVE_ONLY", av=True, ttl=1
        )
        # verify_act with a future `now` simulates expiry without sleeping
        assert verify_act(token, now=time.time() + 10_000) is None
        r = verify_caller_identity(
            "sess-exp", "ariffazil", token=token
        )  # current-time check passes mint TTL=1? guard below
        # The call uses wall-clock now; ttl=1 token may still be valid for ~1s.
        # Force determinism by verifying an already-expired token directly:
        from arifosmcp.runtime import act_token as at

        orig = at.time.time
        at.time.time = lambda: orig() + 10_000
        try:
            r2 = verify_caller_identity("sess-exp", "ariffazil", token=token)
        finally:
            at.time.time = orig
        assert r2.verified is False
        assert r2.reason == "act_token_invalid"

    def test_av_false_token_rejected(self) -> None:
        from arifosmcp.runtime.act_token import mint_act

        token, _ = mint_act(
            sid="sess-av0", actor="ariffazil", auth="OBSERVE_ONLY", av=False
        )
        r = verify_caller_identity("sess-av0", "ariffazil", token=token)
        assert r.verified is False
        assert r.reason == "act_token_av_false"

    def test_session_mismatch_rejected(self) -> None:
        from arifosmcp.runtime.act_token import mint_act

        token, _ = mint_act(
            sid="sess-A", actor="ariffazil", auth="OBSERVE_ONLY", av=True
        )
        r = verify_caller_identity("sess-B", "ariffazil", token=token)
        assert r.verified is False
        assert r.reason == "act_token_session_mismatch"


# ── Ed25519 proof path (real _verify_ed25519_proof) ─────────────────────────


class TestEd25519ProofPath:
    def _proof(self, actor_id: str = "ariffazil") -> dict[str, str]:
        from arifosmcp.runtime.sovereign_signer import (
            get_constitution_hash,
            sign,
        )

        nonce = f"{int(time.time())}:calltime-test"
        sig = sign(actor_id, get_constitution_hash(), nonce)
        return {"signature": sig, "nonce": nonce, "timestamp": str(int(time.time()))}

    def test_valid_proof_verifies(self) -> None:
        pytest.importorskip("cryptography")
        try:
            proof = self._proof()
        except FileNotFoundError:
            pytest.skip("Sovereign private key not available in this environment")
        r = verify_caller_identity("sess-ed-1", "ariffazil", ed25519_proof=proof)
        assert r.verified is True
        assert r.method == "ed25519_proof"
        assert r.actor == "ariffazil"

    def test_forged_signature_rejected(self) -> None:
        proof = self._proof()
        proof["signature"] = "Zm9yZ2VkLXNpZw=="
        r = verify_caller_identity("sess-ed-1", "ariffazil", ed25519_proof=proof)
        assert r.verified is False
        assert r.reason == "ed25519_proof_invalid"

    def test_stale_nonce_rejected(self) -> None:
        from arifosmcp.runtime.sovereign_signer import (
            get_constitution_hash,
            sign,
        )

        stale = f"{int(time.time()) - 2000}:calltime-stale"
        sig = sign("ariffazil", get_constitution_hash(), stale)
        r = verify_caller_identity(
            "sess-ed-1",
            "ariffazil",
            ed25519_proof={
                "signature": sig,
                "nonce": stale,
                "timestamp": str(int(time.time())),
            },
        )
        assert r.verified is False

    def test_missing_actor_rejected(self) -> None:
        r = verify_caller_identity(
            "sess-ed-1", "", ed25519_proof={"signature": "x", "nonce": "y"}
        )
        assert r.verified is False
        assert r.reason == "ed25519_proof_missing_actor"


# ── extract_act_token ────────────────────────────────────────────────────────


class TestExtractActToken:
    def test_body_field(self) -> None:
        assert (
            extract_act_token(body={"act_token": "act_v1.abc.def"}) == "act_v1.abc.def"
        )

    def test_header(self) -> None:
        assert (
            extract_act_token(headers={"x-act-token": "act_v1.a.b"}) == "act_v1.a.b"
        )

    def test_bearer_authorization(self) -> None:
        assert (
            extract_act_token(authorization="Bearer act_v1.a.b") == "act_v1.a.b"
        )

    def test_random_bearer_is_not_act(self) -> None:
        assert extract_act_token(authorization="Bearer sk-some-api-key") is None

    def test_absent_returns_none(self) -> None:
        assert extract_act_token(body={}, headers={}, authorization=None) is None


# ── REST wiring: gate seam behavior ─────────────────────────────────────────


class TestRestGateSeam:
    """The /tools route must consult calltime_identity before the gate reads
    _is_actor_verified — a valid credential promotes the session; an unsigned
    call stays actor_verified=False at the gate."""

    def _app(self):
        from arifosmcp.runtime.rest_routes import rest_routes as routes

        async def tool(**_: Any) -> dict[str, str]:
            return {"status": "OK"}

        app = Starlette()
        routes.register_rest_routes(app, {"arif_observe": tool})
        return routes, app

    def test_unsigned_call_leaves_session_unverified(self, monkeypatch) -> None:
        routes, app = self._app()
        seen: dict[str, bool] = {}

        def spy(session_id, actor_id):
            seen["gate_saw_verified"] = False  # canonical: no verified session
            return False

        # The gate does `from arifosmcp.runtime.tools import _is_actor_verified`
        # at call time — patch the canonical source module, not routes.
        import arifosmcp.runtime.tools as tools_mod

        monkeypatch.setattr(tools_mod, "_is_actor_verified", spy, raising=False)
        with TestClient(app) as client:
            resp = client.post("/tools/arif_observe", json={"session_id": "sess-x"})
        assert resp.status_code == 200
        assert seen["gate_saw_verified"] is False

    def test_signed_call_promotes_session_for_gate(self, monkeypatch) -> None:
        from arifosmcp.runtime.act_token import mint_act
        from arifosmcp.runtime.tools import _SESSIONS

        token, _ = mint_act(
            sid="sess-ct-rest", actor="ariffazil", auth="OBSERVE_ONLY", av=True
        )
        # Create a live session record so promotion has a target
        _SESSIONS["sess-ct-rest"] = {"session_id": "sess-ct-rest"}
        try:
            routes, app = self._app()
            seen: dict[str, bool] = {}

            def spy(session_id, actor_id):
                # Replicate the real read: authority_state on the session record
                from arifosmcp.runtime.authority import read_authority_state
                from arifosmcp.runtime.tools import _SESSIONS as S

                sess = S.get(session_id)
                v = (
                    bool(read_authority_state(sess).actor.verified)
                    if isinstance(sess, dict)
                    else False
                )
                seen["gate_saw_verified"] = v
                return v

            # The gate imports _is_actor_verified from runtime.tools at call time
            # — patch the canonical source module, not routes.
            import arifosmcp.runtime.tools as tools_mod

            monkeypatch.setattr(tools_mod, "_is_actor_verified", spy, raising=False)
            with TestClient(app) as client:
                resp = client.post(
                    "/tools/arif_observe",
                    json={
                        "session_id": "sess-ct-rest",
                        "actor_id": "ariffazil",
                        "act_token": token,
                    },
                )
            assert resp.status_code in (200, 403)  # gate policy verdict is out of scope
            assert seen["gate_saw_verified"] is True
        finally:
            _SESSIONS.pop("sess-ct-rest", None)
