from __future__ import annotations

from arifosmcp.runtime.tools import _arif_session_init, _hold


def test_hold_supports_extra_meta() -> None:
    result = _hold("arif_session_init", "bad mode", extra_meta={"allowed_modes": ["init"]})

    assert result["status"] == "HOLD"
    assert result["meta"]["allowed_modes"] == ["init"]


def test_legacy_modes_are_non_destructive_aliases() -> None:
    discover = _arif_session_init(mode="discover", actor_id="arif")
    status = _arif_session_init(mode="status", actor_id="arif")
    handover = _arif_session_init(mode="handover", actor_id="arif")

    # discover is a pre-session probe; the runtime wrapper now delegates to the
    # canonical session module, which returns a SessionManifest-like receipt.
    assert discover["tool"] == "arif_session_init"
    assert discover["status"] == "OK"
    assert discover["mode"] == "discover"
    assert discover["result"]["kernel"] == "alive"

    # "status" and "handover" are legacy aliases remapped to "validate" / "resume".
    # Without a real session_id these modes correctly HOLD with a migration hint.
    assert status["status"] == "HOLD"
    assert "validate" in status["meta"]["reason"]
    assert handover["status"] == "HOLD"
    assert "resume" in handover["meta"]["reason"]
