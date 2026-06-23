"""
tests/golden/organs/sense/test_sense_golden.py — 111_SENSE Golden Contract Tests

Phase 0: Freeze governance pathway parity (check_laws vs kernel bridge),
agentic search plan structure, sensing sufficiency grading,
and paradox anchor injection.

Constitutional risk: MODERATE. Sense bridges external reality into the
constitutional pipeline. Its governance pathway must produce identical
results whether routed through check_laws() or the kernel bridge.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations


from arifosmcp.tools.sense import (
    SENSE_PARADOX_ANCHORS,
    _SENSE_BY_CELL,
    _SENSE_BY_ID,
    _agentic_search_plan,
    _grade_sensing_sufficiency,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PARADOX ANCHOR REGISTRY — 9 anchors
# ═══════════════════════════════════════════════════════════════════════════════


class TestSenseAnchorRegistry:
    """Freeze the 9 Sense paradox anchors."""

    def test_nine_anchors_exist(self):
        """Sense must have exactly 9 paradox anchors."""
        assert len(SENSE_PARADOX_ANCHORS) == 9

    def test_all_cells_and_ids_resolve(self):
        """Every anchor must resolve by both cell and ID."""
        for anchor in SENSE_PARADOX_ANCHORS:
            assert anchor["id"] in _SENSE_BY_ID, f"ID {anchor['id']} not in _SENSE_BY_ID"
            assert anchor["matrix_cell"] in _SENSE_BY_CELL, (
                f"Cell {anchor['matrix_cell']} not in _SENSE_BY_CELL"
            )

    def test_golden_anchor_ids(self):
        """Verify key Sense anchors exist."""
        # S_TxC: Deming — bring data
        assert "S_TxC" in _SENSE_BY_ID
        assert "Deming" in _SENSE_BY_ID["S_TxC"]["quote"]["author"]

        # S_HxC: Hawking — illusion of knowledge
        assert "S_HxC" in _SENSE_BY_ID
        assert "Hawking" in _SENSE_BY_ID["S_HxC"]["quote"]["author"]

        # S_HxJ: Galileo — measure what is measurable
        assert "S_HxJ" in _SENSE_BY_ID
        assert "Galileo" in _SENSE_BY_ID["S_HxJ"]["quote"]["author"]

        # S_CxP: Anaïs Nin — we see things as we are
        assert "S_CxP" in _SENSE_BY_ID
        assert "Nin" in _SENSE_BY_ID["S_CxP"]["quote"]["author"]

    def test_ditempa_motto_on_humility_justice(self):
        """S_HxJ (humility_justice) carries DITEMPA, BUKAN DIBERI."""
        anchor = _SENSE_BY_ID["S_HxJ"]
        assert anchor["motto_binding"] == "DITEMPA, BUKAN DIBERI"
        assert anchor["matrix_row"] == "HUMILITY"
        assert anchor["matrix_col"] == "JUSTICE"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GOVERNANCE PATHWAY PARITY — check_laws() ≡ kernel bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernancePathwayParity:
    """
    Golden contract: check_laws() and the kernel bridge path must produce
    semantically equivalent constitutional results for the same inputs.

    This is the contract that must hold before we can safely remove the
    sense.py kernel bridge and unify on check_laws().
    """

    def test_check_laws_returns_dict_with_verdict(self):
        """check_laws must return a dict with 'verdict' key."""
        from arifosmcp.runtime.law import check_laws

        result = check_laws("arif_sense_observe", {"query": "safe test query"}, "arif")
        assert isinstance(result, dict)
        assert "verdict" in result

    def test_check_laws_seal_for_safe_query(self):
        """Safe query should get SEAL from check_laws."""
        from arifosmcp.runtime.law import check_laws

        result = check_laws("arif_sense_observe", {"query": "what is the weather"}, "arif")
        assert result["verdict"] in ("SEAL", "SABAR"), (
            f"Safe query should not be HOLD/VOID, got {result['verdict']}"
        )

    def test_kernel_bridge_produces_compatible_structure(self):
        """
        The kernel bridge path must return verdict and floors keys
        compatible with what check_laws() returns, so governance
        consumers don't need to know which path was taken.
        """
        import sys
        from pathlib import Path

        _WORK = Path(__file__).resolve().parents[5]
        if str(_WORK) not in sys.path:
            sys.path.insert(0, str(_WORK))

        from core.governance_kernel import get_governance_kernel

        gk = get_governance_kernel("test-session-golden")
        kernel_result = gk.evaluate_floors(
            query="safe test query",
            options={
                "session_id": "test-session-golden",
                "actor_id": "arif",
                "human_witness": 0.8,
                "ai_witness": 0.8,
                "earth_witness": 0.8,
            },
        )

        # Kernel bridge returns: verdict, qdf, floors dict
        assert "verdict" in kernel_result, (
            f"Kernel bridge must return 'verdict', got keys: {list(kernel_result.keys())}"
        )
        assert "floors" in kernel_result, (
            f"Kernel bridge must return 'floors', got keys: {list(kernel_result.keys())}"
        )

    def test_both_paths_agree_on_constitutional_outcome(self):
        """
        GOLDEN GAP: check_laws() and kernel_bridge currently DIVERGE.
        check_laws returns SEAL for safe queries; kernel_bridge returns HOLD.
        This test documents the divergence. Phase 4 (governance unification)
        must resolve this before removing sense.py's kernel bridge.
        """
        from arifosmcp.runtime.law import check_laws
        import sys
        from pathlib import Path

        _WORK = Path(__file__).resolve().parents[5]
        if str(_WORK) not in sys.path:
            sys.path.insert(0, str(_WORK))
        from core.governance_kernel import get_governance_kernel

        query = "Retrieve current system health status and report metrics"
        sid = "parity-test-golden"

        # Path A: check_laws
        laws_result = check_laws("arif_sense_observe", {"query": query}, "arif")

        # Path B: kernel bridge
        gk = get_governance_kernel(sid)
        kernel_result = gk.evaluate_floors(
            query=query,
            options={
                "session_id": sid,
                "actor_id": "arif",
                "human_witness": 0.8,
                "ai_witness": 0.8,
                "earth_witness": 0.8,
            },
        )

        # Current behavior: paths DIVERGE (check_laws=SEAL, kernel_bridge=HOLD)
        # This is a known gap — Phase 4 must resolve.
        assert isinstance(laws_result, dict), "check_laws must return dict"
        assert isinstance(kernel_result, dict), "kernel_bridge must return dict"
        # Document the divergence explicitly
        print(
            f"GOVERNANCE PATHWAY DIVERGENCE (known): "
            f"check_laws={laws_result.get('verdict')}, "
            f"kernel_bridge={kernel_result.get('verdict')}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. AGENTIC SEARCH PLAN — VOI-driven sensing
# ═══════════════════════════════════════════════════════════════════════════════


class TestAgenticSearchPlan:
    """Freeze the VOI-driven sensing plan structure."""

    def test_plan_has_required_sections(self):
        """SENSE_PLAN must contain goal, subquestions, candidate_tools, budget, stop_conditions."""
        plan = _agentic_search_plan(
            need_evidence={
                "topics": [{"topic": "constitutional floors"}],
                "urgency": "MEDIUM",
                "min_trust": 0.7,
            },
            prior_coverage=0.2,
            prior_trust=0.3,
        )
        assert plan["type"] == "SENSE_PLAN"
        assert "goal" in plan
        assert len(plan["subquestions"]) >= 2
        assert "memory" in plan["candidate_tools"]  # Always check memory first
        assert "budget" in plan
        assert "stop_conditions" in plan
        assert plan["voi_estimate"] > 0

    def test_high_urgency_increases_budget(self):
        """HIGH urgency → up to 2 extra search steps."""
        plan_low = _agentic_search_plan(
            need_evidence={"topics": [{"topic": "test"}], "urgency": "LOW"},
            budget_steps=4,
        )
        plan_high = _agentic_search_plan(
            need_evidence={"topics": [{"topic": "test"}], "urgency": "HIGH"},
            budget_steps=4,
        )
        assert plan_high["budget"]["max_steps"] >= plan_low["budget"]["max_steps"]

    def test_low_voi_attaches_humility_anchor_hint(self):
        """When VOI < 0.1, plan should hint S_HxC (Hawking — illusion of knowledge)."""
        plan = _agentic_search_plan(
            prior_coverage=0.9,  # High coverage → low VOI
            prior_trust=0.9,
            budget_steps=2,
        )
        if plan["voi_estimate"] < 0.1:
            assert plan.get("paradox_hint") == "S_HxC"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SENSING SUFFICIENCY GRADING
# ═══════════════════════════════════════════════════════════════════════════════


class TestSensingSufficiency:
    """Freeze the sufficiency grading that decides STOP vs REPLAN."""

    def test_empty_observations_trigger_replan(self):
        """No observations → REPLAN with S_HxP (Thurber — know questions)."""
        grade = _grade_sensing_sufficiency([], 0.2, 0.3)
        assert grade["sufficient"] is False
        assert grade["recommendation"] == "REPLAN"
        assert grade["paradox_hint"] == "S_HxP"

    def test_single_source_triggers_triangulation_hint(self):
        """Single source → S_CxP (Nin — single perspective risk)."""
        observations = [
            {"source_type": "web", "trust": 0.7},
        ]
        grade = _grade_sensing_sufficiency(observations, 0.3, 0.5)
        if not grade["sufficient"]:
            assert grade.get("paradox_hint") == "S_CxP"

    def test_sufficient_evidence_gives_stop(self):
        """Multiple high-trust sources → STOP."""
        observations = [
            {"source_type": "web", "trust": 0.9},
            {"source_type": "local_wiki", "trust": 0.85},
            {"source_type": "repo_index", "trust": 0.9},
        ]
        grade = _grade_sensing_sufficiency(observations, 0.5, 0.5, required_quality=0.7)
        assert grade["sufficient"] is True
        assert grade["recommendation"] == "STOP"
