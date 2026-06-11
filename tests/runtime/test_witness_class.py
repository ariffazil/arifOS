"""
tests/runtime/test_witness_class.py — Unit tests for the positional witness taxonomy.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.witness_class import (
    NARRATIVE_SEAL_PATTERNS,
    ReceiptContext,
    WitnessPosition,
    classify_witness_position,
    narrator_debt,
    reject_narrative_seal,
    tri_witness_position_state,
)


# ──────────────────────────────────────────────────────────────────────
# Positional witness classification
# ──────────────────────────────────────────────────────────────────────


class TestWitnessPosition:
    def test_human_actor_is_human_position(self) -> None:
        ctx = ReceiptContext(actor_id="arif", tool_name="x", target_name="y")
        assert classify_witness_position(ctx) == WitnessPosition.HUMAN

    def test_human_actor_aliases_resolve(self) -> None:
        for alias in ("arif", "Arif", "arif-fazil", "ariffazil", "888"):
            ctx = ReceiptContext(actor_id=alias, tool_name="x", target_name="y")
            assert classify_witness_position(ctx) == WitnessPosition.HUMAN

    def test_tool_attesting_to_itself_is_self(self) -> None:
        ctx = ReceiptContext(tool_name="arif_forge_execute", target_name="arif_forge_execute")
        assert classify_witness_position(ctx) == WitnessPosition.SELF

    def test_human_wins_over_self_even_when_tool_self_attests(self) -> None:
        # The human sovereign's presence is the binding witness.
        # When actor_id is the sovereign, the position is HUMAN
        # regardless of whether the tool attests to itself. This is
        # the F13 SOVEREIGN signal: the human is outside every loop.
        ctx = ReceiptContext(
            actor_id="arif",
            tool_name="arif_forge_execute",
            target_name="arif_forge_execute",
        )
        assert classify_witness_position(ctx) == WitnessPosition.HUMAN

    def test_known_federation_agent_is_internal(self) -> None:
        ctx = ReceiptContext(agent_id="arifos", tool_name="sense", target_name="health")
        assert classify_witness_position(ctx) == WitnessPosition.INTERNAL

    def test_unknown_agent_is_external(self) -> None:
        ctx = ReceiptContext(agent_id="perplexity-sonnet", tool_name="x", target_name="y")
        assert classify_witness_position(ctx) == WitnessPosition.EXTERNAL

    def test_human_wins_over_self(self) -> None:
        # If the actor is human AND the tool attests to itself, the
        # position is HUMAN (the human is the binding witness, not
        # the tool's self-attestation).
        ctx = ReceiptContext(
            actor_id="arif",
            tool_name="arif_forge_execute",
            target_name="arif_forge_execute",
        )
        assert classify_witness_position(ctx) == WitnessPosition.HUMAN

    def test_custom_federation_set(self) -> None:
        ctx = ReceiptContext(agent_id="custom_agent", tool_name="x", target_name="y")
        # Not in default set
        assert classify_witness_position(ctx) == WitnessPosition.EXTERNAL
        # In custom set
        assert (
            classify_witness_position(ctx, federation_agents={"custom_agent"})
            == WitnessPosition.INTERNAL
        )


# ──────────────────────────────────────────────────────────────────────
# Narrator debt
# ──────────────────────────────────────────────────────────────────────


class TestNarratorDebt:
    def test_zero_debt_when_all_external(self) -> None:
        receipts = [
            (
                ReceiptContext(agent_id="ext_a", tool_name="x", target_name="y"),
                WitnessPosition.EXTERNAL,
            ),
            (
                ReceiptContext(actor_id="arif", tool_name="x", target_name="y"),
                WitnessPosition.HUMAN,
            ),
        ]
        assert narrator_debt(receipts) == 0

    def test_debt_counts_self_and_internal(self) -> None:
        receipts = [
            (ReceiptContext(tool_name="x", target_name="x"), WitnessPosition.SELF),
            (
                ReceiptContext(agent_id="arifos", tool_name="x", target_name="y"),
                WitnessPosition.INTERNAL,
            ),
            (
                ReceiptContext(agent_id="ext_a", tool_name="x", target_name="y"),
                WitnessPosition.EXTERNAL,
            ),
        ]
        assert narrator_debt(receipts) == 2

    def test_empty_receipts_zero_debt(self) -> None:
        assert narrator_debt([]) == 0


# ──────────────────────────────────────────────────────────────────────
# Tri-witness state
# ──────────────────────────────────────────────────────────────────────


class TestTriWitnessState:
    def test_three_substantive_zero_debt_is_ok(self) -> None:
        receipts = [
            (
                ReceiptContext(actor_id="arif", tool_name="x", target_name="y"),
                WitnessPosition.HUMAN,
            ),
            (
                ReceiptContext(agent_id="ext", tool_name="x", target_name="y"),
                WitnessPosition.EXTERNAL,
            ),
            (
                ReceiptContext(agent_id="geox", tool_name="x", target_name="y"),
                WitnessPosition.EXTERNAL,
            ),
        ]
        state = tri_witness_position_state(
            {"human": True, "ai": True, "earth": True},
            receipts,
        )
        assert state.state == "3/3_OK"
        assert state.position_debt == 0

    def test_three_substantive_with_debt_is_degraded(self) -> None:
        # The eureka: all three substantive booleans true, but one
        # receipt is from an internal agent attesting to a federation
        # member. That receipt is inside the loop.
        receipts = [
            (
                ReceiptContext(actor_id="arif", tool_name="x", target_name="y"),
                WitnessPosition.HUMAN,
            ),
            (
                ReceiptContext(agent_id="arifos", tool_name="probe", target_name="wealth"),
                WitnessPosition.INTERNAL,
            ),
            (
                ReceiptContext(agent_id="geox", tool_name="x", target_name="y"),
                WitnessPosition.EXTERNAL,
            ),
        ]
        state = tri_witness_position_state(
            {"human": True, "ai": True, "earth": True},
            receipts,
        )
        assert state.state == "2/3_DEGRADED"
        assert state.position_debt == 1
        assert any("SELF or INTERNAL" in n for n in state.notes)

    def test_one_substantive(self) -> None:
        state = tri_witness_position_state(
            {"human": True, "ai": False, "earth": False},
            [],
        )
        assert state.state == "1/3_DEGRADED"

    def test_zero_substantive(self) -> None:
        state = tri_witness_position_state(
            {"human": False, "ai": False, "earth": False},
            [],
        )
        assert state.state == "0/3_DEGRADED"


# ──────────────────────────────────────────────────────────────────────
# Narrative-seal rejection
# ──────────────────────────────────────────────────────────────────────


class TestNarrativeSealRejection:
    def test_empty_seal_accepted(self) -> None:
        result = reject_narrative_seal(None, None)
        assert result.accepted
        assert "no seal" in result.reason

    def test_empty_seal_with_hash_accepted(self) -> None:
        result = reject_narrative_seal("", "abc123def4567890abcdef")
        assert result.accepted

    def test_unrecognized_string_accepted(self) -> None:
        result = reject_narrative_seal("hello world", None)
        assert result.accepted

    def test_999_seal_alive_without_hash_rejected(self) -> None:
        result = reject_narrative_seal("999 SEAL ALIVE", None)
        assert not result.accepted
        assert "narrative-seal" in result.reason
        assert result.pattern_matched is not None
        assert "999" in result.pattern_matched

    def test_999_seal_alive_with_valid_hash_accepted(self) -> None:
        result = reject_narrative_seal(
            "999 SEAL ALIVE",
            "abcdef1234567890abcdef1234567890",
        )
        assert result.accepted
        assert "bound to a probe receipt hash" in result.reason

    def test_bare_seal_rejected(self) -> None:
        result = reject_narrative_seal("SEAL", None)
        assert not result.accepted

    def test_ditempa_footer_rejected(self) -> None:
        result = reject_narrative_seal("DITEMPA BUKAN DIBERI", None)
        assert not result.accepted
        assert result.pattern_matched is not None
        assert "DITEMPA" in result.pattern_matched

    def test_ditempa_footer_with_hash_accepted(self) -> None:
        # Even mottos become real seals when bound to a probe hash.
        result = reject_narrative_seal(
            "DITEMPA BUKAN DIBERI",
            "0123456789abcdef0123456789abcdef",
        )
        assert result.accepted

    def test_short_hash_rejected(self) -> None:
        result = reject_narrative_seal("999 SEAL ALIVE", "abc")
        assert not result.accepted

    def test_non_hex_hash_rejected(self) -> None:
        result = reject_narrative_seal(
            "999 SEAL ALIVE",
            "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",
        )
        assert not result.accepted

    @pytest.mark.parametrize("pattern", [p.pattern for p in NARRATIVE_SEAL_PATTERNS])
    def test_all_known_patterns_rejected_without_hash(self, pattern: str) -> None:
        examples = {
            r"^\s*999\s*SEAL\s*ALIVE\s*$": "999 SEAL ALIVE",
            r"^\s*SEAL\s*$": "SEAL",
            r"^\s*999\s*SEAL\s*$": "999 SEAL",
            r"^\s*FORGED_NOT_GIVEN\s*$": "FORGED_NOT_GIVEN",
            r"^\s*DITEMPA\s*BUKAN\s*DIBERI\s*$": "DITEMPA BUKAN DIBERI",
        }
        phrase = examples[pattern]
        result = reject_narrative_seal(phrase, None)
        assert not result.accepted
        assert result.pattern_matched is not None
        # mypy: pattern_matched is now non-None
        assert pattern in result.pattern_matched  # type: ignore[operator]
