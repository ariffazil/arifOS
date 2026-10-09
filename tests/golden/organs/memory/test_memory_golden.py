"""
tests/golden/organs/memory/test_memory_golden.py — 555_MEMORY Golden Contract Tests

Phase 0: Freeze provenance gate (Bacon — knowledge is power → restraint),
recall classification, memory bloat ratio, MoBA block gate,
and paradox anchor injection at coverage gap detection.

Constitutional risk: MODERATE. Memory is the recall substrate.
Its provenance gate is a hard gate for downstream SEAL/MUTATE tools.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from arifosmcp.tools.memory import (
    _MEMORY_BY_CELL,
    _MEMORY_BY_ID,
    MEMORY_PARADOX_ANCHORS,
    _classify_recall_result,
    _compute_memory_bloat,
    _compute_memory_confidence,
    _memory_block_gate,
    _memory_provenance_gate,
)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PARADOX ANCHOR REGISTRY — 9 anchors
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryAnchorRegistry:
    """Freeze the 9 Memory paradox anchors."""

    def test_nine_anchors_exist(self):
        """Memory must have exactly 9 paradox anchors."""
        assert len(MEMORY_PARADOX_ANCHORS) == 9

    def test_golden_anchor_ids(self):
        """Verify key Memory anchors exist with correct quotes."""
        # M_TxJ: Bacon — knowledge is power
        assert "M_TxJ" in _MEMORY_BY_ID
        assert "Bacon" in _MEMORY_BY_ID["M_TxJ"]["quote"]["author"]
        assert _MEMORY_BY_ID["M_TxJ"]["severity_on_fire"] == "hard_gate"

        # M_HxJ: Socrates — I am wiser than this man
        assert "M_HxJ" in _MEMORY_BY_ID
        assert "Socrates" in _MEMORY_BY_ID["M_HxJ"]["quote"]["author"]

        # M_TxP: Plato — knowledge differs from correct opinion
        assert "M_TxP" in _MEMORY_BY_ID
        assert "Plato" in _MEMORY_BY_ID["M_TxP"]["quote"]["author"]

        # M_HxC: Borges — to think is to forget
        assert "M_HxC" in _MEMORY_BY_ID
        assert "Borges" in _MEMORY_BY_ID["M_HxC"]["quote"]["author"]

    def test_all_cells_and_ids_resolve(self):
        """Every anchor must resolve by both cell and ID."""
        for anchor in MEMORY_PARADOX_ANCHORS:
            assert anchor["id"] in _MEMORY_BY_ID
            assert anchor["matrix_cell"] in _MEMORY_BY_CELL


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BACON PROVENANCE GATE — M_TxJ: Knowledge is power → restraint
# ═══════════════════════════════════════════════════════════════════════════════


class TestProvenanceGate:
    """
    Freeze the M_TxJ Bacon Gate: unverified evidence must not authorize
    high-agency (ADJUDICATE, SEAL, MUTATE) actions.
    """

    def test_verified_evidence_passes_for_adjudicate(self):
        """Verified evidence must pass the provenance gate for ADJUDICATE tools."""
        evidence = {
            "provenance": "verified",
            "can_treat_as_proof": True,
        }
        result = _memory_provenance_gate(evidence, target_tool_class="ADJUDICATE")
        assert result["passed"] is True
        assert result["blocked"] is False

    def test_unverified_evidence_blocked_for_seal(self):
        """Unverified evidence must be BLOCKED for SEAL-class tools."""
        evidence = {
            "provenance": "suggested",
            "can_treat_as_proof": False,
        }
        result = _memory_provenance_gate(evidence, target_tool_class="SEAL")
        assert result["passed"] is False
        assert result["blocked"] is True
        assert "M_TxJ" in result.get("paradox_anchor", {}).get("id", "")
        assert "BACON" in result["reason"]  # Reason says "BACON GATE" (all caps)

    def test_all_high_agency_classes_blocked_for_unverified(self):
        """ADJUDICATE, SEAL, and MUTATE must all block unverified evidence."""
        unverified = {"provenance": "remembered", "can_treat_as_proof": False}
        for tool_class in ("ADJUDICATE", "SEAL", "MUTATE"):
            result = _memory_provenance_gate(unverified, target_tool_class=tool_class)
            assert result["blocked"] is True, (
                f"{tool_class} should block unverified evidence"
            )

    def test_readonly_tools_never_blocked(self):
        """OBSERVE and READ tools must never block — provenance gate is for writes only."""
        evidence = {"provenance": "remembered", "can_treat_as_proof": False}
        result = _memory_provenance_gate(evidence, target_tool_class="OBSERVE")
        assert result["passed"] is True
        assert result.get("blocked") is not True


# ═══════════════════════════════════════════════════════════════════════════════
# 3. RECALL CLASSIFICATION — Provenance states
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecallClassification:
    """Freeze the _classify_recall_result provenance classification."""

    def test_null_content_is_quarantined(self):
        """Memory with null/empty text → quarantined, not usable."""
        record = {
            "text": "",
            "content": None,
            "tier": "canon",
            "phoenix_state": "active",
            "phoenix_tri_witness": {},
            "phoenix_anti_hantu_flag": False,
            "f4_conflicts_count": 0,
        }
        result = _classify_recall_result(record)
        assert result["classification"]["quarantined"] is True
        assert result["usable"] is False
        assert result["tier"] == "quarantine"

    def test_sealed_sacred_is_verified_and_sealed(self):
        """Sacred tier + sealed state + not quarantined → sealed classification."""
        record = {
            "text": "Constitutional verdict: SEAL",
            "content": "Constitutional verdict: SEAL",
            "tier": "sacred",
            "phoenix_state": "sealed",
            "phoenix_tri_witness": {"human": 0.5, "ai": 0.5, "earth": 0.5},
            "phoenix_anti_hantu_flag": False,
            "f4_conflicts_count": 0,
        }
        result = _classify_recall_result(record)
        assert result["classification"]["verified"] is True
        assert result["classification"]["sealed"] is True
        assert result["can_treat_as_proof"] is True
        assert result["provenance"] == "verified"

    def test_contradiction_hold_is_contradicted(self):
        """Memory with contradiction_hold → contradicted, but still verified."""
        record = {
            "text": "Some claim that conflicts",
            "content": "Some claim that conflicts",
            "tier": "canon",
            "phoenix_state": "contradiction_hold",
            "phoenix_tri_witness": {"human": 0.5, "ai": 0.5, "earth": 0.5},
            "phoenix_anti_hantu_flag": False,
            "f4_conflicts_count": 1,
        }
        result = _classify_recall_result(record)
        assert result["classification"]["contradicted"] is True
        assert result["classification"]["verified"] is True  # tri_witness complete
        assert result["can_treat_as_proof"] is False  # contradicted overrides

    def test_constructed_text_from_payload(self):
        """
        When text is null, Qdrant payload fields construct synthetic text in
        a local variable (not written back to record["text"]). The record is
        NOT quarantined because the local synthetic text passes the null check.
        """
        record = {
            "text": None,
            "content": None,
            "verdict": "SEAL",
            "source": "arifos_session_init",
            "session_id": "sess-golden-001",
            "tier": "canon",
        }
        result = _classify_recall_result(record)
        assert result.get("_constructed_text") is True
        assert result["usable"] is True
        assert result["classification"]["quarantined"] is False

    def test_semantic_search_result_is_inferred(self):
        """Result with a score → inferred classification."""
        record = {
            "text": "Found via semantic search",
            "score": 0.85,
            "tier": "canon",
            "phoenix_state": "active",
            "phoenix_tri_witness": {},
            "phoenix_anti_hantu_flag": False,
            "f4_conflicts_count": 0,
        }
        result = _classify_recall_result(record)
        assert result["classification"]["inferred"] is True
        assert result["provenance"] == "suggested"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. MEMORY BLOAT — M_b = N_retrieved / (N_used + ε)
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryBloat:
    """Freeze the M_b bloat ratio thresholds."""

    def test_tight_retrieval(self):
        """When retrieved ≈ used → M_b < 2.0 → tight."""
        mb = _compute_memory_bloat(retrieved_count=5, used_in_trace=5)
        assert mb < 2.0, f"Tight retrieval should have M_b < 2.0, got {mb}"

    def test_bloated_retrieval(self):
        """Many retrieved, few used → M_b high → bloated."""
        mb = _compute_memory_bloat(retrieved_count=50, used_in_trace=3)
        assert mb > 5.0, f"Bloated retrieval should have M_b > 5.0, got {mb}"

    def test_zero_used_handled(self):
        """Division by zero avoided via ε."""
        mb = _compute_memory_bloat(retrieved_count=10, used_in_trace=0)
        assert mb > 0  # Should not error, ε prevents division by zero


# ═══════════════════════════════════════════════════════════════════════════════
# 5. MOBA BLOCK GATE — Block-gated memory retrieval
# ═══════════════════════════════════════════════════════════════════════════════


class TestMoBABlockGate:
    """Freeze the MoBA-style block-gated retrieval."""

    def test_high_risk_triggers_full_scan(self):
        """High-risk queries → search all blocks (empty = full scan)."""
        blocks = _memory_block_gate("irreversible operation", risk_level="high")
        assert blocks == []  # Empty = search all

    def test_relevant_blocks_selected(self):
        """Matching tags → blocks selected."""
        available = [
            {"block_id": "b1", "tags": ["constitutional", "floors"], "topic": "F1 Amanah", "age_hours": 1, "avg_trust": 0.9},
            {"block_id": "b2", "tags": ["health", "metrics"], "topic": "system health", "age_hours": 200, "avg_trust": 0.5},
        ]
        selected = _memory_block_gate("constitutional floors question", available, top_k=2)
        assert "b1" in selected  # Tag match + recency + high trust

    def test_low_score_blocks_filtered(self):
        """Blocks with score ≤ 0.2 are excluded."""
        available = [
            {"block_id": "irrelevant", "tags": ["unrelated"], "topic": "nothing", "age_hours": 500, "avg_trust": 0.1},
        ]
        selected = _memory_block_gate("constitutional question", available)
        assert "irrelevant" not in selected


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MEMORY CONFIDENCE — 4-plane calibrated confidence
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryConfidence:
    """Freeze the 4-plane confidence computation."""

    def test_empty_results_gives_zero_integrity(self):
        """No results → 0 content integrity, 0 reasoning authority."""
        conf = _compute_memory_confidence([])
        assert conf["retrieval_relevance"] == 0.0
        assert conf["content_integrity"] == 0.0
        assert conf["reasoning_authority"] == 0.0

    def test_all_usable_gives_high_integrity(self):
        """All results usable → content_integrity = 1.0."""
        results = [
            {"usable": True, "score": 0.9},
            {"usable": True, "score": 0.85},
        ]
        conf = _compute_memory_confidence(results, backend_ok=True)
        assert conf["backend_confidence"] == 0.85
        assert conf["content_integrity"] == 1.0
        assert conf["retrieval_relevance"] > 0.8

    def test_mixed_usable_and_quarantined(self):
        """Some quarantined → reduced content integrity."""
        results = [
            {"usable": True, "score": 0.9},
            {"usable": False, "score": 0.0},
        ]
        conf = _compute_memory_confidence(results, backend_ok=True)
        assert conf["content_integrity"] == 0.5
        assert conf["reasoning_authority"] < 0.5

    def test_backend_unavailable_kills_confidence(self):
        """Backend unavailable → backend_confidence = 0."""
        conf = _compute_memory_confidence([], backend_ok=False)
        assert conf["backend_confidence"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# 7. ECHO/PaW — Score Prediction + Delta Threshold Interrupt (2026-07-21)
# ═══════════════════════════════════════════════════════════════════════════════


class TestScorePredictionDeltaThreshold:
    """F1/F2 DELTA BREACH circuit breaker in _handle_score_prediction."""

    def test_score_prediction_handler_exists(self):
        """_handle_score_prediction must be importable."""
        from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
            _handle_score_prediction,
        )

        assert _handle_score_prediction is not None

    def test_score_prediction_requires_seal_entry_id(self):
        """Missing seal_entry_id → VOID verdict."""
        import asyncio

        from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
            _handle_score_prediction,
        )

        result = asyncio.run(_handle_score_prediction({}, ctx=None))
        assert result["verdict"] == "VOID"
        assert "requires seal_entry_id" in str(result["payload"].get("note", ""))

    def test_score_prediction_with_catastrophic_delta_returns_hold(self):
        """Observation completely contradicts prediction → HOLD verdict, not SEAL."""
        import asyncio

        from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
            _handle_score_prediction,
        )

        # Payload with completely mismatched prediction vs observation
        payload = {
            "seal_entry_id": "seal-test-001",
            "observed_state": {
                "well_score": 20,      # prediction was 80 → massive delta
                "human_ready": "DEGRADED",
                "clarity": 1.0,
                "runtime_drift": True,
                "floors_checked": ["F1"],
                "floors_violated": ["F1", "F2", "F3"],
            },
        }
        # We need predicted_state from a seal entry which won't exist in test
        # So this will have NO_PREDICTED_STATE flag → aggregate_score = 0.0 → HOLD
        result = asyncio.run(_handle_score_prediction(payload, ctx=None))
        assert result["verdict"] == "HOLD"
        assert result["payload"]["hold_type"] == "F1_F2_DELTA_BREACH"
        assert "F1_AMANAH_RISK" in result["payload"]["flags"]
        assert "F2_TRUTH_EPISTEMIC_FAILURE" in result["payload"]["flags"]
        assert result["payload"]["aggregate_score"] < 0.70

    def test_score_prediction_with_no_predicted_state_returns_hold(self):
        """No predicted_state available → aggregate 0.0 → HOLD circuit breaker."""
        import asyncio

        from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
            _handle_score_prediction,
        )

        payload = {
            "seal_entry_id": "seal-nonexistent-999",
            "observed_state": {
                "well_score": 80,
                "human_ready": "OPTIMAL",
                "clarity": 8.0,
            },
        }
        result = asyncio.run(_handle_score_prediction(payload, ctx=None))
        # No seal entry found → aggregate_score = 0.0 → HOLD
        assert result["verdict"] == "HOLD"
        assert result["payload"]["hold_type"] == "F1_F2_DELTA_BREACH"
        assert "NO_PREDICTED_STATE" in result["payload"]["flags"]

    def test_score_prediction_hold_payload_contains_next_action(self):
        """HOLD verdict must specify SOVEREIGN_OVERRIDE_REQUIRED as next action."""
        import asyncio

        from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
            _handle_score_prediction,
        )

        payload = {
            "seal_entry_id": "seal-nonexistent-999",
            "observed_state": {"well_score": 80},
        }
        result = asyncio.run(_handle_score_prediction(payload, ctx=None))
        assert result["verdict"] == "HOLD"
        assert "SOVEREIGN_OVERRIDE_REQUIRED" in result["payload"]["next_action"]
        assert "escalate" in result["payload"]["next_action"]

    def test_score_prediction_mode_registered(self):
        """score_prediction must be in ARIF_MEMORY_MODES."""
        from arifosmcp.runtime.megaTools.tool_13_arif_memory import ARIF_MEMORY_MODES

        assert "score_prediction" in ARIF_MEMORY_MODES

    def test_score_prediction_has_f1_f2_pre_floors(self):
        """score_prediction must require L01 (F1 AMANAH) and L02 (F2 TRUTH) pre-floors."""
        from arifosmcp.runtime.megaTools.tool_13_arif_memory import MODE_PRE_FLOORS

        floors = MODE_PRE_FLOORS["score_prediction"]
        assert "L01" in floors, "F1 AMANAH pre-floor required for score_prediction"
        assert "L02" in floors, "F2 TRUTH pre-floor required for score_prediction"
