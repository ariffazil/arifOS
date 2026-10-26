"""F11 egress mask — a session capability token must not ride out in a tool result.

Witnessed 2026-10-26: arif_memory and arif_route both returned the caller's full
``act_v1.<claims>.<sig>`` at top level and nested under ``result``. The plugin
masks it (``act_v1.<redacted>``); the kernel did not. A bearer credential in a
transcript or artifact has an 8h blast radius.

Contract under test:
  * a minting verb (arif_init) returns the raw token exactly once — that is how a
    client obtains it;
  * every other response carries a deterministic handle, at any nesting depth;
  * masking is idempotent and never raises;
  * ARIFOS_SCT_ECHO=raw restores the legacy echo (escape hatch, not the default).
"""

from __future__ import annotations

import hashlib
import os

import pytest

from arifosmcp.runtime.tools import _mask_sct, _mask_sct_egress

RAW = "act_v1.eyJhdXRoIjoiTElNSVRFRF9NVVRBVEUifQ.c2lnbmF0dXJl"


def _digest(tok: str) -> str:
    return hashlib.sha256(tok.encode()).hexdigest()[:12]


@pytest.fixture(autouse=True)
def _default_mode(monkeypatch):
    monkeypatch.delenv("ARIFOS_SCT_ECHO", raising=False)
    yield


def test_masks_top_level_and_nested():
    resp = {
        "status": "completed",
        "session_token": RAW,
        "result": {"session_token": RAW, "inner": {"sct": RAW}, "rows": [{"sct_token": RAW}]},
    }
    out = _mask_sct_egress(resp, "arif_route")
    handle = f"act_v1.<redacted:sha256:{_digest(RAW)}>"

    assert out["session_token"] == handle
    assert out["result"]["session_token"] == handle
    assert out["result"]["inner"]["sct"] == handle
    assert out["result"]["rows"][0]["sct_token"] == handle
    # the credential itself is nowhere in the serialised response
    assert RAW not in str(out)


def test_mint_verb_is_exempt():
    out = _mask_sct_egress({"session_token": RAW}, "arif_init")
    assert out["session_token"] == RAW


def test_mask_is_idempotent_and_deterministic():
    once = _mask_sct(RAW)
    twice = _mask_sct(once)
    assert once == twice
    assert once == _mask_sct(RAW)
    # prefix survives (so consumers can still recognise a token), payload and
    # signature do not — the handle is strictly shorter than the credential.
    assert once.startswith("act_v1.")
    assert len(once) < len(RAW)


@pytest.mark.parametrize("value", [None, "", 123, [], {}, b"bytes"])
def test_masking_never_raises(value):
    assert _mask_sct(value) == value
    assert _mask_sct_egress(value, "arif_route") == value


def test_raw_escape_hatch(monkeypatch):
    monkeypatch.setenv("ARIFOS_SCT_ECHO", "raw")
    out = _mask_sct_egress({"session_token": RAW}, "arif_route")
    assert out["session_token"] == RAW


def test_falsifier_legacy_echo_is_caught():
    """If the mask is removed, this test must fail — that is its whole job."""
    legacy = {"session_token": RAW}
    masked = _mask_sct_egress(dict(legacy), "arif_memory")
    assert masked["session_token"] != legacy["session_token"]


def test_unknown_echo_mode_fails_closed(monkeypatch):
    """A typo in the env var must not silently disable the mask."""
    monkeypatch.setenv("ARIFOS_SCT_ECHO", "raww")
    out = _mask_sct_egress({"session_token": RAW}, "arif_route")
    assert RAW not in str(out)
