from __future__ import annotations

from arifosmcp.tools.session import _load_model_registry, _resolve_declared_model_key


def test_load_model_registry_maps_tokenrouter_primary() -> None:
    soul, shadow, posture = _load_model_registry("deepseek-reasoner")
    assert soul
    assert isinstance(posture, dict)


def test_load_model_registry_maps_mimo_profiles() -> None:
    soul, shadow, posture = _load_model_registry("mimo-v2.5-pro")
    assert soul
    assert shadow
    assert isinstance(posture, dict)


def test_resolve_declared_model_key_prefers_runtime_defaults(monkeypatch) -> None:
    monkeypatch.delenv("ARIFOS_DEFAULT_MODEL_KEY", raising=False)
    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-reasoner")
    monkeypatch.setenv("MIMO_DEFAULT_MODEL", "mimo-v2.5-pro")
    monkeypatch.delenv("MINIMAX_MODEL", raising=False)

    assert _resolve_declared_model_key(None) == "mimo-v2.5-pro"
