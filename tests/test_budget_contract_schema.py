"""
tests/test_budget_contract_schema.py — Budget Contract Schema tests
═══════════════════════════════════════════════════════════════

Verifies AAA-GOV-BUDGET-v1 Pydantic schema behavior:
- 7-domain budget model
- Consumption and exhaustion
- HOLD emission on violation
- Remaining percentage calculation
- Summary generation

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest

from arifosmcp.schemas.budget_contract import (
    BudgetContractSchema,
    BudgetDomain,
    DomainLimit,
    ViolationPolicy,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN LIMIT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDomainLimit:
    """Test individual domain limits."""

    def test_remaining_when_unused(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        assert limit.remaining() == 1000

    def test_remaining_after_consumption(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        limit.current = 600
        assert limit.remaining() == 400

    def test_remaining_floor_at_zero(self):
        limit = DomainLimit(domain=BudgetDomain.EXECUTION, limit=5)
        limit.current = 10  # over budget
        assert limit.remaining() == 0  # floor at 0

    def test_is_exhausted(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=100)
        limit.current = 100
        assert limit.is_exhausted() is True

    def test_not_exhausted(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=100)
        limit.current = 50
        assert limit.is_exhausted() is False

    def test_percent_used_zero(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        assert limit.percent_used() == 0.0

    def test_percent_used_half(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        limit.current = 500
        assert limit.percent_used() == 50.0

    def test_percent_used_full(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        limit.current = 1000
        assert limit.percent_used() == 100.0

    def test_percent_used_capped_at_100(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=1000)
        limit.current = 2000
        assert limit.percent_used() == 100.0

    def test_percent_used_zero_limit(self):
        """Zero limit = 100% used (nothing available)."""
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=0)
        assert limit.percent_used() == 100.0

    def test_default_on_violation_is_hold(self):
        limit = DomainLimit(domain=BudgetDomain.TOKEN, limit=100)
        assert limit.on_violation == ViolationPolicy.HOLD

    def test_blast_radius_default_is_void(self):
        """Blast radius violation = VOID (strictest)."""
        bc = BudgetContractSchema(session_id="test")
        blast = bc.get_domain(BudgetDomain.BLAST_RADIUS)
        assert blast is not None
        assert blast.on_violation == ViolationPolicy.VOID


# ═══════════════════════════════════════════════════════════════════════════════
# BUDGET CONTRACT SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestBudgetContractSchema:
    """Test the full budget contract schema."""

    def test_default_has_seven_domains(self):
        bc = BudgetContractSchema(session_id="test")
        assert len(bc.domains) == 7

    def test_all_domains_present(self):
        bc = BudgetContractSchema(session_id="test")
        domain_names = {d.domain for d in bc.domains}
        expected = {
            BudgetDomain.ENTROPY,
            BudgetDomain.TOKEN,
            BudgetDomain.EXECUTION,
            BudgetDomain.RETRY,
            BudgetDomain.SIDE_EFFECT,
            BudgetDomain.WALL_CLOCK,
            BudgetDomain.BLAST_RADIUS,
        }
        assert domain_names == expected

    def test_default_not_held(self):
        bc = BudgetContractSchema(session_id="test")
        assert bc.held is False
        assert bc.hold_reason is None

    def test_get_domain(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.TOKEN)
        assert d is not None
        assert d.domain == BudgetDomain.TOKEN
        assert d.limit == 200000

    def test_get_unknown_domain(self):
        bc = BudgetContractSchema(session_id="test")
        # We can't pass an invalid enum, but we can test the None path
        # by checking that all valid domains return non-None
        for domain in BudgetDomain:
            assert bc.get_domain(domain) is not None

    def test_consume_within_budget(self):
        bc = BudgetContractSchema(session_id="test")
        allowed, reason = bc.consume(BudgetDomain.EXECUTION, 5)
        assert allowed is True
        assert reason == "OK"
        d = bc.get_domain(BudgetDomain.EXECUTION)
        assert d.current == 5

    def test_consume_exceeds_budget(self):
        bc = BudgetContractSchema(session_id="test")
        allowed, reason = bc.consume(BudgetDomain.EXECUTION, 20)
        assert allowed is False
        assert "Budget exceeded" in reason
        assert "execution" in reason

    def test_check_and_hold_exceeds_budget(self):
        bc = BudgetContractSchema(session_id="test")
        allowed, reason = bc.check_and_hold(BudgetDomain.EXECUTION, 20)
        assert allowed is False
        assert "888_HOLD" in reason
        assert bc.held is True
        assert bc.hold_reason is not None

    def test_check_and_hold_within_budget(self):
        bc = BudgetContractSchema(session_id="test")
        allowed, reason = bc.check_and_hold(BudgetDomain.EXECUTION, 3)
        assert allowed is True
        assert reason == "OK"
        assert bc.held is False

    def test_held_blocks_consume(self):
        bc = BudgetContractSchema(session_id="test")
        bc.held = True
        bc.hold_reason = "test hold"
        allowed, reason = bc.consume(BudgetDomain.EXECUTION, 1)
        assert allowed is False
        assert "HOLD" in reason

    def test_held_blocks_check_and_hold(self):
        bc = BudgetContractSchema(session_id="test")
        bc.held = True
        bc.hold_reason = "test hold"
        allowed, reason = bc.check_and_hold(BudgetDomain.EXECUTION, 1)
        assert allowed is False
        assert "HOLD" in reason

    def test_is_exhausted_none(self):
        bc = BudgetContractSchema(session_id="test")
        assert bc.is_exhausted() is False

    def test_is_exhausted_after_consumption(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.EXECUTION)
        d.current = d.limit  # exhaust it
        assert bc.is_exhausted() is True
        assert bc.is_exhausted(BudgetDomain.EXECUTION) is True
        assert bc.is_exhausted(BudgetDomain.TOKEN) is False

    def test_remaining_percent_full(self):
        bc = BudgetContractSchema(session_id="test")
        assert bc.remaining_percent(BudgetDomain.TOKEN) == 100.0

    def test_remaining_percent_half(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.TOKEN)
        d.current = 100000  # half of 200000
        assert bc.remaining_percent(BudgetDomain.TOKEN) == 50.0

    def test_remaining_percent_empty(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.TOKEN)
        d.current = 200000  # full
        assert bc.remaining_percent(BudgetDomain.TOKEN) == 0.0

    def test_summary_contains_all_domains(self):
        bc = BudgetContractSchema(session_id="test")
        summary = bc.summary()
        assert summary["contract_id"] == "AAA-GOV-BUDGET-v1"
        assert summary["session_id"] == "test"
        assert summary["held"] is False
        assert "domains" in summary
        assert len(summary["domains"]) == 7

    def test_consume_with_unknown_domain(self):
        """Consuming from a domain not in the contract returns False."""
        bc = BudgetContractSchema(session_id="test")
        # We need to test the "unknown domain" path.
        # Simulate by clearing domains then checking.
        bc.domains = []
        allowed, reason = bc.consume(BudgetDomain.TOKEN, 1)
        assert allowed is False
        assert "Unknown budget domain" in reason


class TestBudgetContractSchemaValidation:
    """Schema validation tests."""

    def test_negative_max_turns_raises(self):
        with pytest.raises(ValueError, match="max_turns"):
            BudgetContractSchema(session_id="test", max_turns=-1)

    def test_negative_max_no_progress_raises(self):
        with pytest.raises(ValueError, match="max_no_progress_turns"):
            BudgetContractSchema(session_id="test", max_no_progress_turns=-1)

    def test_invalid_context_percent_raises(self):
        with pytest.raises(ValueError, match="max_context_percent"):
            BudgetContractSchema(session_id="test", max_context_percent=1.5)

    def test_negative_context_percent_raises(self):
        with pytest.raises(ValueError, match="max_context_percent"):
            BudgetContractSchema(session_id="test", max_context_percent=-0.1)

    def test_default_values(self):
        bc = BudgetContractSchema(session_id="test")
        assert bc.contract_id == "AAA-GOV-BUDGET-v1"
        assert bc.version == "1.1.0"
        assert bc.max_turns == 8
        assert bc.max_no_progress_turns == 2
        assert bc.max_context_percent == 0.75
        assert bc.turns == 0
        assert bc.held is False


class TestBudgetContractSchemaEdgeCases:
    """Edge case behavior."""

    def test_multiple_consumes_accumulate(self):
        bc = BudgetContractSchema(session_id="test")
        bc.consume(BudgetDomain.EXECUTION, 3)
        bc.consume(BudgetDomain.EXECUTION, 4)
        d = bc.get_domain(BudgetDomain.EXECUTION)
        assert d.current == 7

    def test_blast_radius_exhaustion_is_void(self):
        bc = BudgetContractSchema(session_id="test")
        blast = bc.get_domain(BudgetDomain.BLAST_RADIUS)
        assert blast.on_violation == ViolationPolicy.VOID

    def test_wall_clock_default_is_3600s(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.WALL_CLOCK)
        assert d.limit == 3600
        assert d.unit == "seconds"

    def test_side_effect_default_is_5(self):
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.SIDE_EFFECT)
        assert d.limit == 5
        assert d.unit == "count"

    def test_consume_exactly_at_limit(self):
        """Consuming exactly the limit is exhaustion."""
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.EXECUTION)
        bc.consume(BudgetDomain.EXECUTION, d.limit)
        assert d.is_exhausted() is True

    def test_consume_one_over_limit(self):
        """Consuming one over limit is blocked."""
        bc = BudgetContractSchema(session_id="test")
        d = bc.get_domain(BudgetDomain.EXECUTION)
        bc.consume(BudgetDomain.EXECUTION, d.limit)  # fill to max
        # Next consume should fail
        allowed, reason = bc.consume(BudgetDomain.EXECUTION, 1)
        assert allowed is False
        assert "Budget exceeded" in reason
