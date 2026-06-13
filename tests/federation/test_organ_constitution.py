"""
tests/federation/test_organ_constitution.py
══════════════════════════════════════════════════════════════════════════════
Tests for the Pydantic v2 organ constitution schema.

F2-honest: a missing constitution file must yield YELLOW tier, never GREEN.
The schema must reject unknown fields (extra='forbid').
"""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from arifosmcp.federation.organ_constitution import (
    ConstitutionalFloor,
    OrganAuthority,
    OrganBoundaries,
    OrganConstitution,
    list_known_organs,
    load_organ_constitution,
)


class TestOrganConstitutionSchema:
    def test_minimal_valid_constitution(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash=f"sha256:{'a' * 64}",
        )
        assert oc.organ_id == "test"
        assert oc.tier == "YELLOW"  # F7 HUMILITY default
        assert oc.floor_signature == ""  # no floors declared
        assert oc.is_sovereign_bound is True  # final_authority=ARIF

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            OrganConstitution(
                organ_id="test",
                version="v1",
                role="test",
                domain="test",
                authority=OrganAuthority(final_authority="ARIF"),
                canonical_text_hash=f"sha256:{'a' * 64}",
                rogue_field="should_not_appear",
            )
        assert "rogue_field" in str(exc.value)

    def test_hash_format_validation_accepts_valid_sha256(self):
        valid = f"sha256:{hashlib.sha256(b'x').hexdigest()}"
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash=valid,
        )
        assert oc.canonical_text_hash == valid

    def test_hash_format_validation_accepts_missing_marker(self):
        """sha256:missing is the explicit 'no file found' marker."""
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash="sha256:missing",
        )
        assert oc.canonical_text_hash == "sha256:missing"

    def test_hash_format_rejects_invalid_format(self):
        with pytest.raises(ValidationError):
            OrganConstitution(
                organ_id="test",
                version="v1",
                role="test",
                domain="test",
                authority=OrganAuthority(final_authority="ARIF"),
                canonical_text_hash="md5:abcdef",
            )

    def test_floor_id_pattern_enforced(self):
        with pytest.raises(ValidationError):
            ConstitutionalFloor(floor_id="F99", name="BAD", enforcement="HARD")

        with pytest.raises(ValidationError):
            ConstitutionalFloor(floor_id="F1", name="BAD", enforcement="HARD")

        # Valid
        f = ConstitutionalFloor(floor_id="F13", name="SOVEREIGN", enforcement="HARD")
        assert f.floor_id == "F13"

    def test_enforcement_literal_enforced(self):
        with pytest.raises(ValidationError):
            ConstitutionalFloor(floor_id="F01", name="X", enforcement="MAYBE")

    def test_floor_signature_sorted(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash="sha256:missing",
            floors=[
                ConstitutionalFloor(floor_id="F11", name="AUTH", enforcement="HARD"),
                ConstitutionalFloor(floor_id="F01", name="AMANAH", enforcement="HARD"),
                ConstitutionalFloor(floor_id="F07", name="HUMILITY", enforcement="SOFT"),
            ],
        )
        assert oc.floor_signature == "F01,F07,F11"

    def test_hard_floors_filter(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash="sha256:missing",
            floors=[
                ConstitutionalFloor(floor_id="F01", name="AMANAH", enforcement="HARD"),
                ConstitutionalFloor(floor_id="F07", name="HUMILITY", enforcement="SOFT"),
                ConstitutionalFloor(floor_id="F11", name="AUTH", enforcement="HARD"),
            ],
        )
        assert oc.hard_floors == ["F01", "F11"]

    def test_to_canonical_json_deterministic(self):
        """Same content must produce same hash — required for federation hash."""
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash="sha256:missing",
            floors=[ConstitutionalFloor(floor_id="F01", name="X", enforcement="HARD")],
        )
        j1 = oc.to_canonical_json()
        j2 = oc.to_canonical_json()
        assert j1 == j2

    def test_sovereign_bound_when_ARIF(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash="sha256:missing",
        )
        assert oc.is_sovereign_bound is True

    def test_sovereign_bound_when_sovereign_ack_required(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="DELEGATED_TO_KERNEL"),
            canonical_text_hash="sha256:missing",
            boundaries=OrganBoundaries(requires_sovereign_ack=["vault_seal"]),
        )
        assert oc.is_sovereign_bound is True


class TestOrganConstitutionLoaders:
    def test_list_known_organs_includes_six(self):
        known = list_known_organs()
        assert set(known) == {"arifOS", "GEOX", "WEALTH", "WELL", "A-FORGE", "AAA"}

    def test_load_arifOS_constitution(self):
        oc = load_organ_constitution("arifOS")
        assert oc.organ_id == "arifOS"
        assert oc.domain == "governance"
        assert oc.authority.final_authority == "ARIF"
        # arifOS constitution file should exist on this VPS
        if oc.canonical_text_hash != "sha256:missing":
            assert oc.canonical_text_path is not None
            assert oc.canonical_text_hash.startswith("sha256:")
            assert len(oc.canonical_text_hash) == 7 + 64

    def test_load_GEOX_constitution(self):
        oc = load_organ_constitution("GEOX")
        assert oc.organ_id == "GEOX"
        assert oc.domain == "subsurface_evidence"
        assert oc.authority.final_authority == "ARIF"
        # F2, F4, F7 should be in the floor list
        floor_ids = {f.floor_id for f in oc.floors}
        assert "F02" in floor_ids
        assert "F07" in floor_ids

    def test_load_WELL_constitution_is_reflect_only(self):
        oc = load_organ_constitution("WELL")
        assert oc.organ_id == "WELL"
        assert oc.authority.final_authority == "REFLECT_ONLY"
        # F6 EMPATHY should be in the floor list
        floor_ids = {f.floor_id for f in oc.floors}
        assert "F06" in floor_ids

    def test_load_unknown_organ_raises(self):
        with pytest.raises(ValueError) as exc:
            load_organ_constitution("non_existent_organ")
        assert "non_existent_organ" in str(exc.value)

    def test_aforge_AAA_constitutions_declare_no_constitution_file(self):
        """A-FORGE and AAA have no GENESIS/000 yet — YELLOW is honest."""
        for organ_id in ["A-FORGE", "AAA"]:
            oc = load_organ_constitution(organ_id)
            assert oc.canonical_text_hash == "sha256:missing"
            assert oc.canonical_text_path is None
            # But the constitution is still declared
            assert oc.authority.final_authority == "ARIF"
            assert len(oc.floors) > 0
