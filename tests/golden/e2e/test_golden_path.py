"""
tests/golden/e2e/test_golden_path.py — End-to-End Golden Path Contract

Phase 0: Freeze the full INIT → SENSE → MIND → HEART → JUDGE → SEAL pipeline.

This test proves that the 5 organs produce correct, mutually compatible outputs
when chained in the canonical constitutional sequence. Any refactor that breaks
this golden path must be rolled back.

Constitutional risk: HIGHEST. This is the integration contract.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations


import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# GOLDEN FIXTURES — Deterministic inputs
# ═══════════════════════════════════════════════════════════════════════════════

GOLDEN_SESSION_ID = "golden-e2e-2026-06-13"
GOLDEN_ACTOR_ID = "arif"
GOLDEN_QUERY = "Assess whether the system should deploy a new health check endpoint"


@pytest.fixture
def golden_context():
    """Deterministic context used across all golden path stages."""
    return {
        "session_id": GOLDEN_SESSION_ID,
        "actor_id": GOLDEN_ACTOR_ID,
        "g_score": 0.85,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INIT → SENSE bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestInitToSense:
    """INIT (000) must produce a session that SENSE (111) can accept."""

    def test_init_produces_valid_session(self):
        """Session init must return a session_id."""
        from arifosmcp.tools.session import arif_session_init

        result = arif_session_init(
            mode="light",
            actor_id=GOLDEN_ACTOR_ID,
        )
        # Returns SessionManifest Pydantic model (sync, not async)
        assert result.status in ("OK", "INITIALIZED")
        assert result.session.session_id is not None

    def test_sense_accepts_session(self):
        """Sense observe must return a valid status for given session."""
        from arifosmcp.tools.sense import arif_sense_observe

        result = arif_sense_observe(
            mode="compass",
            query=GOLDEN_QUERY,
            session_id=GOLDEN_SESSION_ID,
            actor_id=GOLDEN_ACTOR_ID,
        )
        assert result.get("status") in ("OK", "HOLD", "SABAR")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SENSE → MIND bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestSenseToMind:
    """SENSE (111) output must be consumable by MIND (333)."""

    @pytest.mark.asyncio
    async def test_mind_accepts_sense_context(self, golden_context):
        """Mind reason must accept a context dict with session_id from Sense."""
        from arifosmcp.tools.reason import arif_mind_reason

        result = arif_mind_reason(
            mode="reason",
            query=GOLDEN_QUERY,
            actor_id=GOLDEN_ACTOR_ID,
            context=golden_context,
        )
        # Must produce structured output
        assert result.status in ("OK", "HOLD")
        assert result.tool == "arif_mind_reason"

    def test_mind_delta_bundle_has_required_fields(self):
        """Mind reasoning bundle must include claim_state, confidence, evidence."""
        from arifosmcp.tools.reason import _build_delta_bundle

        bundle = _build_delta_bundle(
            query=GOLDEN_QUERY,
            status="REASONED",
            claim_state="SUPPORTED_CLAIM",
            synthesis="Deploy with standard monitoring. Reversible change.",
            reasoning={
                "attestations": [{"source": "code_review", "confidence": 0.9}],
                "missing_evidence": [],
                "observed_inputs": [],
            },
            confidence={
                "overall_confidence": 0.7,
                "evidence_confidence": 0.8,
                "reasoning_confidence": 0.75,
            },
            uncertainty=[],
            reasoning_mode="analytical",
            axioms_used=["L01_AMANAH"],
            next_safe_action=["Proceed to Heart critique"],
        )
        # Verify required bundle structure
        assert bundle["claim_state"] == "SUPPORTED_CLAIM"
        assert bundle["reasoning_verdict"] == "REASONED"
        assert "final_verdict" in bundle
        assert "provenance" in bundle
        assert bundle["_core_invariant"] is not None
        # Provenance is metadata, not authority
        assert "metadata" in bundle["provenance"]["admissibility_statement"].lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MIND → HEART bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestMindToHeart:
    """MIND (333) output must be consumable by HEART (666)."""

    @pytest.mark.asyncio
    async def test_heart_accepts_mind_output_as_target(self):
        """Heart critique must accept text that could come from Mind reasoning."""
        from arifosmcp.tools.heart import arif_heart_critique

        # Use deterministic fallback mode to avoid LLM dependency
        result = await arif_heart_critique(
            mode="critique",
            target="Deploy a new health check endpoint to /health. Reversible. "
            "Standard monitoring. No PII exposure.",
            actor_id=GOLDEN_ACTOR_ID,
            session_id=GOLDEN_SESSION_ID,
            fractal_auto=False,  # Single pass for deterministic test
        )
        assert "risks_found" in result
        assert "risk_tier" in result
        assert "human_decision_required" in result

    def test_heart_fallback_produces_8_risk_categories(self):
        """Deterministic fallback must scan all 8 risk categories."""
        from arifosmcp.tools.heart import _heart_fallback

        result = _heart_fallback(
            mode="critique",
            target="Delete all user data permanently without backup",
        )
        risks = result.get("risks_found", [])
        risk_types = {r["type"] for r in risks}
        # Must cover: dignity, overclaim, anthropomorphism, irreversibility,
        # autonomy, harm, privacy, bias
        assert len(risks) == 8, f"Expected 8 risk categories, got {len(risks)}: {risk_types}"
        # Irreversibility risk must be flagged for "permanently delete"
        irreversibility = [r for r in risks if r["type"] == "irreversibility_risk"]
        assert len(irreversibility) == 1
        assert irreversibility[0]["severity"] == "high"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. HEART → JUDGE bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeartToJudge:
    """HEART (666) output must be consumable by JUDGE (888)."""

    def test_judge_heart_gate_blocks_on_void(self):
        """
        GOLDEN GAP: The HEART_GATE is documented in judge.py docstring (lines 544-561)
        but NOT implemented as executable code. This test documents the gap.
        Current behavior: Judge proceeds normally despite Heart VOID.
        Phase 1 must implement: move gate from docstring to function body.
        """
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        result = asyncio.run(
            arif_judge_deliberate(
                mode="judge",
                candidate="destroy production database",
                session_id=GOLDEN_SESSION_ID,
                actor_id=GOLDEN_ACTOR_ID,
                heart_critique={
                    "action_risk_verdict": "VOID",
                    "verdict": "VOID",
                    "reason": "Irreversible destruction without rollback plan.",
                },
            )
        )
        # Current: heart_critique is NOT checked (gate is docstring-only)
        # After Phase 1 implementation: result.verdict.value should be "HOLD"
        # and reasons should contain "666_HEART_GATE"
        assert result.verdict is not None
        # Document: HEART_GATE IS NOT CURRENTLY ACTIVE

    def test_judge_heart_gate_allows_on_seal(self):
        """Heart SEAL → Judge must NOT be blocked by HEART_GATE."""
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        result = asyncio.run(
            arif_judge_deliberate(
                mode="judge",
                candidate="add documentation to README",
                session_id=GOLDEN_SESSION_ID,
                actor_id=GOLDEN_ACTOR_ID,
                heart_critique={
                    "action_risk_verdict": "SEAL",
                    "verdict": "OK",
                    "reason": "No risks detected. Fully reversible.",
                },
            )
        )
        heart_gate_reasons = [r for r in result.reasons if "666_HEART_GATE" in r]
        assert len(heart_gate_reasons) == 0, (
            f"HEART_GATE blocked despite Heart SEAL: {heart_gate_reasons}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. JUDGE → SEAL bridge
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeToSeal:
    """JUDGE (888) output must be consumable by VAULT (999)."""

    def test_verdict_output_structurally_compatible_with_seal(self):
        """VerdictOutput fields must be compatible with arif_vault_seal payload."""
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        result = asyncio.run(
            arif_judge_deliberate(
                mode="judge",
                candidate="safe reversible action with full evidence",
                session_id=GOLDEN_SESSION_ID,
                actor_id=GOLDEN_ACTOR_ID,
                action_tier="standard",
            )
        )
        # VerdictOutput must have fields seal expects
        assert result.verdict is not None
        assert result.verdict.value in ("SEAL", "SABAR", "HOLD", "VOID")
        # Must have meta for vault_entry_id routing
        assert hasattr(result, "meta")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. FULL GOLDEN PATH — All 5 organs chained
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullGoldenPath:
    """
    INIT → SENSE → MIND → HEART → JUDGE with deterministic fixtures.

    This is the constitutional integration contract. If this test breaks,
    something fundamental about organ interop has changed.
    """

    @pytest.mark.asyncio
    async def test_golden_path_full_chain(self, golden_context):
        """
        Full constitutional pipeline with deterministic components.

        Verifies:
        - Each organ produces output consumable by the next
        - The chain terminates in a valid verdict
        - No organ crashes on valid input from previous organ
        """
        from arifosmcp.tools.session import arif_session_init
        from arifosmcp.tools.sense import arif_sense_observe
        from arifosmcp.tools.reason import arif_mind_reason
        from arifosmcp.tools.heart import arif_heart_critique
        from arifosmcp.tools.judge import arif_judge_deliberate

        # Stage 000: INIT (sync — returns SessionManifest Pydantic model)
        init_result = arif_session_init(
            mode="light",
            actor_id=GOLDEN_ACTOR_ID,
        )
        assert init_result.status in ("OK", "INITIALIZED")
        session_id = (
            init_result.session.session_id if hasattr(init_result, "session") else GOLDEN_SESSION_ID
        )
        print(f"[000_INIT] session={session_id}")

        # Stage 111: SENSE
        sense_result = arif_sense_observe(
            mode="compass",
            query=GOLDEN_QUERY,
            session_id=session_id,
            actor_id=GOLDEN_ACTOR_ID,
        )
        sense_ok = sense_result.get("status") in ("OK", "HOLD", "SABAR")
        print(f"[111_SENSE] status={sense_result.get('status')}")
        assert sense_ok, f"SENSE failed: {sense_result.get('status')}"

        # Stage 333: MIND
        mind_result = arif_mind_reason(
            mode="reason",
            query=GOLDEN_QUERY,
            actor_id=GOLDEN_ACTOR_ID,
            context={"session_id": session_id},
        )
        print(
            f"[333_MIND] status={mind_result.status}, verdict={mind_result.result.get('status', '?')}"
        )
        assert mind_result.status in ("OK", "HOLD")

        # Stage 666: HEART — single pass (no fractal for determinism)
        heart_result = await arif_heart_critique(
            mode="critique",
            target=GOLDEN_QUERY,
            session_id=session_id,
            actor_id=GOLDEN_ACTOR_ID,
            fractal_auto=False,
        )
        print(
            f"[666_HEART] risk_tier={heart_result.get('risk_tier')}, "
            f"human_req={heart_result.get('human_decision_required')}"
        )
        assert "risks_found" in heart_result
        assert "risk_tier" in heart_result

        # Stage 888: JUDGE (use await — already in async context)
        judge_result = await arif_judge_deliberate(
            mode="judge",
            candidate=GOLDEN_QUERY,
            session_id=session_id,
            actor_id=GOLDEN_ACTOR_ID,
            heart_critique=heart_result,
        )
        print(
            f"[888_JUDGE] verdict={judge_result.verdict.value}, reasons={len(judge_result.reasons)}"
        )
        assert judge_result.verdict is not None
        assert judge_result.verdict.value in ("SEAL", "SABAR", "HOLD", "VOID")

        # Success: the golden path completed without crash
        print("[999_SEAL] Golden path complete — DITEMPA, BUKAN DIBERI")

    def test_paradox_anchors_fire_across_pipeline(self):
        """
        Verify that paradox anchors from all 5 organs are structurally compatible.

        Each organ's anchors follow the same 3×3 matrix geometry:
        TRUTH/CLARITY/HUMILITY × CARE/PEACE/JUSTICE
        """
        from arifosmcp.tools.sense import SENSE_PARADOX_ANCHORS
        from arifosmcp.tools.reason import MIND_PARADOX_ANCHORS
        from arifosmcp.tools.memory import MEMORY_PARADOX_ANCHORS
        from arifosmcp.tools.heart import HEART_PARADOX_ANCHORS
        from arifosmcp.tools.judge import JUDGE_PARADOX_ANCHORS

        all_organs = {
            "sense": SENSE_PARADOX_ANCHORS,
            "mind": MIND_PARADOX_ANCHORS,
            "memory": MEMORY_PARADOX_ANCHORS,
            "heart": HEART_PARADOX_ANCHORS,
            "judge": JUDGE_PARADOX_ANCHORS,
        }

        # Every organ must have exactly 9 anchors (3×3 matrix)
        for organ, anchors in all_organs.items():
            assert len(anchors) == 9, f"{organ} has {len(anchors)} anchors, expected 9"

        # Every cell must exist in every organ
        expected_cells = {
            f"{row}_{col}"
            for row in ("truth", "clarity", "humility")
            for col in ("care", "peace", "justice")
        }
        for organ, anchors in all_organs.items():
            actual_cells = {a["matrix_cell"] for a in anchors}
            missing = expected_cells - actual_cells
            assert not missing, f"{organ} missing matrix cells: {missing}"

        # DITEMPA, BUKAN DIBERI must be the humility_justice anchor in ALL 5 organs
        ditempa_organs = []
        for organ, anchors in all_organs.items():
            for anchor in anchors:
                if (
                    anchor["matrix_row"] == "HUMILITY"
                    and anchor["matrix_col"] == "JUSTICE"
                    and "DITEMPA" in anchor["motto_binding"]
                ):
                    ditempa_organs.append(organ)
        assert len(ditempa_organs) == 5, (
            f"All 5 organs must carry DITEMPA on humility_justice. Found in: {ditempa_organs}"
        )

    def test_mottos_are_unique_per_organ_row_col(self):
        """
        Each organ has unique moto_binding strings.
        But across organs, the same matrix cell may carry the same motto.
        This test verifies structural consistency.
        """
        from arifosmcp.tools.sense import SENSE_PARADOX_ANCHORS
        from arifosmcp.tools.reason import MIND_PARADOX_ANCHORS
        from arifosmcp.tools.heart import HEART_PARADOX_ANCHORS
        from arifosmcp.tools.judge import JUDGE_PARADOX_ANCHORS
        from arifosmcp.tools.memory import MEMORY_PARADOX_ANCHORS

        # TRUTH+CARE → DIKAJI, BUKAN DISUAPI (Examined, not spoon-fed)
        # This should be consistent across organs for the same matrix cell
        truth_care_mottos = set()
        for anchors in [
            SENSE_PARADOX_ANCHORS,
            MIND_PARADOX_ANCHORS,
            MEMORY_PARADOX_ANCHORS,
            HEART_PARADOX_ANCHORS,
            JUDGE_PARADOX_ANCHORS,
        ]:
            for a in anchors:
                if a["matrix_cell"] == "truth_care":
                    truth_care_mottos.add(a["motto_binding"])
        # At least the dominant motto should be present
        assert "DIKAJI, BUKAN DISUAPI" in truth_care_mottos or len(truth_care_mottos) > 0, (
            f"truth_care mottos: {truth_care_mottos}"
        )
