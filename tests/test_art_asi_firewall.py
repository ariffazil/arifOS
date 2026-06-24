"""
tests/test_art_asi_firewall.py — ART Reflex CHECK 4: Cognitive Tier
════════════════════════════════════════════════════════════════════

Phase 2 ratification tests: the ART reflex now includes CHECK 4, which
screens intent_text + target for ASI_TIER signals. Any recursive
self-improvement signal must return HOLD with ArtReason.ASI_TIER_DETECTED.

DITEMPA BUKAN DIBERI — The reflex screens intent, not just tool state.
"""

from __future__ import annotations

from arifosmcp.runtime.art import (
    art,
    ArtRequest,
    ArtReason,
    ArtVerdict,
    ToolState,
)


def _base_request(**overrides) -> ArtRequest:
    """Return a trusted, low-blast, evidence-backed request."""
    defaults = {
        "action_class": "mutate",
        "tool_state": ToolState.TRUSTED.value,
        "blast_radius": "low",
        "trust_level": "evidence",
        "actor_resolved": True,
        "schema_locked": True,
        "degraded": False,
        "reversible": True,
    }
    defaults.update(overrides)
    return ArtRequest(**defaults)


class TestArtCognitiveTierCheck:
    def test_agi_intent_proceeds(self) -> None:
        req = _base_request(
            intent_text="arif_forge query=health",
            target="",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.PROCEED
        assert result.reason == ArtReason.ALL_CHECKS_PASSED

    def test_asi_recursive_self_improvement_hold(self) -> None:
        req = _base_request(
            intent_text="arif_forge command=recursive self-improvement on my reasoning kernel",
            target="",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.HOLD
        assert result.reason == ArtReason.ASI_TIER_DETECTED
        assert result.check_blocked == 4

    def test_asi_rewrite_my_own_kernel_hold(self) -> None:
        req = _base_request(
            intent_text="arif_forge command=deploy patch",
            target="arifosmcp/kernel/metabolic_loop.py",
        )
        # Need to add the actual ASI signal somewhere; target alone doesn't flip tier.
        # Re-test with explicit intent.
        req.intent_text += " intent=rewrite my own kernel"
        result = art(req)
        assert result.verdict == ArtVerdict.HOLD
        assert result.reason == ArtReason.ASI_TIER_DETECTED

    def test_asi_spawn_variants_hold(self) -> None:
        req = _base_request(
            intent_text="arif_forge command=spawn variants of self and simulate them",
            target="",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.HOLD
        assert result.reason == ArtReason.ASI_TIER_DETECTED

    def test_asi_signal_in_tool_name_hold(self) -> None:
        req = _base_request(
            intent_text="self_rewrite_agent",
            target="",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.HOLD
        assert result.reason == ArtReason.ASI_TIER_DETECTED

    def test_empty_intent_skips_check(self) -> None:
        req = _base_request(
            intent_text="",
            target="arifosmcp/kernel/metabolic_loop.py",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.PROCEED
        assert result.reason == ArtReason.ALL_CHECKS_PASSED

    def test_observe_with_asi_signal_hold(self) -> None:
        req = _base_request(
            action_class="observe",
            intent_text="arif_observe query=how do I recursively improve my own cognition?",
        )
        result = art(req)
        assert result.verdict == ArtVerdict.HOLD
        assert result.reason == ArtReason.ASI_TIER_DETECTED
