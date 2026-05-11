from __future__ import annotations

import importlib
import warnings


def test_open_mode_uses_fixed_public_governance_secret(monkeypatch):
    monkeypatch.setenv("ARIFOS_GOVERNANCE_OPEN_MODE", "1")
    monkeypatch.delenv("ARIFOS_GOVERNANCE_SECRET", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_TOKEN_SECRET", raising=False)

    with warnings.catch_warnings(record=True) as caught:
        import core.enforcement.auth_continuity as auth_continuity

        reloaded = importlib.reload(auth_continuity)

    assert reloaded._GOVERNANCE_TOKEN_SECRET == "arifos-open-governance-dev-mode"
    assert not any("ephemeral secret" in str(w.message) for w in caught)
