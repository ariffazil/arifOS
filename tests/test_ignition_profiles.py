"""
Tests for X-OS profile ignition (Wave 5)
"""

from arifos_core.system.ignition import IgnitionLoader


def test_profile_match_arif():
    loader = IgnitionLoader()
    p = loader.match_profile("I am Arif.")
    assert p is not None
    assert p.id == "arifOS"
    assert "BM-English" in p.language_mix


def test_profile_match_azwa():
    loader = IgnitionLoader()
    p = loader.match_profile("Saya Azwa.")
    assert p.id == "azwaOS"
    assert p.tone_mode.startswith("gentle")


def test_profile_no_match_returns_none():
    loader = IgnitionLoader()
    p = loader.match_profile("Hello, I am a stranger.")
    # Could be default profile or None depending on your design
    assert p is None or p.id == "defaultOS"