"""Regression: ARIFOS_ROOTKEY (canonical) vs ARIF_ROOTKEY (legacy alias)."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import os
import time


def _reload():
    import arifosmcp.core.rootkey as rk
    import arifosmcp.runtime.sovereign_verify as sv

    importlib.reload(rk)
    importlib.reload(sv)
    return rk, sv


def test_get_rootkey_prefers_arifos_name(monkeypatch):
    monkeypatch.delenv("ARIF_ROOTKEY", raising=False)
    monkeypatch.setenv("ARIFOS_ROOTKEY", "canonical-secret-value")
    rk, _ = _reload()
    assert rk.get_rootkey() == "canonical-secret-value"
    assert rk._is_rootkey_configured() is True


def test_get_rootkey_falls_back_to_legacy_arif_name(monkeypatch):
    monkeypatch.delenv("ARIFOS_ROOTKEY", raising=False)
    monkeypatch.setenv("ARIF_ROOTKEY", "legacy-secret-value")
    rk, _ = _reload()
    assert rk.get_rootkey() == "legacy-secret-value"


def test_hmac_verify_reads_arifos_rootkey(monkeypatch):
    monkeypatch.delenv("ARIF_ROOTKEY", raising=False)
    monkeypatch.setenv("ARIFOS_ROOTKEY", "hmac-test-secret")
    _, sv = _reload()
    challenge = f"{int(time.time())}:unit-test"
    sig = hmac.new(b"hmac-test-secret", challenge.encode(), hashlib.sha256).hexdigest()
    ok, reason = sv.verify_hmac_signature("ariffazil", challenge, sig)
    assert ok is True
    assert reason == "hmac_signature_verified"


def test_hmac_fails_closed_when_neither_env_set(monkeypatch):
    monkeypatch.delenv("ARIF_ROOTKEY", raising=False)
    monkeypatch.delenv("ARIFOS_ROOTKEY", raising=False)
    _, sv = _reload()
    ok, reason = sv.verify_hmac_signature(
        "ariffazil", f"{int(time.time())}:x", "abcd"
    )
    assert ok is False
    assert reason == "hmac_rootkey_not_configured"
