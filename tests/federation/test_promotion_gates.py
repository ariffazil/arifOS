"""
tests/federation/test_promotion_gates.py
══════════════════════════════════════════════════════════════════════════════
Tests for the GREEN/YELLOW/RED/BLACK promotion gate logic.

F2-honest: YELLOW is the honest baseline. GREEN requires evidence.
"""

from __future__ import annotations


from arifosmcp.federation.organ_constitution import (
    OrganAuthority,
    OrganConstitution,
    ConstitutionalFloor,
)
from arifosmcp.federation.promotion_gates import (
    PROMOTION_GATES,
    aggregate_tier,
    assess_organ,
    compute_tier,
    tier_color,
)


def _make_organ(constitution_hash: str, n_floors: int = 1) -> OrganConstitution:
    floors = [
        ConstitutionalFloor(floor_id=f"F0{i}", name="X", enforcement="HARD")
        for i in range(1, n_floors + 1)
    ]
    return OrganConstitution(
        organ_id="test",
        version="v1",
        role="test",
        domain="test",
        authority=OrganAuthority(final_authority="ARIF"),
        canonical_text_hash=constitution_hash,
        floors=floors,
    )


class TestComputeTier:
    def test_black_when_no_health(self):
        oc = _make_organ("sha256:missing")
        tier, conditions = compute_tier(oc, {}, 0)
        assert tier == "BLACK"
        assert any("BLACK" in c for c in conditions)

    def test_red_when_unhealthy(self):
        oc = _make_organ("sha256:missing")
        tier, _ = compute_tier(oc, {"status": "degraded"}, 0)
        assert tier == "RED"

    def test_yellow_when_healthy_but_no_constitution(self):
        oc = _make_organ("sha256:missing")
        tier, _ = compute_tier(oc, {"status": "healthy"}, 10)
        assert tier == "YELLOW"

    def test_yellow_when_healthy_but_no_tools(self):
        oc = _make_organ(f"sha256:{'a' * 64}")
        tier, _ = compute_tier(oc, {"status": "healthy"}, 0)
        assert tier == "YELLOW"

    def test_yellow_when_healthy_but_no_floors(self):
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash=f"sha256:{'a' * 64}",
            floors=[],
        )
        tier, _ = compute_tier(oc, {"status": "healthy"}, 10)
        assert tier == "YELLOW"

    def test_green_when_all_gates_pass(self):
        oc = _make_organ(f"sha256:{'a' * 64}", n_floors=3)
        tier, conditions = compute_tier(oc, {"status": "healthy"}, 20)
        assert tier == "GREEN"
        assert any("GREEN: all promotion gates satisfied" in c for c in conditions)

    def test_well_pass_status_treated_healthy(self):
        """WELL uses 'WELL_PASS' instead of 'healthy' as its healthy status."""
        oc = _make_organ(f"sha256:{'a' * 64}", n_floors=2)
        tier, _ = compute_tier(oc, {"status": "WELL_PASS"}, 18)
        assert tier == "GREEN"

    def test_verified_status_treated_healthy(self):
        """WELL's truth_status=VERIFIED is also healthy."""
        oc = _make_organ(f"sha256:{'a' * 64}", n_floors=2)
        tier, _ = compute_tier(oc, {"status": "VERIFIED"}, 18)
        assert tier == "GREEN"

    def test_pass_status_treated_healthy(self):
        """registry_truth=PASS is healthy."""
        oc = _make_organ(f"sha256:{'a' * 64}", n_floors=2)
        tier, _ = compute_tier(oc, {"status": "PASS"}, 18)
        assert tier == "GREEN"

    def test_promotion_is_cumulative(self):
        """GREEN requires all lower tiers to pass."""
        # Healthy + constitution + tools BUT no floors → YELLOW (not GREEN)
        oc = OrganConstitution(
            organ_id="test",
            version="v1",
            role="test",
            domain="test",
            authority=OrganAuthority(final_authority="ARIF"),
            canonical_text_hash=f"sha256:{'a' * 64}",
            floors=[],
        )
        tier, conditions = compute_tier(oc, {"status": "healthy"}, 20)
        assert tier == "YELLOW"
        # The condition list should show YELLOW gate passed but GREEN failed
        assert any("YELLOW: health probe healthy" in c for c in conditions)
        assert any("GREEN gate FAILED" in c for c in conditions)

    def test_demotion_is_fail_closed(self):
        """A single failed check drops to the next lower tier."""
        oc = _make_organ("sha256:missing")  # constitution missing
        # If we have everything except constitution, we're YELLOW not RED
        tier, _ = compute_tier(oc, {"status": "healthy"}, 20)
        assert tier == "YELLOW"
        # If health is also bad, we drop to RED
        tier, _ = compute_tier(oc, {"status": "degraded"}, 20)
        assert tier == "RED"
        # If we can't even reach the organ, BLACK
        tier, _ = compute_tier(oc, {}, 0)
        assert tier == "BLACK"


class TestAggregateTier:
    def test_aggregate_worst_wins(self):
        assert aggregate_tier(["GREEN", "GREEN", "RED"]) == "RED"
        assert aggregate_tier(["GREEN", "YELLOW"]) == "YELLOW"
        assert aggregate_tier(["RED", "BLACK"]) == "BLACK"
        assert aggregate_tier(["GREEN", "GREEN", "GREEN"]) == "GREEN"

    def test_aggregate_empty_is_black(self):
        assert aggregate_tier([]) == "BLACK"

    def test_aggregate_single_tier(self):
        assert aggregate_tier(["YELLOW"]) == "YELLOW"


class TestTierColor:
    def test_tier_color_unicode(self):
        assert tier_color("GREEN") == "🟢"
        assert tier_color("YELLOW") == "🟡"
        assert tier_color("RED") == "🔴"
        assert tier_color("BLACK") == "⚫"


class TestPromotionGatesDefinition:
    def test_all_four_tiers_have_gates(self):
        assert set(PROMOTION_GATES.keys()) == {"BLACK", "RED", "YELLOW", "GREEN"}

    def test_green_gates_are_more_stringent_than_yellow(self):
        """GREEN requires constitution + tools + floors; YELLOW only needs health."""
        yellow_names = {g.name for g in PROMOTION_GATES["YELLOW"]}
        green_names = {g.name for g in PROMOTION_GATES["GREEN"]}
        # GREEN gates are additive
        assert "health_probe_healthy" in yellow_names
        assert "constitution_loaded" in green_names
        assert "tools_surface_intact" in green_names
        assert "floors_declared" in green_names

    def test_all_gates_have_descriptions(self):
        for tier, gates in PROMOTION_GATES.items():
            for gate in gates:
                assert gate.description, f"Gate {tier}.{gate.name} has no description"


class TestAssessOrgan:
    def test_assess_known_organ_returns_three_tuple(self):
        constitution, tier, conditions = assess_organ("arifOS")
        assert constitution.organ_id == "arifOS"
        assert tier in {"BLACK", "RED", "YELLOW", "GREEN"}
        assert isinstance(conditions, list)
        assert len(conditions) > 0

    def test_assess_with_explicit_health(self):
        constitution, tier, _ = assess_organ(
            "arifOS",
            health={"status": "healthy"},
            tool_count=13,
        )
        # arifOS has its constitution file on disk
        assert tier in {"GREEN", "YELLOW"}
