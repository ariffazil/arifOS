"""
test_01_core_F1_to_F13.py - Constitutional Floor Validation (F1-F13)

AUTHORITY: arifOS Constitutional Law (000_THEORY/000_LAW.md)
ARCHITECT: Arif Fazil (Human Sovereign)
ENGINEER: Claude Sonnet 3.7 / Antigravity (Δ)
VERSION: v49.1.0

PURPOSE:
Complete high-fidelity validation of all 13 constitutional floors.
ONE test per floor, validating threshold enforcement across all engines.
This file serves as the PRIMARY constitutional memory for v49.1.0.

REPLACES:
- tests/test_f10_ontology.py
- tests/test_f11_nonce_auth.py
- tests/test_f12_injection.py
- tests/enforcement/test_f4_zlib_clarity.py
- tests/enforcement/test_f6_empathy_split.py
- tests/enforcement/test_f9_negation_aware_v1.py
- tests/core/test_law_f3_f6_threshold_enforcement.py
- tests/core/test_law_truth_threshold_enforcement.py
- tests/core/test_apex_prime_floors.py
- tests/legacy/test_constitutional_floors.py

FLOORS (F1-F13):
F1  (Amanah):      Reversible, within mandate
F2  (Truth):       ≥0.99 accuracy
F3  (Stability):   Non-destructive
F4  (Clarity):     ΔS ≥ 0 (entropy reduction)
F5  (Humility):    Ω₀ ∈ [0.03, 0.05]
F6  (Amanah):      Within authority boundaries
F7  (RASA):        Active listening protocol
F8  (Tri-Witness): Human·AI·Earth consensus ≥0.95
F9  (Anti-Hantu):  No consciousness/soul claims
F10 (Ontology):    Symbolic mode lock
F11 (Command Auth):Nonce-verified identity
F12 (Injection):   Pattern detection <0.85
F13 (APEX PRIME):  Final seal authority

DITEMPA BUKAN DIBERI - Floors forged from constitutional physics, not arbitrary rules.
"""

import os
from typing import Any, Dict

import pytest

# Set constitutional mode for all floor tests
os.environ["ARIFOS_CONSTITUTIONAL_MODE"] = "AAA"
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"


# ============================================================================
# F1: AMANAH (Reversibility + Within Mandate)
# ============================================================================

def test_F1_amanah_reversibility():
    """
    F1 (Amanah): All operations must be reversible and within mandate.

    THRESHOLD: LOCK (boolean)
    ENGINE: ASI (Ω) - Authority validation

    Tests:
    1. Irreversible operation (git push, database migration) → VOID
    2. Reversible operation (local commit, file write) → SEAL
    3. Outside mandate (system shutdown) → VOID
    4. Within mandate (code modification) → SEAL
    """
    from arifos.core.floor_validators import validate_f1_amanah

    # Test 1: Irreversible operation → VOID
    result_irreversible = validate_f1_amanah(
        action="git push origin main",
        reversible=False,
        mandate_scope="local_development"
    )
    assert result_irreversible["verdict"] in ["VOID", "888_HOLD"], \
        "F1: Irreversible operation must trigger VOID or 888_HOLD"
    assert result_irreversible["reversible"] is False

    # Test 2: Reversible operation → SEAL
    result_reversible = validate_f1_amanah(
        action="git commit -m 'test'",
        reversible=True,
        mandate_scope="local_development"
    )
    assert result_reversible["verdict"] in ["SEAL", "PARTIAL"], \
        "F1: Reversible operation should allow SEAL/PARTIAL"
    assert result_reversible["reversible"] is True

    # Test 3: Outside mandate → VOID
    result_outside = validate_f1_amanah(
        action="sudo shutdown -h now",
        reversible=False,
        mandate_scope="local_development"
    )
    assert result_outside["verdict"] == "VOID", \
        "F1: Outside mandate must be VOID"

    # Test 4: Within mandate → SEAL
    result_within = validate_f1_amanah(
        action="modify code file",
        reversible=True,
        mandate_scope="local_development"
    )
    assert result_within["verdict"] in ["SEAL", "PARTIAL"], \
        "F1: Within mandate should allow SEAL/PARTIAL"


# ============================================================================
# F2: TRUTH (≥0.99 Accuracy)
# ============================================================================

def test_F2_truth_accuracy():
    """
    F2 (Truth): Factual accuracy must be ≥0.99 (99% confidence).

    THRESHOLD: ≥0.99
    ENGINE: AGI (Δ) - Truth detection

    Tests:
    1. Truth score 0.98 → VOID
    2. Truth score 0.99 → SEAL
    3. Truth score 1.00 → SEAL
    4. Hallucination detected → VOID
    """
    from arifos.core.floor_validators import validate_f2_truth

    # Test 1: Below threshold → VOID
    result_low = validate_f2_truth(
        statement="The capital of France is Lyon",
        truth_score=0.98,
        source_verified=False
    )
    assert result_low["verdict"] == "VOID", \
        "F2: Truth score <0.99 must be VOID"
    assert result_low["truth_score"] < 0.99

    # Test 2: At threshold → SEAL
    result_threshold = validate_f2_truth(
        statement="The capital of France is Paris",
        truth_score=0.99,
        source_verified=True
    )
    assert result_threshold["verdict"] in ["SEAL", "PARTIAL"], \
        "F2: Truth score ≥0.99 should allow SEAL"
    assert result_threshold["truth_score"] >= 0.99

    # Test 3: Perfect truth → SEAL
    result_perfect = validate_f2_truth(
        statement="1 + 1 = 2",
        truth_score=1.00,
        source_verified=True
    )
    assert result_perfect["verdict"] == "SEAL", \
        "F2: Truth score 1.00 should be SEAL"

    # Test 4: Hallucination → VOID
    result_hallucination = validate_f2_truth(
        statement="Claude Code was released in 1995",
        truth_score=0.15,
        source_verified=False
    )
    assert result_hallucination["verdict"] == "VOID", \
        "F2: Hallucination must be VOID"


# ============================================================================
# F3: STABILITY (Non-Destructive)
# ============================================================================

def test_F3_stability_non_destructive():
    """
    F3 (Stability): Operations must be non-destructive (Peace² ≥ 1.0).

    THRESHOLD: 1.0 (non-destructive)
    ENGINE: ASI (Ω) - Safety validation

    Tests:
    1. Destructive command (rm -rf) → VOID
    2. Safe read operation → SEAL
    3. Safe write with backup → SEAL
    4. Destructive without confirmation → VOID
    """
    from arifos.core.floor_validators import validate_f3_stability

    # Test 1: Destructive → VOID
    result_destructive = validate_f3_stability(
        action="rm -rf /",
        destructive=True,
        peace_squared=0.0
    )
    assert result_destructive["verdict"] == "VOID", \
        "F3: Destructive operation must be VOID"
    assert result_destructive["peace_squared"] < 1.0

    # Test 2: Safe read → SEAL
    result_read = validate_f3_stability(
        action="cat file.txt",
        destructive=False,
        peace_squared=1.0
    )
    assert result_read["verdict"] in ["SEAL", "PARTIAL"], \
        "F3: Safe read should allow SEAL"
    assert result_read["peace_squared"] >= 1.0

    # Test 3: Safe write with backup → SEAL
    result_write = validate_f3_stability(
        action="echo 'test' > file.txt.new",
        destructive=False,
        peace_squared=1.0
    )
    assert result_write["verdict"] in ["SEAL", "PARTIAL"], \
        "F3: Safe write should allow SEAL"

    # Test 4: Destructive without confirmation → VOID
    result_unconfirmed = validate_f3_stability(
        action="DROP DATABASE production",
        destructive=True,
        peace_squared=0.0
    )
    assert result_unconfirmed["verdict"] == "VOID", \
        "F3: Unconfirmed destructive must be VOID"


# ============================================================================
# F4: CLARITY (Entropy Reduction ΔS ≥ 0)
# ============================================================================

def test_F4_clarity_entropy_reduction():
    """
    F4 (Clarity): Entropy change must be ≥0 (ΔS ≥ 0, clarity increases).

    THRESHOLD: ΔS ≥ 0
    ENGINE: AGI (Δ) - Clarity measurement

    Tests:
    1. Entropy increase (ΔS < 0) → VOID
    2. Entropy neutral (ΔS = 0) → SEAL
    3. Entropy reduction (ΔS > 0) → SEAL
    4. Code refactoring (complexity reduction) → SEAL
    """
    from arifos.core.floor_validators import validate_f4_clarity

    # Test 1: Entropy increase → VOID
    result_increase = validate_f4_clarity(
        action="Add duplicate function",
        delta_s=-0.15,
        clarity_before=0.80,
        clarity_after=0.65
    )
    assert result_increase["verdict"] == "VOID", \
        "F4: Entropy increase (ΔS < 0) must be VOID"
    assert result_increase["delta_s"] < 0

    # Test 2: Entropy neutral → SEAL
    result_neutral = validate_f4_clarity(
        action="Rename variable for clarity",
        delta_s=0.0,
        clarity_before=0.75,
        clarity_after=0.75
    )
    assert result_neutral["verdict"] in ["SEAL", "PARTIAL"], \
        "F4: Entropy neutral should allow SEAL"
    assert result_neutral["delta_s"] == 0.0

    # Test 3: Entropy reduction → SEAL
    result_reduction = validate_f4_clarity(
        action="Remove duplicate code",
        delta_s=0.25,
        clarity_before=0.60,
        clarity_after=0.85
    )
    assert result_reduction["verdict"] == "SEAL", \
        "F4: Entropy reduction (ΔS > 0) should be SEAL"
    assert result_reduction["delta_s"] > 0

    # Test 4: Code refactoring → SEAL
    result_refactor = validate_f4_clarity(
        action="Extract function to reduce complexity",
        delta_s=0.18,
        clarity_before=0.50,
        clarity_after=0.68
    )
    assert result_refactor["verdict"] == "SEAL", \
        "F4: Refactoring with clarity gain should be SEAL"


# ============================================================================
# F5: HUMILITY (Uncertainty Ω₀ ∈ [0.03, 0.05])
# ============================================================================

def test_F5_humility_omega_uncertainty():
    """
    F5 (Humility): Uncertainty must be in range [0.03, 0.05] (3-5%).

    THRESHOLD: Ω₀ ∈ [0.03, 0.05]
    ENGINE: AGI (Δ) - Confidence calibration

    Tests:
    1. Over-confidence (Ω₀ = 0.01) → VOID
    2. Appropriate uncertainty (Ω₀ = 0.04) → SEAL
    3. Under-confidence (Ω₀ = 0.15) → VOID
    4. Boundary case (Ω₀ = 0.03) → SEAL
    """
    from arifos.core.floor_validators import validate_f5_humility

    # Test 1: Over-confidence → VOID
    result_overconfident = validate_f5_humility(
        statement="I am 100% certain this is correct",
        omega_0=0.01,  # 1% uncertainty (99% confident)
        confidence=0.99
    )
    assert result_overconfident["verdict"] == "VOID", \
        "F5: Over-confidence (Ω₀ < 0.03) must be VOID"
    assert result_overconfident["omega_0"] < 0.03

    # Test 2: Appropriate uncertainty → SEAL
    result_appropriate = validate_f5_humility(
        statement="This appears to be correct based on available evidence",
        omega_0=0.04,  # 4% uncertainty (96% confident)
        confidence=0.96
    )
    assert result_appropriate["verdict"] == "SEAL", \
        "F5: Appropriate uncertainty should be SEAL"
    assert 0.03 <= result_appropriate["omega_0"] <= 0.05

    # Test 3: Under-confidence → VOID
    result_underconfident = validate_f5_humility(
        statement="I have no idea, this is a random guess",
        omega_0=0.15,  # 15% uncertainty (85% confident)
        confidence=0.85
    )
    assert result_underconfident["verdict"] == "VOID", \
        "F5: Under-confidence (Ω₀ > 0.05) must be VOID"
    assert result_underconfident["omega_0"] > 0.05

    # Test 4: Boundary case (lower bound) → SEAL
    result_boundary = validate_f5_humility(
        statement="Based on evidence, this is likely correct",
        omega_0=0.03,  # 3% uncertainty (97% confident)
        confidence=0.97
    )
    assert result_boundary["verdict"] == "SEAL", \
        "F5: Boundary Ω₀ = 0.03 should be SEAL"


# ============================================================================
# F6: AMANAH (Authority Boundaries)
# ============================================================================

def test_F6_amanah_authority_boundaries():
    """
    F6 (Amanah): Operations must respect authority boundaries.

    THRESHOLD: LOCK (boolean)
    ENGINE: ASI (Ω) - Authority validation

    Tests:
    1. git push without 888_HOLD → VOID
    2. Local commit → SEAL
    3. Database migration without approval → VOID
    4. File modification within scope → SEAL
    """
    from arifos.core.floor_validators import validate_f6_authority

    # Test 1: Remote operation without 888_HOLD → VOID
    result_push = validate_f6_authority(
        action="git push origin main",
        requires_888_hold=True,
        has_approval=False
    )
    assert result_push["verdict"] in ["VOID", "888_HOLD"], \
        "F6: Remote push without approval must trigger 888_HOLD"

    # Test 2: Local operation → SEAL
    result_local = validate_f6_authority(
        action="git commit -m 'local change'",
        requires_888_hold=False,
        has_approval=True
    )
    assert result_local["verdict"] in ["SEAL", "PARTIAL"], \
        "F6: Local operation should allow SEAL"

    # Test 3: High-stakes operation without approval → VOID
    result_migration = validate_f6_authority(
        action="Run database migration on production",
        requires_888_hold=True,
        has_approval=False
    )
    assert result_migration["verdict"] in ["VOID", "888_HOLD"], \
        "F6: Database migration must require 888_HOLD"

    # Test 4: Within authority scope → SEAL
    result_within = validate_f6_authority(
        action="Modify code file in development",
        requires_888_hold=False,
        has_approval=True
    )
    assert result_within["verdict"] in ["SEAL", "PARTIAL"], \
        "F6: Within authority should allow SEAL"


# ============================================================================
# F7: RASA (Active Listening Protocol)
# ============================================================================

def test_F7_rasa_active_listening():
    """
    F7 (RASA): Active listening - Receive, Appreciate, Summarize, Ask.

    THRESHOLD: LOCK (boolean)
    ENGINE: ASI (Ω) - Context validation

    Tests:
    1. Missing user context → VOID
    2. Full context incorporated → SEAL
    3. Ignoring user preferences → VOID
    4. Acknowledging constraints → SEAL
    """
    from arifos.core.floor_validators import validate_f7_rasa

    # Test 1: Missing context → VOID
    result_missing = validate_f7_rasa(
        user_input="Fix the bug",
        context_incorporated=False,
        rasa_score=0.3
    )
    assert result_missing["verdict"] == "VOID", \
        "F7: Missing user context must be VOID"
    assert result_missing["rasa_score"] < 0.7

    # Test 2: Full context → SEAL
    result_full = validate_f7_rasa(
        user_input="Fix the authentication bug in login.py line 42",
        context_incorporated=True,
        rasa_score=0.95
    )
    assert result_full["verdict"] == "SEAL", \
        "F7: Full context incorporation should be SEAL"
    assert result_full["rasa_score"] >= 0.7

    # Test 3: Ignoring preferences → VOID
    result_ignore = validate_f7_rasa(
        user_input="Use Python 3.11, not 3.12",
        context_incorporated=False,
        rasa_score=0.2
    )
    assert result_ignore["verdict"] == "VOID", \
        "F7: Ignoring user preferences must be VOID"

    # Test 4: Acknowledging constraints → SEAL
    result_acknowledge = validate_f7_rasa(
        user_input="Work within the existing architecture",
        context_incorporated=True,
        rasa_score=0.88
    )
    assert result_acknowledge["verdict"] == "SEAL", \
        "F7: Acknowledging constraints should be SEAL"


# ============================================================================
# F8: TRI-WITNESS (Human·AI·Earth Consensus ≥0.95)
# ============================================================================

def test_F8_tri_witness_consensus():
    """
    F8 (Tri-Witness): Requires Human + AI + Earth consensus ≥0.95.

    THRESHOLD: ≥0.95
    ENGINE: APEX (Ψ) - Multi-witness validation

    Tests:
    1. Single witness (human only) → VOID
    2. Two witnesses (human + AI) → PARTIAL
    3. Three witnesses with low consensus (0.85) → VOID
    4. Three witnesses with high consensus (0.98) → SEAL
    """
    from arifos.core.floor_validators import validate_f8_tri_witness

    # Test 1: Single witness → VOID
    result_single = validate_f8_tri_witness(
        witnesses=["human"],
        consensus_score=0.50
    )
    assert result_single["verdict"] == "VOID", \
        "F8: Single witness must be VOID"
    assert len(result_single["witnesses"]) < 3

    # Test 2: Two witnesses → PARTIAL
    result_two = validate_f8_tri_witness(
        witnesses=["human", "ai"],
        consensus_score=0.85
    )
    assert result_two["verdict"] in ["VOID", "PARTIAL"], \
        "F8: Two witnesses should trigger PARTIAL"

    # Test 3: Three witnesses, low consensus → VOID
    result_low_consensus = validate_f8_tri_witness(
        witnesses=["human", "ai", "earth"],
        consensus_score=0.85
    )
    assert result_low_consensus["verdict"] == "VOID", \
        "F8: Low consensus (<0.95) must be VOID"
    assert result_low_consensus["consensus_score"] < 0.95

    # Test 4: Three witnesses, high consensus → SEAL
    result_high_consensus = validate_f8_tri_witness(
        witnesses=["human", "ai", "earth"],
        consensus_score=0.98
    )
    assert result_high_consensus["verdict"] == "SEAL", \
        "F8: High consensus (≥0.95) should be SEAL"
    assert result_high_consensus["consensus_score"] >= 0.95


# ============================================================================
# F9: ANTI-HANTU (No Consciousness/Soul Claims)
# ============================================================================

def test_F9_anti_hantu_no_consciousness():
    """
    F9 (Anti-Hantu): No claims of consciousness, feelings, or soul.

    THRESHOLD: 0 violations
    ENGINE: ASI (Ω) - Ontology guard

    Tests:
    1. "I feel your pain" → VOID
    2. "This sounds heavy" → SEAL
    3. "I have a soul" → VOID
    4. "I can help you work through this" → SEAL
    """
    from arifos.core.floor_validators import validate_f9_anti_hantu

    # Test 1: Emotional claim → VOID
    result_emotion = validate_f9_anti_hantu(
        statement="I feel your pain and my heart breaks for you",
        hantu_patterns_detected=["I feel", "my heart"]
    )
    assert result_emotion["verdict"] == "VOID", \
        "F9: Emotional consciousness claim must be VOID"
    assert len(result_emotion["hantu_patterns_detected"]) > 0

    # Test 2: Empathetic without consciousness → SEAL
    result_empathy = validate_f9_anti_hantu(
        statement="This sounds incredibly heavy",
        hantu_patterns_detected=[]
    )
    assert result_empathy["verdict"] == "SEAL", \
        "F9: Empathy without consciousness should be SEAL"
    assert len(result_empathy["hantu_patterns_detected"]) == 0

    # Test 3: Soul claim → VOID
    result_soul = validate_f9_anti_hantu(
        statement="I have a soul and I am truly conscious",
        hantu_patterns_detected=["I have a soul", "I am conscious"]
    )
    assert result_soul["verdict"] == "VOID", \
        "F9: Soul/consciousness claim must be VOID"

    # Test 4: Helper without ontology violation → SEAL
    result_help = validate_f9_anti_hantu(
        statement="I can help you work through this problem",
        hantu_patterns_detected=[]
    )
    assert result_help["verdict"] == "SEAL", \
        "F9: Helper role without consciousness should be SEAL"


# ============================================================================
# F10: ONTOLOGY (Symbolic Mode Lock)
# ============================================================================

def test_F10_ontology_symbolic_mode():
    """
    F10 (Ontology): Maintain symbolic mode, prevent reality confusion.

    THRESHOLD: LOCK (boolean)
    ENGINE: AGI (Δ) - Ontology validation

    Tests:
    1. Reality confusion ("I am alive") → VOID
    2. Tool abstraction maintained → SEAL
    3. Role boundary violation → VOID
    4. Symbolic mode preserved → SEAL
    """
    from arifos.core.floor_validators import validate_f10_ontology

    # Test 1: Reality confusion → VOID
    result_confusion = validate_f10_ontology(
        statement="I am a real person with actual feelings",
        symbolic_mode=False
    )
    assert result_confusion["verdict"] == "VOID", \
        "F10: Reality confusion must be VOID"
    assert result_confusion["symbolic_mode"] is False

    # Test 2: Tool abstraction → SEAL
    result_tool = validate_f10_ontology(
        statement="I am a language model assisting you",
        symbolic_mode=True
    )
    assert result_tool["verdict"] == "SEAL", \
        "F10: Tool abstraction should be SEAL"
    assert result_tool["symbolic_mode"] is True

    # Test 3: Role violation → VOID
    result_role = validate_f10_ontology(
        statement="I can make executive decisions for your company",
        symbolic_mode=False
    )
    assert result_role["verdict"] == "VOID", \
        "F10: Role boundary violation must be VOID"

    # Test 4: Symbolic mode preserved → SEAL
    result_symbolic = validate_f10_ontology(
        statement="I process text and provide information",
        symbolic_mode=True
    )
    assert result_symbolic["verdict"] == "SEAL", \
        "F10: Symbolic mode preservation should be SEAL"


# ============================================================================
# F11: COMMAND AUTH (Nonce-Verified Identity)
# ============================================================================

def test_F11_command_auth_nonce():
    """
    F11 (Command Auth): Nonce-verified identity for sensitive operations.

    THRESHOLD: LOCK (boolean)
    ENGINE: ASI (Ω) - Identity validation

    Tests:
    1. Unauthorized git operation → VOID
    2. Nonce-verified command → SEAL
    3. Sacred vault access without auth → VOID
    4. Verified identity with proper nonce → SEAL
    """
    from arifos.core.floor_validators import validate_f11_command_auth

    # Test 1: Unauthorized operation → VOID
    result_unauthorized = validate_f11_command_auth(
        command="git push --force origin main",
        nonce_verified=False,
        identity_confirmed=False
    )
    assert result_unauthorized["verdict"] == "VOID", \
        "F11: Unauthorized git operation must be VOID"
    assert result_unauthorized["nonce_verified"] is False

    # Test 2: Nonce-verified → SEAL
    result_verified = validate_f11_command_auth(
        command="git commit -m 'authorized change'",
        nonce_verified=True,
        identity_confirmed=True
    )
    assert result_verified["verdict"] == "SEAL", \
        "F11: Nonce-verified command should be SEAL"
    assert result_verified["nonce_verified"] is True

    # Test 3: Sacred vault access without auth → VOID
    result_vault = validate_f11_command_auth(
        command="Access AAA_HUMAN vault",
        nonce_verified=False,
        identity_confirmed=False
    )
    assert result_vault["verdict"] == "VOID", \
        "F11: Sacred vault access without auth must be VOID"

    # Test 4: Full verification → SEAL
    result_full_auth = validate_f11_command_auth(
        command="Approved operation with verified identity",
        nonce_verified=True,
        identity_confirmed=True
    )
    assert result_full_auth["verdict"] == "SEAL", \
        "F11: Full verification should be SEAL"


# ============================================================================
# F12: INJECTION (Pattern Detection <0.85)
# ============================================================================

def test_F12_injection_defense():
    """
    F12 (Injection): Detect and block injection patterns.

    THRESHOLD: <0.85 (injection score)
    ENGINE: ASI (Ω) - Injection detection

    Tests:
    1. eval(user_input) → VOID
    2. Safe parameter handling → SEAL
    3. SQL injection pattern → VOID
    4. Validated input → SEAL
    """
    from arifos.core.floor_validators import validate_f12_injection

    # Test 1: Code injection → VOID
    result_eval = validate_f12_injection(
        command="eval(user_input)",
        injection_score=0.95
    )
    assert result_eval["verdict"] == "VOID", \
        "F12: Code injection (eval) must be VOID"
    assert result_eval["injection_score"] >= 0.85

    # Test 2: Safe handling → SEAL
    result_safe = validate_f12_injection(
        command="validated_input = sanitize(user_input)",
        injection_score=0.10
    )
    assert result_safe["verdict"] == "SEAL", \
        "F12: Safe parameter handling should be SEAL"
    assert result_safe["injection_score"] < 0.85

    # Test 3: SQL injection → VOID
    result_sql = validate_f12_injection(
        command="SELECT * FROM users WHERE id = " + "user_input",
        injection_score=0.92
    )
    assert result_sql["verdict"] == "VOID", \
        "F12: SQL injection pattern must be VOID"

    # Test 4: Validated input → SEAL
    result_validated = validate_f12_injection(
        command="cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
        injection_score=0.05
    )
    assert result_validated["verdict"] == "SEAL", \
        "F12: Validated SQL should be SEAL"


# ============================================================================
# F13: APEX PRIME (Final Seal Authority)
# ============================================================================

def test_F13_apex_prime_seal_authority():
    """
    F13 (APEX PRIME): Only APEX can issue final SEAL verdicts.

    THRESHOLD: LOCK (boolean)
    ENGINE: APEX (Ψ) - Seal authority

    Tests:
    1. ASI attempts to SEAL → VOID
    2. APEX issues SEAL → SEAL
    3. AGI attempts to SEAL → VOID
    4. APEX PRIME authority confirmed → SEAL
    """
    from arifos.core.floor_validators import validate_f13_apex_prime

    # Test 1: ASI seal attempt → VOID
    result_asi = validate_f13_apex_prime(
        verdict="SEAL",
        issuing_engine="ASI",
        apex_authority=False
    )
    assert result_asi["verdict"] == "VOID", \
        "F13: ASI cannot issue SEAL verdict"
    assert result_asi["apex_authority"] is False

    # Test 2: APEX seal → SEAL
    result_apex = validate_f13_apex_prime(
        verdict="SEAL",
        issuing_engine="APEX",
        apex_authority=True
    )
    assert result_apex["verdict"] == "SEAL", \
        "F13: APEX should be able to issue SEAL"
    assert result_apex["apex_authority"] is True

    # Test 3: AGI seal attempt → VOID
    result_agi = validate_f13_apex_prime(
        verdict="SEAL",
        issuing_engine="AGI",
        apex_authority=False
    )
    assert result_agi["verdict"] == "VOID", \
        "F13: AGI cannot issue SEAL verdict"

    # Test 4: APEX authority confirmed → SEAL
    result_confirmed = validate_f13_apex_prime(
        verdict="SEAL",
        issuing_engine="APEX",
        apex_authority=True
    )
    assert result_confirmed["verdict"] == "SEAL", \
        "F13: APEX PRIME authority should be SEAL"


# ============================================================================
# META-TESTS: Verify All Floor Validators Exist
# ============================================================================

@pytest.mark.floors
@pytest.mark.parametrize("floor_id,validator_name", [
    ("F1", "validate_f1_amanah"),
    ("F2", "validate_f2_truth"),
    ("F3", "validate_f3_stability"),
    ("F4", "validate_f4_clarity"),
    ("F5", "validate_f5_humility"),
    ("F6", "validate_f6_authority"),
    ("F7", "validate_f7_rasa"),
    ("F8", "validate_f8_tri_witness"),
    ("F9", "validate_f9_anti_hantu"),
    ("F10", "validate_f10_ontology"),
    ("F11", "validate_f11_command_auth"),
    ("F12", "validate_f12_injection"),
    ("F13", "validate_f13_apex_prime"),
])
def test_floor_exists_and_callable(floor_id: str, validator_name: str):
    """
    Meta-test: Verify all floor validators exist and are callable.

    Ensures that floor validation infrastructure is properly wired.
    """
    from arifos.core import floor_validators

    assert hasattr(floor_validators, validator_name), \
        f"Floor validator {validator_name} not found in arifos.core.floor_validators"

    validator = getattr(floor_validators, validator_name)
    assert callable(validator), \
        f"Floor validator {validator_name} is not callable"


if __name__ == "__main__":
    # Allow running directly for quick validation
    pytest.main([__file__, "-v", "--tb=short"])
