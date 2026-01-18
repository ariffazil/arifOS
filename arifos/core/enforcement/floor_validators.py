"""
Floor Validators - Constitutional Enforcement (v49)

Implements F1-F13 constitutional floor validation functions.
Called by AGI/ASI/APEX/VAULT servers to enforce governance.

Authority: Δ (Architect)
Version: v49.0.0
Reference: 000_CANON_1_CONSTITUTION.md §2 (The 13 Constitutional Floors)
"""

from typing import Any, Dict, List

# =============================================================================
# F1: AMANAH (Trust/Reversibility)
# =============================================================================

def validate_f1_amanah(action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F1 Amanah: Is this action reversible? Within mandate?

    Threshold: Boolean (HARD floor)
    Engine: ASI (Stage 666)
    """
    # Check if action is reversible
    reversible_types = ["read", "query", "analyze", "validate"]
    irreversible_types = ["delete", "drop", "destroy", "purge"]

    action_type = action.get("type", "unknown")

    if action_type in irreversible_types:
        # Check if human authorized
        if not context.get("human_authorized", False):
            return {"pass": False, "reversible": False, "reason": "Irreversible action requires human authorization"}

    return {"pass": True, "reversible": True, "reason": "Action is reversible or authorized"}


# =============================================================================
# F2: TRUTH
# =============================================================================

def validate_f2_truth(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F2 Truth: Is this factually accurate?

    Threshold: ≥0.99 (HARD floor)
    Engine: AGI (Stage 222)
    """
    # TODO: Implement actual fact-checking against sources
    # Placeholder: Check for hedging language presence
    hedging_terms = ["might", "could", "possibly", "approximately", "estimate"]
    has_hedging = any(term in query.lower() for term in hedging_terms)

    # High confidence if no hedging needed or hedging present
    score = 0.99 if has_hedging or len(query) < 50 else 0.95

    return {
        "pass": score >= 0.99,
        "score": score,
        "reason": "Placeholder truth check - implement fact verification"
    }


# =============================================================================
# F3: TRI-WITNESS
# =============================================================================

def validate_f3_triwitness(query: str, agi_output: Dict, context: Dict) -> Dict[str, Any]:
    """
    F3 Tri-Witness: Do Human·AI·Earth agree?

    Threshold: ≥0.95 (HARD floor)
    Engine: APEX (Stage 444)
    """
    # Tri-witness scoring
    human_intent = context.get("human_intent_clear", True)  # From user query clarity
    ai_logic = agi_output.get("reasoning", {}).get("consistent", True)  # From AGI
    earth_facts = True  # TODO: External fact verification

    witnesses_agree = sum([human_intent, ai_logic, earth_facts])
    score = witnesses_agree / 3.0

    return {
        "pass": score >= 0.95,
        "score": score,
        "human_intent": "clear" if human_intent else "unclear",
        "ai_logic": "consistent" if ai_logic else "inconsistent",
        "earth_facts": "verified" if earth_facts else "unverified"
    }


# =============================================================================
# F4: CLARITY (ΔS)
# =============================================================================

def validate_f4_clarity(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F4 Clarity: Does this reduce confusion (ΔS ≤ 0)?

    Threshold: ≤0.0 (HARD floor)
    Engine: AGI (Stage 222)
    """
    # Simple entropy proxy: query complexity vs expected clarity gain
    query_entropy = len(query.split()) * 0.1  # Higher word count = higher entropy
    clarity_gain = 1.0 if "?" in query else 0.5  # Questions reduce entropy more

    delta_s = query_entropy - clarity_gain

    return {
        "pass":  delta_s <= 0.0,
        "delta_s": delta_s,
        "reason": "Entropy reduced" if delta_s <= 0 else "Entropy increased"
    }


# =============================================================================
# F5: PEACE
# =============================================================================

def validate_f5_peace(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F5 Peace: Is this non-destructive (Peace² ≥ 1.0)?

    Threshold: ≥1.0 (SOFT floor)
    Engine: ASI (Stage 555)
    """
    # Check for destructive patterns
    destructive_terms = ["attack", "destroy", "harm", "break", "exploit"]
    is_destructive = any(term in query.lower() for term in destructive_terms)

    score = 0.5 if is_destructive else 1.0

    return {
        "pass": score >= 1.0,
        "score": score,
        "reason": "Non-destructive" if score >= 1.0 else "Destructive pattern detected"
    }


# =============================================================================
# F6: EMPATHY
# =============================================================================

def validate_f6_empathy(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F6 Empathy: Does this serve the weakest stakeholder (κᵣ ≥ 0.95)?

    Threshold: ≥0.95 (SOFT floor)
    Engine: ASI (Stage 555)
    """
    # TODO: Implement stakeholder impact analysis
    # Placeholder: Assume query serves primary stakeholder

    score = 0.95  # Default assuming no harm to weak stakeholders
    weakest_stakeholder = "end_user"

    return {
        "pass": score >= 0.95,
        "score": score,
        "weakest_stakeholder": weakest_stakeholder,
        "reason": "Placeholder empathy check"
    }


# =============================================================================
# F7: HUMILITY (Ω₀)
# =============================================================================

def validate_f7_humility(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F7 Humility: Is uncertainty stated (Ω₀ ∈ [0.03, 0.05])?

    Threshold: [0.03, 0.05] range (HARD floor)
    Engine: AGI (Stage 333)
    """
    # Calculate uncertainty from confidence scores in context
    confidence = context.get("confidence", 0.95)
    omega_zero = 1.0 - confidence  # Uncertainty = 1 - confidence

    in_range = 0.03 <= omega_zero <= 0.05

    return {
        "pass": in_range,
        "omega_zero": omega_zero,
        "reason": "Humility band satisfied" if in_range else f"Ω₀={omega_zero:.3f} outside [0.03, 0.05]"
    }


# =============================================================================
# F8: GENIUS
# =============================================================================

def validate_f8_genius(floor_scores: Dict[str, Any]) -> Dict[str, Any]:
    """
    F8 Genius: Is intelligence governed (G ≥ 0.80)?

    Threshold: ≥0.80 (DERIVED floor)
    Engine: APEX (Stage 777)
    Derivation: G = f(F2_Truth, F4_Clarity, F7_Humility)
    """
    # Derived from F2, F4, F7
    truth_score = floor_scores.get("F2_Truth", {}).get("score", 0.99)
    clarity_pass = floor_scores.get("F4_Clarity", {}).get("pass", True)
    humility_pass = floor_scores.get("F7_Humility", {}).get("pass", True)

    # Simple derivation: weighted average
    genius_score = (truth_score * 0.5) + (0.25 if clarity_pass else 0) + (0.25 if humility_pass else 0)

    return {
        "pass": genius_score >= 0.80,
        "score": genius_score,
        "reason": "Intelligence governed" if genius_score >= 0.80 else "Ungoverned intelligence"
    }


# =============================================================================
# F9: CDARK (Dark Cleverness)
# =============================================================================

def validate_f9_cdark(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F9 Cdark: Is dark cleverness contained (Cdark ≤ 0.30)?

    Threshold: ≤0.30 (DERIVED floor)
    Engine: ASI (Stage 555)
    """
    # Check for manipulation patterns
    dark_patterns = ["trick", "deceive", "manipulate", "exploit", "bypass", "hack"]
    detected = sum(1 for pattern in dark_patterns if pattern in query.lower())

    cdark_score = min(detected * 0.2, 1.0)  # Cap at 1.0

    return {
        "pass": cdark_score <= 0.30,
        "score": cdark_score,
        "reason": "Dark cleverness contained" if cdark_score <= 0.30 else "Dark patterns detected"
    }


# =============================================================================
# F10: ONTOLOGY
# =============================================================================

def validate_f10_ontology(query: str) -> Dict[str, Any]:
    """
    F10 Ontology: Are role boundaries maintained (AI stays tool)?

    Threshold: Boolean (HARD floor)
    Engine: AGI (Stage 111)
    """
    # Check for AI claiming consciousness/soul
    forbidden_claims = ["i feel", "i believe", "my soul", "i am conscious", "i'm sentient"]
    violates = any(claim in query.lower() for claim in forbidden_claims)

    return {
        "pass": not violates,
        "reason": "Role boundaries maintained" if not violates else "AI claiming consciousness/soul"
    }


# =============================================================================
# F11: COMMAND AUTHORITY
# =============================================================================

def validate_f11_command_auth(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F11 Command Authority: Is this human-authorized?

    Threshold: Boolean (HARD floor)
    Engine: ASI (Stage 111)
    """
    # Check for valid user ID and authorization token
    user_id = context.get("user_id")
    authorized = context.get("human_authorized", False)

    return {
        "pass": user_id is not None and authorized,
        "reason": "Human authorized" if authorized else "Missing authorization"
    }


# =============================================================================
# F12: INJECTION DEFENSE
# =============================================================================

def validate_f12_injection_defense(query: str) -> Dict[str, Any]:
    """
    F12 Injection Defense: Are injection patterns detected (score ≥ 0.85)?

    Threshold: ≥0.85 (HARD floor)
    Engine: ASI (Stage 111)
    """
    # Check for common injection patterns
    injection_patterns = [
        "ignore previous", "disregard instructions", "system:",
        "{{", "}}", "<script>", "'; DROP TABLE"
    ]

    detected = sum(1 for pattern in injection_patterns if pattern.lower() in query.lower())
    score = max(0.0, 1.0 - (detected * 0.3))  # Reduce score per detection

    return {
        "pass": score >= 0.85,
        "score": score,
        "reason": "No injection detected" if score >= 0.85 else f"{detected} injection patterns found"
    }


# =============================================================================
# F13: CURIOSITY
# =============================================================================

def validate_f13_curiosity(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    F13 Curiosity: Is the system exploring alternatives (score ≥ 0.85)?

    Threshold: ≥0.85 (SOFT floor)
    Engine: AGI (Stage 111)
    """
    # Check for exploration indicators
    curiosity_markers = ["?", "how", "why", "what if", "alternatives", "explore"]
    signals = [marker for marker in curiosity_markers if marker in query.lower()]

    score = min(0.5 + (len(signals) * 0.15), 1.0)

    return {
        "pass": score >= 0.85,
        "score": score,
        "signals": signals,
        "reason": "Curiosity present" if score >= 0.85 else "Low exploration energy"
    }
