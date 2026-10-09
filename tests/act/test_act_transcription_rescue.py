"""Regression: ACT transcription-rescue fallback (2026-09-12).

Root cause (live-proven 2026-09-12, FI-003 session SEAL-44e5822e01814e9c):
ACT tokens relayed through agent context windows corrupt single characters;
HMAC correctly rejects them, but the hard deny obscured that the no-token
path grants identical session-store authority. Contract pinned here:

- corrupted token + valid store session  -> PASS with _act_relay_rescue stamp
- corrupted token + unknown session       -> HOLD TOKEN_INVALID + forensic fields
- valid token                             -> PASS, no rescue stamp
"""

import os
import time

os.environ.setdefault("ARIFOS_SESSION_SECRET", "test-secret-transcription-rescue")

from arifosmcp.runtime import act_token as at  # noqa: E402
from arifosmcp.runtime.tools import _SESSIONS, verify_and_inject_token  # noqa: E402

SID = "SEAL-TEST-TR-001"
ACTOR = "qwen-code/FI-003"


def _seed_store() -> str:
    token, _claims = at.mint_act(
        sid=SID, actor=ACTOR, auth="OBSERVE_ONLY", av=False,
        allowed=["arif_init", "arif_observe", "arif_think"],
    )
    _SESSIONS[SID] = {
        "session_id": SID,
        "actor_id": ACTOR,
        "created_at": "2026-09-12T00:00:00Z",
        "created_at_unix": time.time() - 60,
        "expires_at_unix": time.time() + 3600,
        "stage": "000",
        "lane": "AGI",
        "authority": "OBSERVE_ONLY",
        "allowed_next_verbs": ["arif_init", "arif_observe", "arif_think"],
    }
    return token


def _corrupt(token: str) -> str:
    flip = "0" if token[-1] != "0" else "1"
    return token[:-1] + flip


def setup_function(_fn):
    _SESSIONS.pop(SID, None)


def teardown_function(_fn):
    _SESSIONS.pop(SID, None)


def test_corrupted_token_with_valid_store_rescues():
    token = _seed_store()
    bad = _corrupt(token)
    kwargs = {"session_token": bad, "session_id": SID, "actor_id": ACTOR}
    ok, err, claims = verify_and_inject_token(kwargs, "arif_observe")
    assert ok is True, f"expected rescue pass, got deny: {err and err.get('reason_code')}"
    assert kwargs.get("_act_relay_rescue") is True
    assert claims and claims.get("actor") == ACTOR


def test_corrupted_token_unknown_session_denies_with_forensics():
    token = _seed_store()
    bad = _corrupt(token)
    kwargs = {"session_token": bad, "session_id": "SEAL-NOPE-404", "actor_id": ACTOR}
    ok, err, _claims = verify_and_inject_token(kwargs, "arif_observe")
    assert ok is False
    assert err["reason_code"] == "TOKEN_INVALID"
    sesat = err["sesat_event"]
    assert sesat["token_len"] == len(bad)
    assert isinstance(sesat["token_sha8"], str) and len(sesat["token_sha8"]) == 8
    assert kwargs.get("_act_relay_rescue") is None


def test_valid_token_passes_without_rescue():
    token = _seed_store()
    kwargs = {"session_token": token, "session_id": SID, "actor_id": ACTOR}
    ok, err, claims = verify_and_inject_token(kwargs, "arif_observe")
    assert ok is True, f"expected pass, got: {err and err.get('reason_code')}"
    assert kwargs.get("_act_relay_rescue") is None
    assert claims and claims.get("sid") == SID
