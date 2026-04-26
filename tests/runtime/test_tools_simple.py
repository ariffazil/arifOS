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

    assert discover["tool"] == "arif_ping"
    assert discover["status"] == "OK"
    assert status["status"] == "HOLD"
    assert "validate" in status["meta"]["reason"]
    assert handover["status"] == "HOLD"
    assert "resume" in handover["meta"]["reason"]
