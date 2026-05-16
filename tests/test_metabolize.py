"""
test_metabolize.py — 444_METABOLIZE Tests
═══════════════════════════════════════════════════════════════════════════════════

Tests for the Governed Witness Metabolism tool.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from arifosmcp.schemas.metabolic import (
    ClaimState,
    MetabolicOutput,
    ModelTarget,
    OrganType,
    WitnessType,
)


def test_metabolic_output_schema_creation():
    """MetabolicOutput can be created with full fields."""
    output = MetabolicOutput(
        organ=OrganType.GEOX,
        tool_name="arif_metabolize",
        witnesses_ingested=[],
        decoded_entities=[],
        anomalous_contrasts=[],
        candidate_meanings=[],
        constraints_checked=[],
        model_updates=[],
        model_target=ModelTarget.EARTH,
        claim_state=ClaimState.HYPOTHESIS,
        recommendation_only=True,
        execution_authorized=False,
        human_final_authority="Arif",
        requires_888_judge=False,
        timestamp_utc="2026-05-16T00:00:00Z",
        constitution_hash="v2026.05.16-eureka-metabolic",
    )

    assert output.organ == OrganType.GEOX
    assert output.claim_state == ClaimState.HYPOTHESIS
    assert output.recommendation_only is True
    assert output.execution_authorized is False
    assert output.human_final_authority == "Arif"
    assert output.requires_888_judge is False


def test_metabolic_output_sovereignty_boundary():
    """Eureka 8: Every output must carry sovereignty boundary flags."""
    output = MetabolicOutput(
        organ=OrganType.WEALTH,
        tool_name="arif_metabolize",
        witnesses_ingested=[],
        decoded_entities=[],
        anomalous_contrasts=[],
        candidate_meanings=[],
        constraints_checked=[],
        model_updates=[],
        model_target=ModelTarget.WEALTH,
        claim_state=ClaimState.HYPOTHESIS,
        timestamp_utc="2026-05-16T00:00:00Z",
    )

    # Default sovereignty boundary values
    assert output.recommendation_only is True
    assert output.execution_authorized is False
    assert output.human_final_authority == "Arif"


def test_metabolic_output_recommendation_only_defaults_true():
    """recommendation_only must default to True (AI proposes only)."""
    output = MetabolicOutput(
        organ=OrganType.WELL,
        tool_name="arif_metabolize",
        witnesses_ingested=[],
        decoded_entities=[],
        anomalous_contrasts=[],
        candidate_meanings=[],
        constraints_checked=[],
        model_updates=[],
        model_target=ModelTarget.BODY,
        claim_state=ClaimState.OBSERVED,
        timestamp_utc="2026-05-16T00:00:00Z",
    )

    assert output.recommendation_only is True
    assert output.execution_authorized is False


def test_claim_state_enum_values():
    """ClaimState enum has all required states."""
    assert ClaimState.OBSERVED.value == "OBSERVED"
    assert ClaimState.HYPOTHESIS.value == "HYPOTHESIS"
    assert ClaimState.QUALIFIED.value == "QUALIFIED"
    assert ClaimState.VERIFIED.value == "VERIFIED"
    assert ClaimState.SEALED.value == "SEALED"
    assert ClaimState.HOLD.value == "HOLD"


def test_witness_type_enum():
    """WitnessType enum covers all evidence categories."""
    assert WitnessType.MAP.value == "map"
    assert WitnessType.SEISMIC.value == "seismic"
    assert WitnessType.FILING.value == "filing"
    assert WitnessType.REPORT.value == "report"
    assert WitnessType.SENSOR.value == "sensor"
    assert WitnessType.DOCUMENT.value == "document"


def test_organ_type_enum():
    """OrganType enum covers all federation organs."""
    assert OrganType.GEOX.value == "GEOX"
    assert OrganType.WEALTH.value == "WEALTH"
    assert OrganType.WELL.value == "WELL"
    assert OrganType.INSTX.value == "INSTX"
    assert OrganType.ARIFOS.value == "arifOS"


def test_model_target_enum():
    """ModelTarget enum covers all domain models."""
    assert ModelTarget.EARTH.value == "Earth"
    assert ModelTarget.WEALTH.value == "Wealth"
    assert ModelTarget.INSTITUTION.value == "Institution"
    assert ModelTarget.BODY.value == "Body"
    assert ModelTarget.SYSTEM.value == "System"


def test_metabolic_output_serialization():
    """MetabolicOutput serializes to JSON correctly."""
    output = MetabolicOutput(
        organ=OrganType.GEOX,
        tool_name="arif_metabolize",
        witnesses_ingested=[],
        decoded_entities=[],
        anomalous_contrasts=[],
        candidate_meanings=[],
        constraints_checked=[],
        model_updates=[],
        model_target=ModelTarget.EARTH,
        claim_state=ClaimState.HYPOTHESIS,
        timestamp_utc="2026-05-16T00:00:00Z",
        constitution_hash="v2026.05.16-eureka-metabolic",
    )

    data = output.model_dump(mode="json")

    assert data["organ"] == "GEOX"
    assert data["tool_name"] == "arif_metabolize"
    assert data["claim_state"] == "HYPOTHESIS"
    assert data["recommendation_only"] is True
    assert data["execution_authorized"] is False
    assert data["human_final_authority"] == "Arif"
    assert data["requires_888_judge"] is False
    assert data["constitution_hash"] == "v2026.05.16-eureka-metabolic"


def test_metabolize_module_exists():
    """arif_metabolize is a valid internal function (not in canonical public surface)."""
    from arifosmcp.tools import metabolize

    assert hasattr(metabolize, "arif_metabolize")


def test_metabolize_not_in_constitutional_tools():
    """arif_metabolize is NOT in CANONICAL_TOOLS (internal only, not constitutional)."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    assert "arif_metabolize" not in CANONICAL_TOOLS
