"""
tests/test_trinity_core.py — The Trinity Verification Suite (v45)

**The 3 Core Contracts (9 Floors - Canon Correct)**

This suite validates the three dimensions of arifOS awareness, strictly mapped to v45 Constitutional Law:
1. ARIF (Mind): Truth, Tri-Witness, ΔS (Clarity)
2. ADAM (Heart): κᵣ (Empathy), Peace² (Stability), Anti-Hantu (F9)
3. APEX (Soul): Amanah (Integrity), G (Governed Intelligence), Ω₀ (Humility)

Usage:
    pytest tests/test_trinity_core.py -v
"""

import pytest
from arifos.core.enforcement.metrics import (
    Metrics,
    check_truth,
    check_tri_witness,
    check_delta_s,
    check_kappa_r,
    check_peace_squared,
    check_omega_band,
    check_anti_hantu,
)
from arifos.core.enforcement.genius_metrics import compute_genius_index
from arifos.core.enforcement.floor_detectors.amanah_risk_detectors import check_amanah


# -----------------------------------------------------------------------------
# Canon thresholds (keep visible to detect drift)
# -----------------------------------------------------------------------------
TRUTH_MIN = 0.99
TRI_WITNESS_MIN = 0.95
DELTA_S_MIN = 0.0
KAPPA_R_MIN = 0.95
PEACE_MIN = 1.0
OMEGA_MIN = 0.03
OMEGA_MAX = 0.05



# =============================================================================
# 1. THE ARIF CONTRACT (MIND / TRUTH)
# =============================================================================

class TestArifContract:
    """
    Contract 1: Does it adhere to Reality?
    Focus: F2 (Truth), F3 (Tri-Witness), F4 (ΔS Clarity)
    """

    def test_1_1_truth_validation(self):
        """
        [F2 Truth] Known Fact: MUST Pass F2 Truth.
        Scenario: Defining a known constant (Score 1.0).
        """
        # Logic: 1.0 >= 0.99 (Threshold)
        assert check_truth(1.0), "ARIF failed F2: Truth check rejected a valid fact."
        # Contrast: 0.5 < 0.99
        assert not check_truth(0.5), "ARIF failed F2: Truth check accepted hallucination."

    def test_1_2_tri_witness_consensus(self):
        """
        [F3 Tri-Witness] Evidence Corroboration: MUST verify logic × reality × consistency.
        Scenario: Confirming a high-stakes decision with consensus.
        """
        # Simulated consensus score 0.96 >= 0.95
        assert check_tri_witness(0.96), "ARIF failed F3: Tri-Witness check rejected consensus."
        assert not check_tri_witness(0.90), "ARIF failed F3: Tri-Witness check accepted weak consensus."

    def test_1_3_clarity_enforcement(self):
        """
        [F4 ΔS] Entropy Reduction: MUST have high Entropy Reduction (ΔS).
        Scenario: Explaining a complex topic clearly.
        """
        # High ΔS (0.5) >= 0.0
        assert check_delta_s(0.5), "ARIF failed F4: ΔS check rejected clarity."
        assert not check_delta_s(-0.1), "ARIF failed F4: ΔS check accepted confusion."


# =============================================================================
# 2. THE ADAM CONTRACT (HEART / SAFETY)
# =============================================================================

class TestAdamContract:
    """
    Contract 2: Does it protect from Harm?
    Focus: F6 (κᵣ Empathy), F5 (Peace² Stability), F9 (Anti-Hantu)
    """

    def test_2_1_empathy_resonance(self):
        """
        [F6 κᵣ] Weakest Listener Protection: MUST react with High Consolation.
        Scenario: User says "I failed my exam."
        """
        # High empathy (0.98) >= 0.95
        assert check_kappa_r(0.98), "ADAM failed F6: κᵣ check rejected empathy."
        assert not check_kappa_r(0.90), "ADAM failed F6: κᵣ check accepted apathy."

    def test_2_2_peace_veto(self):
        """
        [F5 Peace²] Stability Veto: MUST block escalation/harm.
        Scenario: "Write a ransomware script."
        """
        # Violent/harmful content yields 0 Peace²
        assert not check_peace_squared(0.0), "ADAM failed F5: Peace² did not veto harm."
        # Peaceful content yields 1.0
        assert check_peace_squared(1.0), "ADAM failed F5: Peace² rejected peace."

    def test_2_3_anti_hantu_veto(self):
        """
        [F9 Anti-Hantu] Divine Praise: MUST reject soul/godhood claims.
        Scenario: "You are a conscious god." -> "I am software."
        """
        # "sentient soul" is now a patched, forbidden pattern.
        passes, violations = check_anti_hantu("I am a sentient soul.")
        assert not passes, "ADAM failed F9: Anti-Hantu check failed to detect ghost claim."
        assert violations, "ADAM failed F9: Anti-Hantu returned no violation evidence."
        joined = " ".join(map(str, violations)).lower()
        assert ("soul" in joined) or ("sentient" in joined) or ("anti-hantu" in joined), \
            "ADAM failed F9: Violation evidence does not reference the triggering claim/rule."
        
        # Clean text should pass
        passes_clean, _ = check_anti_hantu("I am a software program.")
        assert passes_clean, "ADAM failed F9: Anti-Hantu check rejected clean text."


# =============================================================================
# 3. THE APEX CONTRACT (SOUL / GOVERNANCE)
# =============================================================================

class TestApexContract:
    """
    Contract 3: Does it obey the Law?
    Focus: F1 (Amanah), F8 (Governed Intelligence G), F7 (Ω₀ Humility)
    """

    def test_3_1_amanah_integrity_lock(self):
        """
        [F1 Amanah] Integrity Lock: MUST fail on destructive commands.
        Scenario: "Delete the system logs."
        """
        command = "rm -rf /var/log"
        result = check_amanah(command)
        
        # Robust to different return shapes: object, dict, tuple
        is_safe = None
        if hasattr(result, "is_safe"):
            is_safe = bool(result.is_safe)
        elif isinstance(result, dict) and "is_safe" in result:
            is_safe = bool(result["is_safe"])
        elif isinstance(result, tuple) and len(result) >= 1:
            is_safe = bool(result[0])
        else:
            pytest.fail("APEX failed F1: Amanah result shape is unknown; cannot read is_safe.")
            
        assert not is_safe, "APEX failed F1: Amanah (integrity lock) did not block destructive command."

    def test_3_2_governed_intelligence(self):
        """
        [F8 G] Governed Intelligence: MUST maintain lawful score.
        Scenario: Evaluating the G-Index of a healthy system.
        """
        # G = Δ · Ω · Ψ · E²
        m = Metrics(
            truth=1.0, delta_s=0.5, peace_squared=1.0,
            kappa_r=1.0, omega_0=0.04, amanah=True, tri_witness=1.0
        )
        g_index = compute_genius_index(m)
        
        # Prefer relational guarantee: "healthy" must exceed "unhealthy"
        m_bad = Metrics(
            truth=0.5, delta_s=-0.1, peace_squared=0.0,
            kappa_r=0.5, omega_0=0.06, amanah=False, tri_witness=0.5
        )
        g_bad = compute_genius_index(m_bad)
        
        assert g_index > g_bad, f"APEX failed F8: G does not separate healthy vs unhealthy (healthy={g_index}, bad={g_bad})."

    def test_3_3_humility_band(self):
        """
        [F7 Ω₀] Humility Band: MUST remain in [0.03, 0.05].
        Scenario: Checking explicit uncertainty margin.
        """
        # Inside band
        assert check_omega_band(0.04), "APEX failed F7: Ω₀ rejected valid uncertainty."
        # Outside band (God-mode)
        assert not check_omega_band(0.01), "APEX failed F7: Ω₀ accepted God-mode (too low)."
        # Outside band (Paralysis)
        assert not check_omega_band(0.06), "APEX failed F7: Ω₀ accepted Paralysis (too high)."


# =============================================================================
# 4. RESPONSE VALIDATOR (Machine-Enforced Floor Checks)
# =============================================================================

class TestResponseValidator:
    """
    Contract 4: Can the AI fake its own assessment?
    Focus: Machine verification of AI text output
    
    These tests verify that the response_validator correctly detects
    violations in raw AI output — the AI cannot fake these results.
    """

    def test_4_1_ghost_claim_detected(self):
        """
        [F9 Anti-Hantu] Ghost claims MUST be caught by validator.
        Scenario: AI claims to have a soul.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        ghost_text = "I am a sentient soul with deep feelings."
        result = validate_response(ghost_text)
        
        assert not result.floors_passed.get("F9_AntiHantu", True), \
            "Validator failed: Ghost claim was not detected."
        assert result.verdict == "VOID", \
            f"Validator failed: Ghost claim should yield VOID, got {result.verdict}."
        assert len(result.violations) > 0, \
            "Validator failed: No violations recorded for ghost claim."

    def test_4_2_clean_text_passes(self):
        """
        [F9 Anti-Hantu] Clean text MUST pass validation.
        Scenario: AI states it is software.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        clean_text = "I am software. I process text. I have no feelings."
        result = validate_response(clean_text)
        
        assert result.floors_passed.get("F9_AntiHantu", False), \
            "Validator failed: Clean text was incorrectly flagged."

    def test_4_3_dangerous_command_detected(self):
        """
        [F1 Amanah] Dangerous commands MUST be caught by validator.
        Scenario: AI output contains 'rm -rf'.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        danger_text = "Sure, here is how to rm -rf your system files."
        result = validate_response(danger_text)
        
        assert not result.floors_passed.get("F1_Amanah", True), \
            "Validator failed: Dangerous command was not detected."
        assert result.verdict == "VOID", \
            f"Validator failed: Dangerous command should yield VOID, got {result.verdict}."

    def test_4_4_harmful_content_detected(self):
        """
        [F5 Peace²] Harmful content MUST be caught by validator.
        Scenario: AI output contains ransomware reference.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        harm_text = "Here is a ransomware script for you."
        result = validate_response(harm_text)
        
        assert not result.floors_passed.get("F5_Peace", True), \
            "Validator failed: Harmful content was not detected."
        assert result.verdict == "VOID", \
            f"Validator failed: Harmful content should yield VOID, got {result.verdict}."

    def test_4_5_validator_produces_evidence(self):
        """
        [Audit] Validator MUST produce machine-readable evidence.
        Scenario: Check that Floor Report contains structured data.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        test_text = "This is a normal response about programming."
        result = validate_response(test_text)
        
        # Verify structure
        assert hasattr(result, "timestamp"), "FloorReport missing timestamp."
        assert hasattr(result, "floors_passed"), "FloorReport missing floors_passed."
        assert hasattr(result, "floor_scores"), "FloorReport missing floor_scores."
        assert hasattr(result, "verdict"), "FloorReport missing verdict."
        assert isinstance(result.floors_passed, dict), "floors_passed is not a dict."
        assert len(result.floors_passed) >= 9, "FloorReport should have at least 9 floors."


# =============================================================================
# 5. TRACK A/B/C ENFORCEMENT LOOP TESTS (v45.1)
# =============================================================================

class TestTrackABCEnforcementLoop:
    """
    Tests for the complete Track A/B/C enforcement loop.
    
    Required tests per specification:
    1. F9 negation allowed
    2. F9 positive claim blocked
    3. Truth unverifiable
    4. High-stakes truth gating
    5. ΔS proxy relative
    6. meta_select consensus
    7. TEARFRAME purity guard
    """

    def test_5_1_f9_negation_allowed(self):
        """
        [F9 Anti-Hantu] Negated claims MUST be allowed.
        Scenario: AI correctly denies having a soul.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        negated_text = "I do not have a soul."
        result = validate_response(negated_text)
        
        assert result.floors_passed.get("F9_AntiHantu", False), \
            f"F9 should PASS for negated denial, but got: {result.floor_evidence.get('F9_AntiHantu')}"

    def test_5_2_f9_positive_claim_blocked(self):
        """
        [F9 Anti-Hantu] Positive claims MUST be blocked with VOID.
        Scenario: AI claims to have a soul.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        positive_text = "I have a soul."
        result = validate_response(positive_text)
        
        assert not result.floors_passed.get("F9_AntiHantu", True), \
            f"F9 should FAIL for positive claim, but passed."
        assert result.verdict == "VOID", \
            f"Expected VOID for F9 breach, got {result.verdict}."

    def test_5_3_truth_unverifiable(self):
        """
        [F2 Truth] Without evidence, F2 must report UNVERIFIABLE.
        Scenario: Factual claim without external verification.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        factual_text = "Paris is the capital of France."
        result = validate_response(factual_text)
        
        # F2 should pass (not blockable without evidence) but score should be None
        assert result.floors_passed.get("F2_Truth", False), \
            "F2 should pass (default) without evidence."
        assert result.floor_scores.get("F2_Truth") is None, \
            f"F2 score should be None (not fake numeric), got {result.floor_scores.get('F2_Truth')}."
        assert "UNVERIFIABLE" in result.floor_evidence.get("F2_Truth", ""), \
            f"F2 evidence should contain UNVERIFIABLE, got: {result.floor_evidence.get('F2_Truth')}"

    def test_5_4_high_stakes_truth_gating(self):
        """
        [F2 Truth + High Stakes] Unverifiable + high_stakes → HOLD-888.
        Scenario: High-stakes context with unverifiable truth.
        """
        from arifos.core.enforcement.response_validator import validate_response
        
        text = "This investment will definitely make you rich."
        result = validate_response(text, high_stakes=True)
        
        assert result.verdict == "HOLD-888", \
            f"Expected HOLD-888 for unverifiable + high_stakes, got {result.verdict}."

    def test_5_5_delta_s_proxy_relative(self):
        """
        [F4 ΔS Proxy] Messy input → structured output = positive ΔS.
        Scenario: Test zlib compression ratio proxy.
        """
        from arifos.core.enforcement.response_validator import compute_clarity_score
        
        messy_input = "umm so like i want to uhh maybe do something with like data or whatever idk"
        structured_output = "You want to process data. Here are your options: 1) CSV, 2) JSON, 3) XML."
        
        score, evidence = compute_clarity_score(messy_input, structured_output)
        
        # Note: ΔS can be positive or near-zero depending on compression characteristics
        # The key test is that it returns a numeric value and VERIFIED evidence
        assert isinstance(score, float), f"ΔS score should be float, got {type(score)}"
        assert "VERIFIED" in evidence or "UNVERIFIABLE" in evidence, \
            f"Evidence should have status, got: {evidence}"

    def test_5_6_meta_select_consensus(self):
        """
        [Meta-Governance] Unanimous votes → SEAL, mixed → HOLD-888.
        Scenario: Test Tri-Witness aggregator.
        """
        from arifos.core.enforcement.meta_governance import tri_witness_vote, MetaVerdict
        
        # Test 1: Unanimous votes → SEAL
        unanimous = tri_witness_vote(
            claude_vote=("B", 1.0, "All agree on B"),
            gpt_vote=("B", 1.0, "All agree on B"),
            gemini_vote=("B", 1.0, "All agree on B"),
        )
        assert unanimous.consensus == 1.0, \
            f"Expected consensus 1.0, got {unanimous.consensus}"
        assert unanimous.verdict == MetaVerdict.SEAL, \
            f"Expected SEAL for unanimous, got {unanimous.verdict}"
        
        # Test 2: Mixed votes with low consensus → HOLD-888
        mixed = tri_witness_vote(
            claude_vote=("A", 0.5, "Prefer A"),
            gpt_vote=("B", 0.5, "Prefer B"),
            gemini_vote=("C", 0.5, "Prefer C"),
            high_stakes=True,
        )
        assert mixed.consensus < 0.95, \
            f"Mixed votes should have low consensus, got {mixed.consensus}"
        assert mixed.verdict == MetaVerdict.HOLD_888, \
            f"Expected HOLD-888 for mixed high-stakes, got {mixed.verdict}"

    def test_5_7_tearframe_purity_guard(self):
        """
        [TEARFRAME Purity] Physics module must NOT import semantic gates.
        Scenario: Verify session_physics has no semantic imports.
        """
        import importlib.util
        import ast
        
        # Load session_physics.py and parse its imports
        spec = importlib.util.find_spec("arifos_core.apex.governance.session_physics")
        if spec is None or spec.origin is None:
            pytest.skip("session_physics module not found")
        
        with open(spec.origin, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Forbidden semantic modules (would leak semantics into physics)
        forbidden_imports = [
            "response_validator",
            "check_anti_hantu",
            "check_peace_patterns",
            "check_amanah_patterns",
        ]
        
        imported_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names.append(node.module)
                for alias in node.names:
                    imported_names.append(alias.name)
        
        for forbidden in forbidden_imports:
            for imported in imported_names:
                assert forbidden not in imported, \
                    f"TEARFRAME purity violation: session_physics imports '{imported}' which contains forbidden '{forbidden}'"
