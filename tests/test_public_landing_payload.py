"""
tests/test_public_landing_payload.py — Public surface contract tests.

Updated 2026-07-08: _public_landing_payload was removed during ZEN-9 consolidation.
Tests now verify CANONICAL_12 (the actual public surface) and public_tool_names_for_mode.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.public_surface import CANONICAL_9, CANONICAL_12, public_tool_names_for_mode


def test_canonical_12_has_12_tools():
    """The canonical public surface is exactly 12 tools."""
    assert len(CANONICAL_12) == 12
    assert all(name.startswith("arif_") for name in CANONICAL_12)


def test_canonical_9_is_deprecated_alias():
    """CANONICAL_9 is a deprecated alias for CANONICAL_12."""
    assert CANONICAL_9 == CANONICAL_12


def test_public_tool_names_returns_canonical():
    """public_tool_names_for_mode(None) returns the canonical surface."""
    names = public_tool_names_for_mode(None)
    assert len(names) >= 9
    assert all(name.startswith("arif_") for name in names)
