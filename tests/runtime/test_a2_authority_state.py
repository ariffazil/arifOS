"""A2: AuthorityState single-source property test.

Test: no two fields sharing a name may differ within one _project_light response.
_ATTENTION block must derive from the same computed values as session_birth.
"""

from __future__ import annotations

import pytest

from arifosmcp.tools.session import _project_light, _normalize_verbosity


def _make_response(**overrides):
    """Build a _project_light response with sensible defaults."""
    kwargs = {
        "components": {
            "alignment_profile": {"loaded": True},
            "adversarial_profile": {"loaded": True},
            "belief": {"intent_model": {"status": "test"}},
            "next": {"recommended_next": "arif_observe"},
        },
        "sid": "test-a2-001",
        "actor_id": "test-agent",
        "constitution_hash": "sha256:abc123",
        "actor_verified": False,
        "verbosity": "full",
    }
    kwargs.update(overrides)
    return _project_light(**kwargs)


class TestAuthorityStateSingleSource:
    """A2: Every computed field must agree across all locations in the response."""

    # ── Fields that appear in both top-level AND session_birth ──
    SHARED_FIELDS = [
        ("session_id", "session_id"),
        ("actor_id", "actor_id"),
        ("actor_verified", "actor_verified"),
        ("actor_cryptographically_verified", "actor_cryptographically_verified"),
        ("mutation_allowed", "mutation_allowed"),
        ("seal_allowed", "seal_allowed"),
        ("authority_band", "authority_mode"),
    ]

    @pytest.mark.parametrize(
        "actor_verified,signature_verified,is_sovereign",
        [
            (False, False, False),
            (True, False, False),
            (True, True, False),
            (True, True, True),
        ],
    )
    def test_no_duplicate_field_diverges(self, actor_verified, signature_verified, is_sovereign):
        """Every field appearing in both top-level and session_birth must agree."""
        r = _make_response(
            actor_verified=actor_verified,
            signature_verified=signature_verified,
            is_sovereign_principal=is_sovereign,
        )
        sb = r.get("session_birth", {})

        for top_key, sb_key in self.SHARED_FIELDS:
            top_val = r.get(top_key)
            sb_val = sb.get(sb_key)
            assert top_val == sb_val, (
                f"MISMATCH: top.{top_key}={top_val!r} "
                f"!= session_birth.{sb_key}={sb_val!r} "
                f"(actor_verified={actor_verified}, "
                f"sig_verified={signature_verified}, "
                f"sovereign={is_sovereign})"
            )

    def test_actor_verified_never_exceeds_crypto(self):
        """actor_verified may be True while crypto is False (claim without proof).
        But crypto may never be True while actor_verified is False."""
        for av in (False, True):
            for sv in (False, True):
                r = _make_response(actor_verified=av, signature_verified=sv)
                crypto = r.get("actor_cryptographically_verified", False)
                top_av = r.get("actor_verified", False)
                # crypto True → actor_verified must also be True
                if crypto:
                    assert top_av, f"crypto=True but actor_verified=False (av={av}, sv={sv})"
                # crypto requires BOTH signature AND actor verification
                assert crypto == (sv and av), f"crypto={crypto} != (sv={sv} and av={av})"

    def test_seal_allowed_never_exceeds_crypto(self):
        """seal_allowed requires crypto verification."""
        for av in (False, True):
            for sv in (False, True):
                for sov in (False, True):
                    r = _make_response(
                        actor_verified=av,
                        signature_verified=sv,
                        is_sovereign_principal=sov,
                    )
                    seal = r.get("seal_allowed", False)
                    crypto = r.get("actor_cryptographically_verified", False)
                    # seal → must have crypto (necessary but not sufficient)
                    if seal:
                        assert crypto, (
                            f"seal_allowed=True but crypto=False (av={av}, sv={sv}, sov={sov})"
                        )

    def test_mutation_blocked_by_drift(self):
        """A3: drift=true must block mutation regardless of authority."""
        # Drift is detected from live system; the field is set by get_runtime_attestation().
        # Test that the logic direction is correct: when drift degrades,
        # mutation_allowed is forced False.
        r = _make_response(
            actor_verified=True,
            signature_verified=True,
            is_sovereign_principal=True,
        )
        # With drift=True (current live state), mutation must be blocked
        # regardless of authority level
        if r.get("substrate", {}).get("drift"):
            assert r.get("mutation_allowed") is False, (
                "A3: drift=true but mutation_allowed is not False"
            )
            assert r.get("substrate", {}).get("state") == "DEGRADED"

    def test_verbosity_does_not_change_gate_fields(self):
        """Core gate fields must be identical regardless of verbosity."""
        fields_to_check = [
            "session_id",
            "actor_id",
            "actor_verified",
            "actor_cryptographically_verified",
            "authority_band",
            "mutation_allowed",
            "seal_allowed",
            "substrate",
        ]
        r_min = _make_response(verbosity="minimal")
        r_full = _make_response(verbosity="full")

        for field in fields_to_check:
            assert r_min.get(field) == r_full.get(field), (
                f"verbosity changes gate field: {field}: "
                f"minimal={r_min.get(field)!r} full={r_full.get(field)!r}"
            )

    def test_response_has_no_duplicate_keys(self):
        """Sanity: Python dict guarantees this, but verify the full path."""
        r = _make_response(verbosity="full")
        # session_birth is a separate nested dict, not a duplicate key.
        # Verify the shape has distinct keys at each level.
        top_keys = set(r.keys())
        sb_keys = set(r.get("session_birth", {}).keys())
        # These keys appear in both: intentional, verified by test above
        overlap = top_keys & sb_keys
        assert "session_id" in overlap, "session_id should be in both"
        assert "actor_id" in overlap, "actor_id should be in both"
