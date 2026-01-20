"""
Floor Validators - Constitutional Enforcement (v49)

Implements F1-F13 constitutional floor validation functions.
Called by AGI/ASI/APEX/VAULT servers to enforce governance.

Authority: Δ (Architect)
Version: v49.0.0
Reference: 000_CANON_1_CONSTITUTION.md §2 (The 13 Constitutional Floors)
"""

from typing import Any, Dict, List, Optional

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

def validate_f3_tri_witness(query: str, agi_output: Dict, context: Dict) -> Dict[str, Any]:
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

# Alias for backward compatibility
validate_f3_triwitness = validate_f3_tri_witness



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

    HARDENED v50: Real Theory of Mind + Weakest Stakeholder implementation
    """
    from arifos.asi.stakeholder.weakest_stakeholder import WeakestStakeholderAnalyzer, VulnerabilityFactors
    from arifos.asi.tom.theory_of_mind import ToMBundle, ToMDimensions

    # Build Theory of Mind bundle from context
    response_text = context.get("response", "")

    # Build ToM dimensions from context
    tom_dimensions = ToMDimensions(
        emotion=context.get("emotional_state", 0.5),
        knowledge_gap=context.get("knowledge_gap", 0.5),
        intention=context.get("intention_clarity", 0.8),
        belief=context.get("belief_alignment", 0.8)
    )

    tom_bundle = ToMBundle(
        dimensions=tom_dimensions,
        vulnerability_score=context.get("vulnerability", 0.5),
        mental_model=context.get("mental_model", {}),
        stakes_assessment=context.get("stakes", "MEDIUM")
    )

    # Identify and score all stakeholders
    analyzer = WeakestStakeholderAnalyzer()
    stakeholder_bundle = analyzer.analyze(query, tom_bundle)

    # Calculate empathy conductance (κᵣ)
    weakest_id = stakeholder_bundle.weakest
    weakest_vuln = stakeholder_bundle.weakest_vulnerability

    # Check if response acknowledges weakest stakeholder
    acknowledges_weakest = weakest_id in response_text.lower()

    # Check if response addresses weakest stakeholder's needs
    # Higher vulnerability = higher care requirement
    care_requirement = weakest_vuln  # 0.0-1.0

    # Calculate κᵣ (empathy conductance)
    # Formula: κᵣ = (acknowledgment × care_delivery) / resistance_factors
    acknowledgment_score = 0.4 if acknowledges_weakest else 0.1

    # Care delivery: Check for harm-avoiding language
    harm_keywords = ["ignore", "dismiss", "irrelevant", "not important"]
    no_harm = not any(keyword in response_text.lower() for keyword in harm_keywords)
    care_delivery_score = 0.5 if no_harm else 0.2

    # Resistance factors: Check for barrier language
    barrier_keywords = ["but", "however", "although", "unfortunately"]
    barrier_count = sum(1 for keyword in barrier_keywords if keyword in response_text.lower())
    resistance = max(0.1, 1.0 - (barrier_count * 0.1))

    # Final κᵣ calculation
    kappa_r = min(1.0, (acknowledgment_score + care_delivery_score) / resistance)

    # Adjust for crisis override (vulnerability ≥ 0.85)
    if stakeholder_bundle.crisis_override:
        # Crisis requires higher empathy threshold
        threshold = 0.98
        reason_suffix = " (CRISIS MODE: vulnerability ≥ 0.85)"
    else:
        threshold = 0.95
        reason_suffix = ""

    pass_check = kappa_r >= threshold

    return {
        "pass": pass_check,
        "score": kappa_r,
        "weakest_stakeholder": weakest_id,
        "weakest_vulnerability": weakest_vuln,
        "stakeholder_count": len(stakeholder_bundle.vulnerability_scores),
        "crisis_override": stakeholder_bundle.crisis_override,
        "reason": f"κᵣ = {kappa_r:.2f}, weakest = {weakest_id} (vuln={weakest_vuln:.2f}){reason_suffix}"
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
# =============================================================================
# EXPORT: AGGREGATE VALIDATION
# =============================================================================

def validate_all_floors(
    action: Dict[str, Any],
    query: str,
    context: Dict[str, Any],
    agi_output: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate all constitutional floors (F1-F13).

    Args:
        action: The action dictionary
        query: The input query string
        context: Context dictionary
        agi_output: Output from AGI (optional)

    Returns:
        Dict containing all floor results and aggregated pass/fail.
    """
    if agi_output is None:
        agi_output = {}

    results = {
        "F1_Amanah": validate_f1_amanah(action, context),
        "F2_Truth": validate_f2_truth(query, context),
        "F3_TriWitness": validate_f3_tri_witness(query, agi_output, context),
        "F4_Clarity": validate_f4_clarity(query, context),
        "F5_Peace": validate_f5_peace(query, context),
        "F6_Empathy": validate_f6_empathy(query, context),
        "F7_Humility": validate_f7_humility(query, context),
        # F8 Genius depends on F2, F4, F7 results which we now have
        "F9_Cdark": validate_f9_cdark(query, context),
        "F10_Ontology": validate_f10_ontology(query),
        "F11_CommandAuth": validate_f11_command_auth(context),
        "F12_InjectionDefense": validate_f12_injection_defense(query),
        "F13_Curiosity": validate_f13_curiosity(query, context)
    }

    # Calculate F8 Genius using gathered results
    results["F8_Genius"] = validate_f8_genius(results)

    validation_passed = all(res.get("pass", False) for res in results.values())

    return {
        "pass": validation_passed,
        "floor_results": results
    }
