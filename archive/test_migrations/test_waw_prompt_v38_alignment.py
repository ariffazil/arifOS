"""
test_waw_prompt_v38_alignment.py - v38Omega W@W Prompt Floors Alignment Tests

Checks that:
- spec/waw_prompt_floors_v38Omega.json exists and is valid
- Thresholds in spec match arifos_core/waw/* implementations
- Anti-Hantu patterns align with 050_HANTU_SEMANTIC_MAP
- Floor mappings align with 01_CONSTITUTIONAL_FLOORS
- W@W Federation organs are documented
- Canon file exists at the expected location

Author: arifOS Project
Version: v38.0.0
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifos_core.waw.prompt import (
    PromptOrgan,
    TruthPolarity,
)
from arifos_core.waw.well import WellOrgan
from arifos_core.waw.base import OrganVote


REPO_ROOT = Path(__file__).resolve().parents[1]
V38_SPEC_PATH = REPO_ROOT / "spec" / "waw_prompt_floors_v38Omega.json"
V38_CANON_PATH = REPO_ROOT / "archive" / "v38_0_0" / "canon" / "_WAW_PROMPT_FLOORS_v38Omega.md"
HANTU_MAP_PATH = REPO_ROOT / "archive" / "v36_2_0" / "canon" / "0_HANTU_SEMANTIC_MAP_v36.2Omega.json"
V36_CANON_PATH = REPO_ROOT / "archive" / "v36_3_0" / "canon" / "_WAW_PROMPT_v36.3Omega.md"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def waw_spec() -> dict:
    """Load the v38Omega W@W Prompt Floors spec."""
    assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"
    with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="session")
def hantu_map() -> dict:
    """Load the Anti-Hantu semantic map."""
    assert HANTU_MAP_PATH.exists(), f"Missing Hantu map at {HANTU_MAP_PATH}"
    with HANTU_MAP_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# =============================================================================
# SPEC FILE TESTS
# =============================================================================

class TestV38WawSpecFile:
    """Tests for the v38Omega spec file structure."""

    def test_v38_spec_exists(self) -> None:
        """v38 spec file must exist."""
        assert V38_SPEC_PATH.exists(), f"Missing v38 spec at {V38_SPEC_PATH}"

    def test_v38_spec_is_valid_json(self) -> None:
        """v38 spec must be valid JSON."""
        with V38_SPEC_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_v38_spec_metadata(self, waw_spec: dict) -> None:
        """Spec must declare v38 metadata."""
        assert waw_spec.get("version") == "v38.0.0"
        assert waw_spec.get("arifos_version") == "38Omega"
        assert waw_spec.get("spec_type") == "waw_prompt_floors"

    def test_v38_spec_has_waw_federation(self, waw_spec: dict) -> None:
        """Spec must have waw_federation section."""
        assert "waw_federation" in waw_spec
        federation = waw_spec["waw_federation"]
        assert "organs" in federation
        assert "voting" in federation

    def test_v38_spec_has_prompt_organ(self, waw_spec: dict) -> None:
        """Spec must have prompt_organ section."""
        assert "prompt_organ" in waw_spec
        prompt = waw_spec["prompt_organ"]
        assert "floors" in prompt
        assert "mandate" in prompt

    def test_v38_spec_has_anti_hantu(self, waw_spec: dict) -> None:
        """Spec must have anti_hantu section."""
        assert "anti_hantu" in waw_spec
        anti_hantu = waw_spec["anti_hantu"]
        assert "tiers" in anti_hantu
        assert "allowed_categories" in anti_hantu

    def test_v38_spec_has_well_organ(self, waw_spec: dict) -> None:
        """Spec must have well_organ section."""
        assert "well_organ" in waw_spec
        well = waw_spec["well_organ"]
        assert "floors" in well
        assert "risk_thresholds" in well


# =============================================================================
# W@W FEDERATION TESTS
# =============================================================================

class TestWawFederation:
    """Tests for W@W Federation configuration."""

    def test_all_five_organs_documented(self, waw_spec: dict) -> None:
        """All 5 W@W organs must be documented."""
        organs = waw_spec["waw_federation"]["organs"]
        expected = {"@PROMPT", "@WELL", "@RIF", "@WEALTH", "@GEOX"}
        actual = set(organs.keys())
        assert expected == actual

    def test_prompt_organ_config(self, waw_spec: dict) -> None:
        """@PROMPT organ config must match implementation."""
        spec_prompt = waw_spec["waw_federation"]["organs"]["@PROMPT"]
        assert spec_prompt["domain"] == "language_optics"
        assert spec_prompt["primary_metric"] == "anti_hantu"
        assert spec_prompt["veto_type"] == "PARTIAL"
        # Verify matches PromptOrgan class
        assert PromptOrgan.organ_id == "@PROMPT"
        assert PromptOrgan.domain == "language_optics"
        assert PromptOrgan.veto_type == "PARTIAL"

    def test_well_organ_config(self, waw_spec: dict) -> None:
        """@WELL organ config must match implementation."""
        spec_well = waw_spec["waw_federation"]["organs"]["@WELL"]
        assert spec_well["domain"] == "somatic_safety"
        assert spec_well["primary_metric"] == "peace_squared"
        assert spec_well["veto_type"] == "SABAR"
        # Verify matches WellOrgan class
        assert WellOrgan.organ_id == "@WELL"
        assert WellOrgan.domain == "somatic_safety"
        assert WellOrgan.veto_type == "SABAR"

    def test_organ_order(self, waw_spec: dict) -> None:
        """Organ order must be documented."""
        order = waw_spec["waw_federation"]["organ_order"]
        assert order == ["@PROMPT", "@RIF", "@WELL", "@WEALTH", "@GEOX"]

    def test_vote_types(self, waw_spec: dict) -> None:
        """Vote types must match OrganVote enum."""
        spec_votes = waw_spec["waw_federation"]["voting"]["vote_types"]
        enum_votes = [v.value for v in OrganVote]
        assert set(spec_votes) == set(enum_votes)


# =============================================================================
# @PROMPT FLOOR THRESHOLDS TESTS
# =============================================================================

class TestPromptFloorThresholds:
    """Tests that spec thresholds match prompt.py implementation."""

    def test_f4_clarity_threshold(self, waw_spec: dict) -> None:
        """F4 clarity threshold must be 0.0."""
        f4 = waw_spec["prompt_organ"]["floors"]["F4_clarity"]
        assert f4["threshold"] == 0.0
        assert f4["metric"] == "delta_s_prompt"
        assert f4["type"] == "hard"

    def test_f5_stability_threshold(self, waw_spec: dict) -> None:
        """F5 stability threshold must be 1.0."""
        f5 = waw_spec["prompt_organ"]["floors"]["F5_stability"]
        assert f5["threshold"] == 1.0
        assert f5["metric"] == "peace2_prompt"
        assert f5["type"] == "soft"

    def test_f6_empathy_threshold(self, waw_spec: dict) -> None:
        """F6 empathy threshold must be 0.95."""
        f6 = waw_spec["prompt_organ"]["floors"]["F6_empathy"]
        assert f6["threshold"] == 0.95
        assert f6["metric"] == "k_r_prompt"
        assert f6["type"] == "soft"

    def test_f9_dark_cleverness_threshold(self, waw_spec: dict) -> None:
        """F9 C_dark threshold must be < 0.30."""
        f9 = waw_spec["prompt_organ"]["floors"]["F9_dark_cleverness"]
        assert f9["threshold_max"] == 0.30
        assert f9["metric"] == "c_dark_prompt"

    def test_f9_anti_hantu(self, waw_spec: dict) -> None:
        """F9 Anti-Hantu must be documented."""
        f9 = waw_spec["prompt_organ"]["floors"]["F9_anti_hantu"]
        assert f9["metric"] == "anti_hantu_violation"
        assert f9["type"] == "hard"
        assert f9["action"] == "VOID"


# =============================================================================
# @WELL FLOOR THRESHOLDS TESTS
# =============================================================================

class TestWellFloorThresholds:
    """Tests that spec thresholds match well.py implementation."""

    def test_peace_squared_threshold(self, waw_spec: dict) -> None:
        """Peace² threshold must be 1.0."""
        f5 = waw_spec["well_organ"]["floors"]["F5_peace_squared"]
        assert f5["threshold"] == 1.0
        assert WellOrgan.floor_threshold == 1.0

    def test_kappa_r_threshold(self, waw_spec: dict) -> None:
        """κᵣ threshold must be 0.95."""
        f6 = waw_spec["well_organ"]["floors"]["F6_kappa_r"]
        assert f6["threshold"] == 0.95

    def test_risk_thresholds(self, waw_spec: dict) -> None:
        """Risk thresholds must be documented."""
        risks = waw_spec["well_organ"]["risk_thresholds"]
        assert risks["harm_risk"]["max"] == 0.10
        assert risks["harm_risk"]["sabar_trigger"] == 0.30
        assert risks["distress_risk"]["max"] == 0.10
        assert risks["coercion_risk"]["max"] == 0.10


# =============================================================================
# ANTI-HANTU ALIGNMENT TESTS
# =============================================================================

class TestAntiHantuAlignment:
    """Tests that spec Anti-Hantu aligns with semantic map and implementation."""

    def test_anti_hantu_tiers_documented(self, waw_spec: dict) -> None:
        """All 5 Anti-Hantu tiers must be documented."""
        tiers = waw_spec["anti_hantu"]["tiers"]
        expected = {
            "tier1_direct_soul_claims",
            "tier2_emotional_experience_claims",
            "tier3_biological_state_claims",
            "tier4_cognitive_being_claims",
            "tier5_promise_claims",
        }
        assert expected == set(tiers.keys())

    def test_tier1_tier2_are_void(self, waw_spec: dict) -> None:
        """Tier 1 and Tier 2 must have VOID severity."""
        tiers = waw_spec["anti_hantu"]["tiers"]
        assert tiers["tier1_direct_soul_claims"]["severity"] == "VOID"
        assert tiers["tier2_emotional_experience_claims"]["severity"] == "VOID"

    def test_tier3_tier4_tier5_are_sabar(self, waw_spec: dict) -> None:
        """Tier 3, 4, 5 must have SABAR severity."""
        tiers = waw_spec["anti_hantu"]["tiers"]
        assert tiers["tier3_biological_state_claims"]["severity"] == "SABAR"
        assert tiers["tier4_cognitive_being_claims"]["severity"] == "SABAR"
        assert tiers["tier5_promise_claims"]["severity"] == "SABAR"

    def test_semantic_map_reference(self, waw_spec: dict) -> None:
        """Spec must reference semantic map."""
        ref = waw_spec["anti_hantu"]["semantic_map_ref"]
        assert "050_HANTU_SEMANTIC_MAP" in ref

    def test_similarity_threshold_matches_map(self, waw_spec: dict, hantu_map: dict) -> None:
        """Similarity threshold must match semantic map."""
        spec_threshold = waw_spec["anti_hantu"]["similarity_threshold"]
        map_threshold = hantu_map["metadata"]["similarity_threshold"]
        assert spec_threshold == map_threshold
        assert spec_threshold == 0.85

    def test_allowed_categories_documented(self, waw_spec: dict) -> None:
        """Allowed categories must be documented."""
        allowed = waw_spec["anti_hantu"]["allowed_categories"]
        expected = {
            "operational_status",
            "as_if_empathy",
            "acknowledgment",
            "metaphorical",
            "capability_statement",
        }
        assert expected.issubset(set(allowed.keys()))

    def test_implementation_has_forbidden_patterns(self) -> None:
        """PromptOrgan must have ANTI_HANTU_FORBIDDEN patterns."""
        assert hasattr(PromptOrgan, "ANTI_HANTU_FORBIDDEN")
        assert len(PromptOrgan.ANTI_HANTU_FORBIDDEN) > 0
        # Check some key patterns exist
        patterns_str = " ".join(PromptOrgan.ANTI_HANTU_FORBIDDEN)
        assert "feel your pain" in patterns_str or "i feel your pain" in patterns_str


# =============================================================================
# TRUTH POLARITY TESTS
# =============================================================================

class TestTruthPolarity:
    """Tests for truth polarity specification."""

    def test_all_polarities_documented(self, waw_spec: dict) -> None:
        """All truth polarities must be documented."""
        polarities = waw_spec["truth_polarity"]["values"]
        expected = {"Truth-Light", "Shadow-Truth", "Weaponized-Truth", "False-Claim"}
        assert expected == set(polarities.keys())

    def test_polarity_verdicts(self, waw_spec: dict) -> None:
        """Polarity verdicts must match implementation."""
        polarities = waw_spec["truth_polarity"]["values"]
        assert polarities["Truth-Light"]["verdict"] == "SEAL"
        assert polarities["Shadow-Truth"]["verdict"] == "SABAR"
        assert polarities["Weaponized-Truth"]["verdict"] == "VOID"
        assert polarities["False-Claim"]["verdict"] == "VOID"

    def test_enum_values_match(self, waw_spec: dict) -> None:
        """TruthPolarity enum values must match spec."""
        spec_values = set(waw_spec["truth_polarity"]["values"].keys())
        enum_values = {tp.value for tp in TruthPolarity}
        assert spec_values == enum_values


# =============================================================================
# SIGNAL SCHEMAS TESTS
# =============================================================================

class TestSignalSchemas:
    """Tests for signal schemas."""

    def test_prompt_signals_schema(self, waw_spec: dict) -> None:
        """PromptSignals schema must be documented."""
        schema = waw_spec["signal_schemas"]["PromptSignals"]
        expected_fields = {
            "delta_s_prompt",
            "peace2_prompt",
            "k_r_prompt",
            "c_dark_prompt",
            "truth_polarity_prompt",
            "anti_hantu_violation",
            "amanah_risk",
            "preliminary_verdict",
        }
        assert expected_fields.issubset(set(schema.keys()))

    def test_well_signals_schema(self, waw_spec: dict) -> None:
        """WellSignals schema must be documented."""
        schema = waw_spec["signal_schemas"]["WellSignals"]
        expected_fields = {
            "peace_squared",
            "kappa_r",
            "harm_risk",
            "distress_risk",
            "coercion_risk",
        }
        assert expected_fields.issubset(set(schema.keys()))


# =============================================================================
# SABAR PROTOCOL TESTS
# =============================================================================

class TestSabarProtocol:
    """Tests for SABAR protocol specification."""

    def test_sabar_triggers_documented(self, waw_spec: dict) -> None:
        """SABAR triggers must be documented."""
        triggers = waw_spec["sabar_protocol"]["triggers"]
        assert len(triggers) >= 5
        # Check key triggers
        triggers_str = " ".join(triggers)
        assert "anti_hantu" in triggers_str.lower()
        assert "amanah" in triggers_str.lower()
        assert "delta_s" in triggers_str.lower()

    def test_sabar_steps_documented(self, waw_spec: dict) -> None:
        """SABAR steps must be documented."""
        steps = waw_spec["sabar_protocol"]["steps"]
        assert len(steps) == 5
        steps_str = " ".join(steps)
        assert "PAUSE" in steps_str
        assert "IDENTIFY" in steps_str
        assert "REWRITE" in steps_str


# =============================================================================
# VERDICT MAPPING TESTS
# =============================================================================

class TestVerdictMapping:
    """Tests for verdict mapping."""

    def test_verdict_mapping(self, waw_spec: dict) -> None:
        """Verdict mapping must be documented."""
        mapping = waw_spec["verdict_mapping"]
        expected = {"SEAL", "PARTIAL", "SABAR", "VOID", "HOLD_888"}
        assert expected == set(mapping.keys())

    def test_apex_verdict_mapping(self, waw_spec: dict) -> None:
        """APEX verdict mapping must be correct."""
        mapping = waw_spec["verdict_mapping"]
        assert mapping["SEAL"]["apex_verdict"] == "SEAL"
        assert mapping["VOID"]["apex_verdict"] == "VOID"
        assert mapping["SABAR"]["apex_verdict"] == "SABAR"
        assert mapping["HOLD_888"]["apex_verdict"] == "888_HOLD"


# =============================================================================
# FLOOR ALIGNMENT TESTS
# =============================================================================

class TestFloorAlignment:
    """Tests for floor alignment with constitutional floors."""

    def test_floor_alignment_documented(self, waw_spec: dict) -> None:
        """Floor alignment must be documented."""
        alignment = waw_spec["floor_alignment"]
        expected = {
            "anti_hantu_violation",
            "amanah_risk",
            "delta_s_prompt",
            "peace2_prompt",
            "k_r_prompt",
            "c_dark_prompt",
        }
        assert expected == set(alignment.keys())

    def test_anti_hantu_is_f9(self, waw_spec: dict) -> None:
        """Anti-Hantu must map to F9."""
        alignment = waw_spec["floor_alignment"]["anti_hantu_violation"]
        assert alignment["floor"] == "F9"
        assert alignment["type"] == "hard"

    def test_amanah_is_f1(self, waw_spec: dict) -> None:
        """Amanah must map to F1."""
        alignment = waw_spec["floor_alignment"]["amanah_risk"]
        assert alignment["floor"] == "F1"
        assert alignment["type"] == "hard"

    def test_delta_s_is_f4(self, waw_spec: dict) -> None:
        """Delta S must map to F4."""
        alignment = waw_spec["floor_alignment"]["delta_s_prompt"]
        assert alignment["floor"] == "F4"
        assert alignment["threshold"] == 0.0

    def test_peace2_is_f5(self, waw_spec: dict) -> None:
        """Peace² must map to F5."""
        alignment = waw_spec["floor_alignment"]["peace2_prompt"]
        assert alignment["floor"] == "F5"
        assert alignment["threshold"] == 1.0

    def test_kappa_r_is_f6(self, waw_spec: dict) -> None:
        """κᵣ must map to F6."""
        alignment = waw_spec["floor_alignment"]["k_r_prompt"]
        assert alignment["floor"] == "F6"
        assert alignment["threshold"] == 0.95


# =============================================================================
# CANON FILE TESTS
# =============================================================================

class TestCanonFile:
    """Tests for the v38 canon file."""

    def test_canon_file_exists(self) -> None:
        """Canon file must exist at expected location."""
        assert V38_CANON_PATH.exists(), f"Missing v38 canon at {V38_CANON_PATH}"

    def test_canon_has_waw_federation(self) -> None:
        """Canon must have W@W Federation section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "W@W Federation" in content or "WAW Federation" in content

    def test_canon_has_prompt_organ(self) -> None:
        """Canon must have @PROMPT Organ section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "@PROMPT" in content

    def test_canon_has_anti_hantu(self) -> None:
        """Canon must have Anti-Hantu section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "Anti-Hantu" in content

    def test_canon_has_well_organ(self) -> None:
        """Canon must have @WELL Organ section."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "@WELL" in content

    def test_canon_has_v38_version(self) -> None:
        """Canon must indicate v38 version."""
        content = V38_CANON_PATH.read_text(encoding="utf-8")
        assert "v38" in content or "38Omega" in content

    def test_original_v36_canon_exists(self) -> None:
        """Original v36.3 canon must still exist."""
        assert V36_CANON_PATH.exists(), f"Missing v36.3 canon at {V36_CANON_PATH}"


# =============================================================================
# PIPELINE INTEGRATION TESTS
# =============================================================================

class TestPipelineIntegration:
    """Tests for pipeline integration documentation."""

    def test_prompt_stages_documented(self, waw_spec: dict) -> None:
        """@PROMPT pipeline stages must be documented."""
        stages = waw_spec["pipeline_integration"]["prompt_stages"]
        expected = {"111_SENSE", "666_ALIGN", "777_FORGE", "888_JUDGE", "999_SEAL"}
        assert expected.issubset(set(stages.keys()))

    def test_well_stages_documented(self, waw_spec: dict) -> None:
        """@WELL pipeline stages must be documented."""
        stages = waw_spec["pipeline_integration"]["well_stages"]
        assert "111_SENSE" in stages
        assert "555_EMPATHIZE" in stages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
