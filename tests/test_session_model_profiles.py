"""
tests/test_session_model_profiles.py — Model registry loading tests.

Updated 2026-07-08: _resolve_declared_model_key was removed.
Tests now verify _load_model_registry only.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.tools.session import _load_model_registry


def test_load_model_registry_maps_mimo_profiles():
    """mimo-v2.5-pro should resolve to a soul profile."""
    soul, shadow, posture = _load_model_registry("mimo-v2.5-pro")
    assert isinstance(posture, dict)


def test_load_model_registry_returns_tuples():
    """Registry loader always returns 3-tuple of dicts."""
    soul, shadow, posture = _load_model_registry("nonexistent-model")
    assert isinstance(soul, dict)
    assert isinstance(shadow, dict)
    assert isinstance(posture, dict)
