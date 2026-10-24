"""VAULT999-SIG enforce-default tests (F13 order 2026-10-24, Arif).

Directive: without a signing key, append must be REJECTED — never written
unsigned. _sig_enforce() defaults ON; explicit env opt-out stays possible
for documented mirroring flows.
"""

import importlib
import json
import os

import pytest


@pytest.fixture()
def clean_env(monkeypatch, tmp_path):
    """No key, no explicit enforce flag, isolated vault dir."""
    monkeypatch.delenv("ARIFOS_VAULT_HMAC_KEY", raising=False)
    monkeypatch.delenv("ARIFOS_VAULT_HMAC_KEY_FILE", raising=False)
    monkeypatch.delenv("ARIFOS_VAULT_SIG_ENFORCE", raising=False)
    monkeypatch.setenv("ARIFOS_CANONICAL_VAULT_DIR", str(tmp_path / "vault"))
    import arifosmcp.runtime.canonical_vault_chain as cvc

    importlib.reload(cvc)
    return cvc


def test_sig_enforce_defaults_on(clean_env):
    """F13 2026-10-24: unset env means ENFORCED (fail-closed), not silent."""
    assert clean_env._sig_enforce() is True


def test_sig_enforce_explicit_opt_out(clean_env, monkeypatch):
    monkeypatch.setenv("ARIFOS_VAULT_SIG_ENFORCE", "0")
    assert clean_env._sig_enforce() is False


def test_append_without_key_is_rejected(clean_env):
    """Without a key, append is refused — no unsigned row ever lands."""
    r = clean_env.append_receipt(
        actor_id="test-actor",
        tool_name="test",
        input_hash="sha256:" + "0" * 64,
        result_hash="sha256:" + "1" * 64,
        authority_state="SOVEREIGN_RATIFIED",
        verdict="SEAL",
        reversibility="IRREVERSIBLE",
        idempotency_key="sigtest-reject-1",
    )
    assert r.ok is False
    assert r.failure_class == "SIG_ENFORCE_NO_KEY"
    assert r.receipt is None
    # and nothing was written to the chain
    chain = clean_env.paths_for(None).chain
    assert not chain.exists() or chain.read_text().strip() == ""


def test_append_with_key_signs_row(clean_env, monkeypatch, tmp_path):
    keyfile = tmp_path / "k.key"
    keyfile.write_text("test-hmac-secret-0123456789abcdef")
    monkeypatch.setenv("ARIFOS_VAULT_HMAC_KEY_FILE", str(keyfile))
    r = clean_env.append_receipt(
        actor_id="test-actor",
        tool_name="test",
        input_hash="sha256:" + "2" * 64,
        result_hash="sha256:" + "3" * 64,
        authority_state="SOVEREIGN_RATIFIED",
        verdict="SEAL",
        reversibility="IRREVERSIBLE",
        idempotency_key="sigtest-signed-1",
    )
    assert r.ok is True
    entry = r.receipt
    assert entry.get("sig_method") == "hmac-sha256"
    assert entry.get("sig_key_id") == clean_env.SIG_KEY_ID
    assert clean_env._verify_receipt_signature(
        entry["receipt_hash"], entry["signature"], keyfile.read_bytes().strip()
    )
