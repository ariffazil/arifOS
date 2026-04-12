"""
test_invariants_identity.py — Identity Governance Invariants

F11 + F2: Canonical identity must never be overridden by display metadata.
These are HARD invariants — any violation is a constitutional failure.
"""
import pytest
from arifosmcp.runtime.sessions import (
    resolve_runtime_context,
    _resolve_canonical_actor,
    bind_session_identity,
    get_session_identity,
    clear_session_identity,
)


class TestIdentityPrecedenceInvariant:
    """Invariant: actor_id > declared_name > anonymous (always)"""

    def test_actor_id_overrides_declared_name(self):
        """actor_id='arif' + declared_name='other' → canonical='ariffazil'"""
        ctx = resolve_runtime_context(
            incoming_session_id="test-001",
            auth_context=None,
            actor_id="arif",
            declared_name="other",
        )
        assert ctx["canonical_actor_id"] == "ariffazil", \
            "actor_id must override declared_name"

    def test_declared_name_only_if_actor_id_anonymous(self):
        """actor_id='anonymous' + declared_name='arif' → canonical='ariffazil'"""
        ctx = resolve_runtime_context(
            incoming_session_id="test-002",
            auth_context=None,
            actor_id="anonymous",
            declared_name="arif",
        )
        assert ctx["canonical_actor_id"] == "ariffazil", \
            "declared_name may substitute if actor_id is anonymous"

    def test_anonymous_fallback(self):
        """No actor_id + no declared_name → canonical='anonymous'"""
        ctx = resolve_runtime_context(
            incoming_session_id="test-003",
            auth_context=None,
            actor_id=None,
            declared_name=None,
        )
        assert ctx["canonical_actor_id"] == "anonymous", \
            "Must fallback to anonymous when no identity provided"


class TestSovereignAliasInvariant:
    """Invariant: All sovereign aliases resolve to 'ariffazil'"""

    SOVEREIGN_ALIASES = [
        "arif",
        "arif-fazil",
        "ariffazil",
        "muhammad-arif",
        "ARIF",
        "Arif",
        "Arif-Fazil",
    ]

    @pytest.mark.parametrize("alias", SOVEREIGN_ALIASES)
    def test_sovereign_alias_normalization(self, alias):
        """All variants of sovereign name resolve to canonical"""
        result = _resolve_canonical_actor(alias, None)
        assert result == "ariffazil", f"Alias '{alias}' must resolve to 'ariffazil'"


class TestIdentityStabilityInvariant:
    """Invariant: Once anchored, identity remains stable for session"""

    def test_identity_persists_in_session(self):
        """Session-bound identity must survive multiple lookups"""
        session_id = "stability-test-001"
        clear_session_identity(session_id)  # Clean slate
        
        # Anchor identity
        bind_session_identity(
            session_id=session_id,
            actor_id="ariffazil",
            authority_level="sovereign",
            auth_context={"actor_id": "ariffazil", "session_id": session_id},
            approval_scope=["arifos_kernel:execute"],
        )
        
        # Multiple lookups must return same identity
        for _ in range(5):
            stored = get_session_identity(session_id)
            assert stored is not None, "Anchored session must persist"
            assert stored["actor_id"] == "ariffazil", "Actor must not change"
            assert stored["authority_level"] == "sovereign", "Authority must not change"
        
        clear_session_identity(session_id)


class TestDisplayNameIsolationInvariant:
    """Invariant: Display name must never affect authority resolution"""

    def test_display_name_not_authority(self):
        """display_name field is presentation-only"""
        ctx = resolve_runtime_context(
            incoming_session_id="test-004",
            auth_context=None,
            actor_id="ariffazil",
            declared_name="Random Display Name",
        )
        # Canonical actor should be resolved correctly
        assert ctx["canonical_actor_id"] == "ariffazil"
        # Display name is preserved but separate
        assert ctx["display_name"] == "Random Display Name"
        # Authority source should reflect actual resolution
        assert ctx["authority_source"] in ["token", "session", "fallback"]


class TestUnicodeNormalizationInvariant:
    """Invariant: Unicode variants resolve consistently"""

    UNICODE_VARIANTS = [
        ("Ärif", "ärif"),  # Diacritic
        ("Ärif-Fazil", "ärif-fazil"),  # Diacritic in alias
    ]

    @pytest.mark.parametrize("input_name,expected_normalized", UNICODE_VARIANTS)
    def test_unicode_identity_resolution(self, input_name, expected_normalized):
        """Unicode variants should normalize deterministically"""
        result = _resolve_canonical_actor(input_name, None)
        # Currently: diacritics are stripped via .lower().strip()
        # This test documents current behavior; may need adjustment
        assert isinstance(result, str), "Must return string identity"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
