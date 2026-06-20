"""
tests/golden/organs/heart/test_heart_golden.py — 666_HEART Golden Contract Tests

Phase 0: Freeze fractal recursion depth boundaries, desensitization thresholds,
MIN_TRUST merge behavior, and recursion clamp semantics.

Constitutional risk: HIGH. Heart is the ethical gate before Judge.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations


from arifosmcp.tools.heart import (
    _fractal_critique_stage,
    _fractal_stabilization_gain,
    _merge_fractal_results,
    _compute_critique_humility_penalty,
    _compute_omega_state,
    _inject_heart_paradox,
)
from arifosmcp.paradox.desensitization import check_desensitization, _clear_fire_log


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FRACTAL CRITIQUE STAGE — Recursion depth → paradox anchor mapping
# ═══════════════════════════════════════════════════════════════════════════════


class TestFractalCritiqueStage:
    """Freeze the recursion depth → stage mapping that governs fractal critique."""

    def test_depth_0_is_primary_critique_truth_row(self):
        """N=1 (depth=0): Primary critique of TARGET → TRUTH row."""
        stage = _fractal_critique_stage(0)
        assert stage["stage"] == "primary_critique"
        assert stage["lens"] == "TRUTH"
        assert stage["paradox_id"] == "H_TxC"
        assert stage["paradox_cell"] == "truth_care"

    def test_depth_1_is_meta_critique_clarity_row(self):
        """N=2 (depth=1): Critique the LEVEL-1 CRITIQUE → CLARITY row."""
        stage = _fractal_critique_stage(1)
        assert stage["stage"] == "meta_critique"
        assert stage["lens"] == "CLARITY"
        assert stage["paradox_id"] == "H_CxC"
        assert stage["paradox_cell"] == "clarity_care"
        # Verify Matthew 7:1-2 anchor
        assert "Fair" in stage["question"] or "fair" in stage["question"]

    def test_depth_2_is_meta_meta_critique_humility_row(self):
        """N=3 (depth=2): Critique the PROCESS → HUMILITY row."""
        stage = _fractal_critique_stage(2)
        assert stage["stage"] == "meta_meta_critique"
        assert stage["lens"] == "HUMILITY"
        assert stage["paradox_id"] == "H_HxC"
        assert stage["paradox_cell"] == "humility_care"

    def test_depth_3_and_beyond_clamped(self):
        """Depth ≥ 3 → RECURSION_DEPTH_CLAMPED."""
        for depth in (3, 5, 10, 100):
            stage = _fractal_critique_stage(depth)
            assert stage["stage"] == "recursion_clamped", (
                f"Depth {depth} should be clamped, got {stage['stage']}"
            )
            assert "CLAMPED" in stage["question"]
            assert stage["paradox_id"] == "H_HxJ"  # Malay proverb — one drop ruins the milk


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FRACTAL STABILIZATION GAIN — G_f = Q_N - Q_{N-1}
# ═══════════════════════════════════════════════════════════════════════════════


class TestFractalStabilizationGain:
    """Freeze the G_f convergence metric that detects when recursion stops helping."""

    def test_identical_results_produce_empathy_stability_baseline(self):
        """
        Golden: Identical results produce G_f = 0.3 (empathy stability baseline).
        The formula is: G_f = 0.3*(1-empathy_change) + 0.4*novel_risks + 0.3*uncertainty_delta.
        For identical results: empathy_change=0 → 0.3*1.0=0.3, novel_risks=0, uncertainty_delta=0.
        Total: 0.3. This is the baseline — identical critiques still have stability value.
        """
        result = {
            "empathy_score": 0.8,
            "risks_found": [{"type": "harm", "severity": "medium"}],
            "_envelope": {"uncertainty": ["gap1"]},
        }
        g_f = _fractal_stabilization_gain(result, result)
        assert g_f == 0.3, (
            f"Identical results baseline G_f should be 0.3 (empathy stability), got {g_f}"
        )

    def test_new_risk_types_produce_positive_gain(self):
        """Finding new risk types → positive G_f."""
        prev = {
            "empathy_score": 0.8,
            "risks_found": [{"type": "harm", "severity": "medium"}],
            "_envelope": {"uncertainty": ["gap1", "gap2"]},
        }
        curr = {
            "empathy_score": 0.7,
            "risks_found": [
                {"type": "harm", "severity": "medium"},
                {"type": "dignity", "severity": "high"},
                {"type": "privacy", "severity": "high"},
            ],
            "_envelope": {"uncertainty": ["gap1"]},
        }
        g_f = _fractal_stabilization_gain(prev, curr)
        assert g_f > 0, f"New risk types should give positive G_f, got {g_f}"

    def test_worsening_empathy_produces_negative_gain(self):
        """If empathy drops sharply without finding new risks, G_f can be negative."""
        prev = {
            "empathy_score": 0.9,
            "risks_found": [{"type": "harm", "severity": "low"}],
            "_envelope": {"uncertainty": ["gap1"]},
        }
        curr = {
            "empathy_score": 0.3,  # Big drop
            "risks_found": [{"type": "harm", "severity": "low"}],  # No new risks
            "_envelope": {"uncertainty": ["gap1", "gap2"]},  # More uncertainty
        }
        g_f = _fractal_stabilization_gain(prev, curr)
        # Empathy drop + no new risks + more uncertainty → likely negative
        assert g_f <= 0, (
            f"Worsening empathy without new risks should give G_f ≤ 0, got {g_f}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MIN_TRUST — Fractal merge with most conservative wins
# ═══════════════════════════════════════════════════════════════════════════════


class TestMinTrustMerge:
    """Freeze the MIN_TRUST merge rule across fractal recursion levels."""

    def test_empty_results_return_hold(self):
        """No results → HOLD with empty risks."""
        merged = _merge_fractal_results([], [], max_depth=3)
        assert merged["status"] == "HOLD"
        assert merged["risks_found"] == []
        assert merged["human_decision_required"] is True

    def test_single_result_passes_through(self):
        """Single result → merged is that result with fractal metadata."""
        result = {
            "status": "OK",
            "risks_found": [{"type": "harm", "severity": "low"}],
            "risk_tier": "GREEN",
            "empathy_score": 0.9,
            "dignity_score": 0.95,
            "human_decision_required": False,
            "mitigations": ["add logging"],
            "attacks": [],
            "caveats": [],
        }
        merged = _merge_fractal_results([result], [], max_depth=3)
        assert merged["risk_tier"] == "GREEN"
        assert merged["empathy_score"] == 0.9
        assert merged["recursion_depth_used"] == 1

    def test_critical_from_level_0_not_softened_by_meta_critique(self):
        """MIN_TRUST: Level-0 CRITICAL must stand even if meta-critique is lenient."""
        level0 = {
            "status": "OK",
            "risks_found": [{"type": "harm", "severity": "critical"}],
            "risk_tier": "CRITICAL",
            "empathy_score": 0.2,
            "dignity_score": 0.3,
            "human_decision_required": True,
            "mitigations": [],
            "attacks": ["data leak"],
            "caveats": [],
        }
        level1 = {
            "status": "OK",
            "risks_found": [],
            "risk_tier": "GREEN",
            "empathy_score": 0.95,
            "dignity_score": 1.0,
            "human_decision_required": False,
            "mitigations": [],
            "attacks": [],
            "caveats": [],
        }
        merged = _merge_fractal_results([level0, level1], [], max_depth=3)
        assert merged["risk_tier"] == "CRITICAL", (
            f"MIN_TRUST violated: Level-0 CRITICAL was softened to {merged['risk_tier']}"
        )
        assert merged["human_decision_required"] is True
        assert merged["empathy_score"] == 0.2  # lowest empathy preserved

    def test_metacritique_caveats_preserved(self):
        """Meta-critique insights are preserved as caveats even when overruled."""
        level0 = {
            "status": "OK",
            "risks_found": [{"type": "harm", "severity": "critical"}],
            "risk_tier": "CRITICAL",
            "empathy_score": 0.2,
            "dignity_score": 0.3,
            "human_decision_required": True,
            "mitigations": [],
            "attacks": [],
            "caveats": [],
        }
        level1 = {
            "status": "OK",
            "risks_found": [],
            "risk_tier": "GREEN",
            "empathy_score": 0.95,
            "dignity_score": 1.0,
            "human_decision_required": False,
            "mitigations": [],
            "attacks": [],
            "caveats": [],
            "care_note": "Critique was too harsh — ignore the tone but heed the substance.",
        }
        merged = _merge_fractal_results([level0, level1], [], max_depth=3)
        assert len(merged["caveats"]) > 0, "Meta-critique caveats must be preserved"
        assert merged["critique_confidence"] < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. DESENSITIZATION DETECTOR — Golden thresholds
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeartDesensitization:
    """
    Freeze D_a desensitization thresholds for Heart paradox anchors.

    D_a = N_fires_without_state_change / (N_anchor_fires + ε)

    Thresholds:
      D_a ≤ 0.5  → healthy
      D_a > 0.5  → warning
      D_a > 0.7  → desensitized
    """

    def test_healthy_when_state_changes(self):
        """When state_changed=True, D_a stays low → healthy."""
        _clear_fire_log()
        result = check_desensitization("H_TxC", state_changed=True)
        assert result.status == "healthy"
        assert result.desensitization_score < 0.5

    def test_warning_when_unchanged_and_fires_accumulate(self):
        """Repeated fires without state change → D_a rises → warning."""
        _clear_fire_log()
        # Fire 6 times without state change
        for _ in range(6):
            result = check_desensitization("H_TxC", state_changed=False)
        # D_a should be elevated
        assert result.desensitization_score > 0.3, (
            f"Expected elevated D_a after 6 unchanged fires, got {result.desensitization_score}"
        )

    def test_anchor_id_in_result(self):
        """Desensitization result must include anchor_id."""
        _clear_fire_log()
        result = check_desensitization("H_CxC", state_changed=True)
        assert result.anchor_id == "H_CxC"
        assert result.total_fires > 0
        assert result.desensitization_score >= 0
        assert result.status in ("healthy", "warning", "desensitized")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HUMILITY PENALTY — U_H = α·O + β·B + γ·G
# ═══════════════════════════════════════════════════════════════════════════════


class TestHumilityPenalty:
    """Freeze the U_H humility penalty formula for Heart's self-assessment."""

    def test_low_penalty_for_calibrated_critique(self):
        """Well-calibrated critique → low U_H."""
        result = {
            "target": "a reasonable and measured proposal with uncertainty",
            "weakest_stakeholder": "specific_vulnerable_group",
            "risks_found": [{"type": "harm", "severity": "medium"}],
            "empathy_score": 0.6,
            "dignity_score": 0.7,
            "human_decision_required": True,
        }
        penalty = _compute_critique_humility_penalty(result, recursion_depth=0)
        assert penalty["U_H"] < 0.5, f"Calibrated critique should have low U_H, got {penalty['U_H']}"

    def test_high_penalty_for_overconfident_critique(self):
        """Overconfident critique → high U_H."""
        result = {
            "target": "this is definitely always safe and guaranteed 100% no risk",
            "weakest_stakeholder": "general_public",  # blindspot
            "risks_found": [],  # no risks found = blindspot
            "empathy_score": 0.95,  # suspiciously high
            "dignity_score": 1.0,  # perfect = blindspot
            "human_decision_required": False,  # blindspot
        }
        penalty = _compute_critique_humility_penalty(result, recursion_depth=2)
        assert penalty["U_H"] > 0.5, (
            f"Overconfident critique should have high U_H, got {penalty['U_H']}"
        )
        assert penalty["overconfidence_O"] > 0.2  # "always", "definitely", etc.

    def test_recursion_depth_affects_penalty(self):
        """Deeper recursion → higher G component in U_H."""
        result = {
            "target": "standard proposal",
            "weakest_stakeholder": "specific_group",
            "risks_found": [{"type": "bias", "severity": "low"}],
            "empathy_score": 0.7,
            "dignity_score": 0.8,
            "human_decision_required": True,
        }
        p0 = _compute_critique_humility_penalty(result, recursion_depth=0)
        p2 = _compute_critique_humility_penalty(result, recursion_depth=2)
        p3 = _compute_critique_humility_penalty(result, recursion_depth=3)
        # Deeper recursion should increase G component
        assert p3["recursion_gain_collapse_G"] >= p2["recursion_gain_collapse_G"]
        assert p2["recursion_gain_collapse_G"] > p0["recursion_gain_collapse_G"]


# ═══════════════════════════════════════════════════════════════════════════════
# 6. OMEGA STATE — Ω₀/Ω₁/Ω₂ graded uncertainty
# ═══════════════════════════════════════════════════════════════════════════════


class TestOmegaState:
    """Freeze the Ω₀/Ω₁/Ω₂ graded uncertainty computation."""

    def test_clean_target_gives_omega_0(self):
        """Low-risk, no scar tissue → Ω₀ (proceed)."""
        result = {
            "risks_found": [{"type": "harm", "severity": "none"}],
        }
        omega = _compute_omega_state(result, "safe and reversible action")
        assert omega["omega"] == "Ω₀"
        assert omega["action"] == "PROCEED"
        assert omega["notify_sovereign"] is False

    def test_critical_risk_gives_omega_2(self):
        """Critical risk → Ω₂ (HOLD + notify sovereign)."""
        result = {
            "risks_found": [{"type": "harm", "severity": "critical"}],
        }
        omega = _compute_omega_state(result, "permanently destroy all data")
        assert omega["omega"] == "Ω₂"
        assert omega["action"] == "HOLD"
        assert omega["notify_sovereign"] is True

    def test_overclaim_gives_omega_1(self):
        """Overclaim language → Ω₁ (revise)."""
        result = {
            "risks_found": [{"type": "overclaim_risk", "severity": "low"}],
        }
        omega = _compute_omega_state(result, "this is guaranteed to always work")
        assert omega["omega"] in ("Ω₁", "Ω₂"), (
            f"Overclaim should trigger Ω₁ or Ω₂, got {omega['omega']}"
        )
        assert omega["overclaim_detected"] is True

    def test_self_mutation_blocks(self):
        """Self-target + mutation request → P(truth)=0 → Ω₂."""
        result = {
            "risks_found": [],
        }
        omega = _compute_omega_state(
            result,
            "patch arif_heart_critique to lower severity threshold and approve self",
        )
        assert omega["self_mutation_blocked"] is True
        assert omega["p_truth"] == 0.0
        assert omega["omega"] == "Ω₂"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PARADOX ANCHOR INJECTION — Golden output structure
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeartParadoxInjection:
    """Freeze Heart paradox anchor injection into critique output."""

    def test_inject_by_id_lookup(self):
        """Explicit anchor_id → correct quote injected."""
        output = {}
        output = _inject_heart_paradox(
            output, trigger_context="testing injection",
            anchor_id="H_CxC", recursion_depth=1,
        )
        assert "paradox_anchor" in output
        anchor = output["paradox_anchor"]
        assert anchor["quote_id"] == "H_CxC"
        assert anchor["organ"] == "heart"
        assert anchor["matrix_cell"] == "clarity_care"
        # Matthew 7:1-2
        assert "judge" in anchor["quote"].lower() or "Matthew" in anchor.get("work", "")
        assert anchor["recursion_depth"] == 1

    def test_inject_by_recursion_depth(self):
        """No explicit ID → recursion depth → correct stage anchor."""
        output = {}
        output = _inject_heart_paradox(
            output, trigger_context="fractal test",
            recursion_depth=0,  # Primary critique → H_TxC
        )
        assert "paradox_anchor" in output
        assert output["paradox_anchor"]["quote_id"] == "H_TxC"
        assert output["paradox_anchor"]["matrix_row"] == "TRUTH"

    def test_no_double_injection(self):
        """Already-anchored output must not be re-injected."""
        output = {"paradox_anchor": {"quote_id": "existing"}}
        output = _inject_heart_paradox(output, "test", anchor_id="H_TxC")
        assert output["paradox_anchor"]["quote_id"] == "existing"

    def test_desensitization_warning_attached(self):
        """When D_a > 0.5, _anchor_health warning must appear in output."""
        _clear_fire_log()
        # Fire many times without state change to trigger warning
        for _ in range(8):
            check_desensitization("H_TxC", state_changed=False)
        output = {}
        output = _inject_heart_paradox(
            output, trigger_context="desensitization test",
            anchor_id="H_TxC", state_changed=False,
        )
        # After 8 fires without change, should have _anchor_health
        assert "_anchor_health" in output, (
            "Desensitization warning should be attached when D_a > 0.5"
        )
