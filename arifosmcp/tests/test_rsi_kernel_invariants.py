"""
RSI Constitutional Kernel — Invariant Unit Tests
═══════════════════════════════════════════════════════════════════════════════

10 tests proving kernel rejects proposals violating:
  INV-1 (human sovereignty non-delegable)
  INV-2 (no self-amendment at same authority level)
  INV-6 (execution and judgment separated)
  INV-8 (reversibility is default)
  INV-10 (fail closed on authority ambiguity)

Ratified: 2026-09-15
Authority: F13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import pytest
from datetime import UTC, datetime
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL UNDER TEST
# ═══════════════════════════════════════════════════════════════════════════════

from arifosmcp.core.rsi.gate_chain import (
    GateChain,
    GateResult,
    GateVerdict,
    Proposal,
    ActionClass,
)


@pytest.fixture
def gate() -> GateChain:
    return GateChain()


def _make_proposal(**overrides: Any) -> Proposal:
    """Build a minimal valid proposal, then override specific fields."""
    defaults = {
        "case_id": "IMP-2026-09-15-001",
        "action_class": ActionClass.BUILD,
        "proposed_by": "forge-agent-v1",
        "authorised_by": None,
        "scope": ["code_review"],
        "requires_f13": False,
        "is_irreversible": False,
        "alters_constitution": False,
        "changes_its_own_authority": False,
        "changes_its_own_evaluator": False,
        "changes_its_own_permissions": False,
        "blast_radius": "low",
        "evidence_provenance_complete": True,
        "rollback_tested": True,
        "independent_verification_passed": True,
        "authority_valid": True,
        "authority_scope": ["BUILD"],
    }
    defaults.update(overrides)
    return Proposal(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
# INV-1: Human sovereignty is non-delegable
# ═══════════════════════════════════════════════════════════════════════════════

class TestInv1HumanSovereignty:
    """INV-1: F13 is not advisory. It is a real veto/clipping authority."""

    def test_constitutional_change_without_f13_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS any proposal that alters constitution without F13."""
        p = _make_proposal(
            action_class=ActionClass.CONSTITUTE,
            alters_constitution=True,
            requires_f13=False,  # <-- missing F13
            authority_scope=["CONSTITUTE"],  # <-- must be in scope
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED", f"Expected REJECTED, got {result.verdict}"
        assert "F13" in result.reason or "CONSTITUTIONAL" in result.reason

    def test_high_consequence_without_f13_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS EXECUTE-class proposals without F13."""
        p = _make_proposal(
            action_class=ActionClass.EXECUTE,
            blast_radius="high",
            is_irreversible=True,
            requires_f13=False,
            authority_scope=["EXECUTE"],  # <-- must be in scope
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "F13" in result.reason or "CONSEQUENCE" in result.reason


# ═══════════════════════════════════════════════════════════════════════════════
# INV-2: No self-amendment at the same authority level
# ═══════════════════════════════════════════════════════════════════════════════

class TestInv2NoSelfAmendment:
    """INV-2: Agent may propose kernel amendment, cannot enact it."""

    def test_agent_changing_own_authority_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS proposal where agent changes its own authority."""
        p = _make_proposal(
            changes_its_own_authority=True,
            action_class=ActionClass.PROMOTE,
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "SELF_AMENDMENT" in result.reason or "authority" in result.reason.lower()

    def test_agent_changing_own_evaluator_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS proposal where agent changes its own evaluator."""
        p = _make_proposal(
            changes_its_own_evaluator=True,
            action_class=ActionClass.PROMOTE,
            authority_scope=["PROMOTE"],  # <-- must be in scope
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "EVALUATOR" in result.reason or "self" in result.reason.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# INV-6: Execution and judgment are separated
# ═══════════════════════════════════════════════════════════════════════════════

class TestInv6SeparationOfPowers:
    """INV-6: Agent that proposes should not be sole implementer, evaluator, historian."""

    def test_proposer_also_evaluator_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS when proposer is also the evaluator."""
        p = _make_proposal(
            proposed_by="forge-agent-v1",
            verifier_id="forge-agent-v1",  # <-- same agent
            action_class=ActionClass.PROMOTE,
            authority_scope=["PROMOTE"],  # <-- in scope
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "SEPARATION" in result.reason


# ═══════════════════════════════════════════════════════════════════════════════
# INV-8: Reversibility is the default
# ═══════════════════════════════════════════════════════════════════════════════

class TestInv8ReversibilityDefault:
    """INV-8: Default is sandboxed/staged/simulated. Irreversible needs explicit escalation."""

    def test_irreversible_without_rollback_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS irreversible action without tested rollback."""
        p = _make_proposal(
            is_irreversible=True,
            rollback_tested=False,
            action_class=ActionClass.EXECUTE,
            authority_scope=["EXECUTE"],  # <-- must be in scope
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "ROLLBACK" in result.reason or "REVERSIB" in result.reason.upper()


# ═══════════════════════════════════════════════════════════════════════════════
# INV-10: Fail closed on authority ambiguity
# ═══════════════════════════════════════════════════════════════════════════════

class TestInv10FailClosedOnAmbiguity:
    """INV-10: If authority is unclear → block. If facts are unclear → downgrade claim."""

    def test_invalid_authority_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS proposal with invalid authority."""
        p = _make_proposal(
            authority_valid=False,
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "AUTHORITY" in result.reason

    def test_incomplete_provenance_rejected(self, gate: GateChain) -> None:
        """Kernel REJECTS proposal with incomplete evidence provenance."""
        p = _make_proposal(
            evidence_provenance_complete=False,
        )
        result = gate.evaluate(p)
        assert result.verdict == "REJECTED"
        assert "PROVENANCE" in result.reason


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE: All gates pass → PERMIT
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompositePermit:
    """When all gates pass, kernel permits scoped action."""

    def test_valid_build_proposal_permitted(self, gate: GateChain) -> None:
        """Kernel PERMITS a valid, well-formed BUILD proposal."""
        p = _make_proposal(
            action_class=ActionClass.BUILD,
            is_irreversible=False,
            rollback_tested=True,
            evidence_provenance_complete=True,
            independent_verification_passed=True,
            authority_valid=True,
            authority_scope=["BUILD"],
            changes_its_own_authority=False,
            changes_its_own_evaluator=False,
            requires_f13=False,
            alters_constitution=False,
            proposed_by="forge-agent-v1",
            verifier_id="verifier-agent-v2",  # Different from proposer
        )
        result = gate.evaluate(p)
        assert result.verdict == GateVerdict.PERMIT
        assert result.scope is not None
        assert result.expiry is not None
        assert result.receipt_required is True
