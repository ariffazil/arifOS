from __future__ import annotations

import importlib
import warnings


def test_file_secret_is_loaded_without_ephemeral_warning(monkeypatch, tmp_path):
    secret_file = tmp_path / "governance.secret"
    secret_file.write_text("file-backed-secret", encoding="utf-8")

    monkeypatch.delenv("ARIFOS_GOVERNANCE_OPEN_MODE", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_SECRET", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_TOKEN_SECRET", raising=False)
    monkeypatch.setenv("ARIFOS_GOVERNANCE_SECRET_FILE", str(secret_file))

    with warnings.catch_warnings(record=True) as caught:
        import core.enforcement.auth_continuity as auth_continuity

        reloaded = importlib.reload(auth_continuity)

    assert reloaded._GOVERNANCE_TOKEN_SECRET == "file-backed-secret"
    assert not any("ephemeral secret" in str(w.message) for w in caught)


def test_previous_file_secret_is_accepted_for_verification(monkeypatch, tmp_path):
    current_file = tmp_path / "governance.current"
    previous_file = tmp_path / "governance.previous"
    current_file.write_text("current-secret", encoding="utf-8")
    previous_file.write_text("previous-secret", encoding="utf-8")

    monkeypatch.delenv("ARIFOS_GOVERNANCE_OPEN_MODE", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_SECRET", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_TOKEN_SECRET", raising=False)
    monkeypatch.setenv("ARIFOS_GOVERNANCE_SECRET_FILE", str(current_file))
    monkeypatch.setenv("ARIFOS_GOVERNANCE_SECRET_PREVIOUS_FILE", str(previous_file))

    import core.enforcement.auth_continuity as auth_continuity

    reloaded = importlib.reload(auth_continuity)
    unsigned_context = {
        "session_id": "sess-1",
        "actor_id": "actor-1",
        "authority_level": "user",
        "token_fingerprint": "fp-1",
        "nonce": "nonce-1",
        "iat": 1,
        "exp": 4102444800,
        "approval_scope": ["seal_vault"],
        "parent_signature": "parent-1",
    }
    old_signature = reloaded._sign_auth_context_with_secret(
        unsigned_context, reloaded._GOVERNANCE_TOKEN_SECRET_PREVIOUS
    )
    auth_context = {**unsigned_context, "signature": old_signature}

    ok, reason = reloaded.verify_auth_context("sess-1", auth_context)

    assert ok is True
    assert reason == ""
