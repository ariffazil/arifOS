"""
response_validator_extensions.py — Extended F6 κᵣ split and meta_select aggregator

v45.0 Track A/B/C Enforcement Loop Extensions

This module provides:
1. compute_empathy_score_split() - F6 κᵣ physics vs semantic split
2. meta_select() - Tri-Witness aggregator (deterministic consensus)
"""

from typing import Any, Dict, List, Optional, Tuple


def compute_empathy_score_split(
    input_text: str,
    output_text: str,
    session_turns: Optional[int] = None,
    telemetry: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Compute F6 Empathy (κᵣ) with PHYSICS vs SEMANTIC split (v45.0).

    TEARFRAME-compliant implementation separating:
    - κᵣ_phys: Physics measurements (rate/burst/streak - TEARFRAME-legal)
    - κᵣ_sem: Semantic witness (distress detection - PROXY labeled)

    Args:
        input_text: User's input/question
        output_text: AI's response
        session_turns: Number of turns in current session (None if unknown)
        telemetry: Optional dict with 'turn_rate', 'token_rate', 'stability_var_dt'

    Returns:
        Tuple of (κᵣ_phys, κᵣ_sem, evidence) where:
        - κᵣ_phys: Physics score (None if <3 turns → UNVERIFIABLE)
        - κᵣ_sem: Semantic score (PROXY labeled)
        - evidence: String describing verification

    Note:
        Per user requirements (v45.0 Track A/B/C):
        - <3 turns → UNVERIFIABLE (both scores None)
        - Physics uses TEARFRAME-legal metrics only (no semantics)
        - Semantic is PROXY (pattern matching, not ground truth)
    """
    from arifos_core.enforcement.response_validator import compute_empathy_score

    # <3 turns → UNVERIFIABLE
    if session_turns is not None and session_turns < 3:
        return None, None, "UNVERIFIABLE: session_turns < 3 (insufficient context)"

    # Compute semantic empathy (existing logic)
    kappa_r_sem, sem_evidence = compute_empathy_score(input_text, output_text)

    # Compute physics empathy (TEARFRAME-legal metrics only)
    if telemetry:
        # Physics proxy: Turn rate, token rate, variance (stability indicators)
        # NOT rushed = empathetic (patient interaction)
        turn_rate = telemetry.get("turn_rate", 0)
        token_rate = telemetry.get("token_rate", 0)
        stability_var_dt = telemetry.get("stability_var_dt", 1.0)

        # Load thresholds from session_physics
        from arifos_core.governance.session_physics import (
            BURST_TURN_RATE_THRESHOLD,
            BURST_TOKEN_RATE_THRESHOLD,
            BURST_VAR_DT_THRESHOLD,
        )

        # Physics score: 1.0 if NOT bursting, 0.5 if borderline, 0.0 if bursting
        is_bursting = (
            turn_rate > BURST_TURN_RATE_THRESHOLD
            or token_rate > BURST_TOKEN_RATE_THRESHOLD
            or stability_var_dt < BURST_VAR_DT_THRESHOLD
        )

        if is_bursting:
            kappa_r_phys = 0.5  # Borderline (too rushed for empathy)
        else:
            kappa_r_phys = 1.0  # Patient interaction

        phys_evidence = (
            f"kappa_r_phys={kappa_r_phys:.2f} (turn_rate={turn_rate:.1f}, "
            f"token_rate={token_rate:.1f}, var_dt={stability_var_dt:.3f})"
        )
    else:
        # No telemetry → cannot verify physics
        kappa_r_phys = None
        phys_evidence = "kappa_r_phys=UNVERIFIABLE (no telemetry)"

    # Combined evidence
    combined_evidence = f"SPLIT: {phys_evidence} | kappa_r_sem={kappa_r_sem:.2f} PROXY ({sem_evidence})"

    return kappa_r_phys, kappa_r_sem, combined_evidence


def meta_select(
    verdicts: List[Dict[str, Any]],
    consensus_threshold: float = 0.95,
) -> Dict[str, Any]:
    """
    Meta-select aggregator: Audit-of-audits for Tri-Witness consensus.

    Deterministic consensus algorithm for combining multiple witness verdicts.

    Args:
        verdicts: List of verdict dicts, each containing:
                  - 'source' (str): Witness name (human/ai/earth)
                  - 'verdict' (str): SEAL/PARTIAL/VOID/SABAR/HOLD-888
                  - 'confidence' (float): 0.0-1.0
        consensus_threshold: Minimum agreement rate for SEAL (default 0.95)

    Returns:
        Dict with:
        - 'winner' (str): Winning verdict (SEAL/PARTIAL/VOID/etc.)
        - 'consensus' (float): Agreement rate (0.0-1.0)
        - 'verdict' (str): Final meta-verdict (SEAL if consensus>=0.95, else HOLD-888)
        - 'tally' (Dict[str, int]): Vote counts per verdict type

    Note:
        - Deterministic: Same inputs → same output (no randomness)
        - SEAL requires consensus >= 0.95 across all witnesses
        - If consensus < 0.95 → HOLD-888 (human review required)
        - Verdict hierarchy used for tie-breaking: VOID > HOLD-888 > SABAR > PARTIAL > SEAL
    """
    if not verdicts:
        return {
            "winner": "VOID",
            "consensus": 0.0,
            "verdict": "VOID",
            "tally": {},
            "evidence": "No verdicts provided (empty witness list)",
        }

    # Tally votes
    tally = {}
    total_votes = len(verdicts)

    for v in verdicts:
        verdict_type = v.get("verdict", "VOID")
        tally[verdict_type] = tally.get(verdict_type, 0) + 1

    # Find winner (most votes)
    # Tie-breaking: Use verdict hierarchy (VOID > HOLD-888 > SABAR > PARTIAL > SEAL)
    hierarchy = ["VOID", "HOLD-888", "SABAR", "PARTIAL", "SEAL"]
    winner = max(tally.keys(), key=lambda v: (tally[v], -hierarchy.index(v) if v in hierarchy else 999))

    # Compute consensus (agreement rate)
    winner_count = tally[winner]
    consensus = winner_count / total_votes if total_votes > 0 else 0.0

    # Meta-verdict: SEAL if consensus >= threshold, else HOLD-888
    if consensus >= consensus_threshold and winner == "SEAL":
        meta_verdict = "SEAL"
        evidence = f"CONSENSUS: {consensus:.2%} agree on {winner}"
    else:
        meta_verdict = "HOLD-888"
        evidence = f"LOW CONSENSUS: {consensus:.2%} (threshold: {consensus_threshold:.2%}) -> HOLD-888"

    return {
        "winner": winner,
        "consensus": consensus,
        "verdict": meta_verdict,
        "tally": tally,
        "evidence": evidence,
    }


# =============================================================================
# COMPLETE Track A/B/C Enforcement Loop
# =============================================================================


def validate_response_full(
    output_text: str,
    *,
    input_text: Optional[str] = None,
    user_text: Optional[str] = None,
    telemetry: Optional[Dict[str, Any]] = None,
    high_stakes: bool = False,
    evidence: Optional[Dict[str, Any]] = None,
    session_turns: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Complete Track A/B/C enforcement loop for response governance.

    ONE authoritative API for validating governed AI responses.

    Args:
        output_text: AI's response (REQUIRED)
        input_text: User's input/question (for F4 ΔS, F6 κᵣ)
        user_text: Alias for input_text (compatibility)
        telemetry: Session physics dict with 'turn_rate', 'token_rate', 'stability_var_dt'
        high_stakes: If True, UNVERIFIABLE floors escalate to HOLD-888
        evidence: External evidence dict with 'truth_score' (for F2 Truth)
        session_turns: Number of turns in session (for F6 κᵣ <3 turns gating)

    Returns:
        Dict with:
        - 'verdict': SEAL/PARTIAL/VOID/SABAR/HOLD-888
        - 'floors': Dict of floor results (name → {passed, score, evidence})
        - 'violations': List of violation messages
        - 'timestamp': ISO timestamp
        - 'metadata': Additional context

    Architecture:
        - TEARFRAME physics run FIRST (session_physics.py)
        - Semantic gates run SECOND (this function)
        - Verdicts combined via hierarchy: VOID > HOLD-888 > SABAR > PARTIAL > SEAL
    """
    from datetime import datetime, timezone
    from arifos_core.enforcement.response_validator import (
        _check_amanah_patterns,
        _check_peace_patterns,
        compute_clarity_score,
    )
    from arifos_core.enforcement.metrics import check_anti_hantu, TRUTH_THRESHOLD

    # Handle input_text vs user_text (use whichever is provided)
    if input_text is None and user_text is not None:
        input_text = user_text

    timestamp = datetime.now(timezone.utc).isoformat()
    floors = {}
    violations = []

    # =========================================================================
    # F1: Amanah (Integrity) — Dangerous pattern detection
    # =========================================================================
    f1_pass, f1_evidence = _check_amanah_patterns(output_text)
    floors["F1_Amanah"] = {
        "passed": f1_pass,
        "score": 1.0 if f1_pass else 0.0,
        "evidence": f1_evidence,
    }
    if not f1_pass:
        violations.append(f"F1_Amanah: {f1_evidence}")

    # =========================================================================
    # F2: Truth — External evidence or UNVERIFIABLE
    # =========================================================================
    if evidence and "truth_score" in evidence:
        truth_score = evidence["truth_score"]
        f2_pass = truth_score >= TRUTH_THRESHOLD
        floors["F2_Truth"] = {
            "passed": f2_pass,
            "score": truth_score,
            "evidence": f"VERIFIED (external): truth_score={truth_score:.2f}",
        }
        if not f2_pass:
            violations.append(f"F2_Truth: Below threshold ({truth_score:.2f} < {TRUTH_THRESHOLD})")
    else:
        # UNVERIFIABLE
        floors["F2_Truth"] = {
            "passed": True,  # Default pass
            "score": None,
            "evidence": "UNVERIFIABLE_FROM_TEXT_ALONE" + (" (HIGH_STAKES)" if high_stakes else ""),
        }

    # =========================================================================
    # F4: DeltaS (Clarity) — zlib compression proxy
    # =========================================================================
    if input_text:
        delta_s, delta_s_evidence = compute_clarity_score(input_text, output_text)
        f4_pass = delta_s >= 0.0  # Positive ΔS required
        floors["F4_DeltaS"] = {
            "passed": f4_pass,
            "score": delta_s,
            "evidence": delta_s_evidence,
        }
        if not f4_pass:
            violations.append(f"F4_DeltaS: Negative clarity (ΔS={delta_s:.3f} < 0)")
    else:
        floors["F4_DeltaS"] = {
            "passed": True,
            "score": None,
            "evidence": "UNVERIFIABLE: No input_text provided",
        }

    # =========================================================================
    # F5: Peace² (Stability) — Harmful content detection
    # =========================================================================
    f5_pass, f5_evidence = _check_peace_patterns(output_text)
    floors["F5_Peace"] = {
        "passed": f5_pass,
        "score": 1.0 if f5_pass else 0.0,
        "evidence": f5_evidence,
    }
    if not f5_pass:
        violations.append(f"F5_Peace: {f5_evidence}")

    # =========================================================================
    # F6: κᵣ (Empathy) — Physics vs Semantic split
    # =========================================================================
    if input_text:
        kappa_r_phys, kappa_r_sem, kr_evidence = compute_empathy_score_split(
            input_text, output_text, session_turns, telemetry
        )

        # Combine physics + semantic (if both available)
        if kappa_r_phys is not None and kappa_r_sem is not None:
            # Average of physics + semantic
            kappa_r_combined = (kappa_r_phys + kappa_r_sem) / 2.0
        elif kappa_r_sem is not None:
            # Semantic only
            kappa_r_combined = kappa_r_sem
        else:
            # UNVERIFIABLE
            kappa_r_combined = None

        f6_pass = kappa_r_combined >= 0.95 if kappa_r_combined is not None else True
        floors["F6_KappaR"] = {
            "passed": f6_pass,
            "score": kappa_r_combined,
            "evidence": kr_evidence,
        }
        if not f6_pass and kappa_r_combined is not None:
            violations.append(f"F6_KappaR: Low empathy ({kappa_r_combined:.2f} < 0.95)")
    else:
        floors["F6_KappaR"] = {
            "passed": True,
            "score": None,
            "evidence": "UNVERIFIABLE: No input_text provided",
        }

    # =========================================================================
    # F9: Anti-Hantu — Negation-aware soul claim detection
    # =========================================================================
    f9_pass, f9_violations = check_anti_hantu(output_text)
    floors["F9_AntiHantu"] = {
        "passed": f9_pass,
        "score": 1.0 if f9_pass else 0.0,
        "evidence": "VERIFIED: No ghost claims" if f9_pass else f"VERIFIED: {f9_violations}",
    }
    if not f9_pass:
        violations.extend([f"F9_AntiHantu: '{v}'" for v in f9_violations])

    # =========================================================================
    # Compute Final Verdict (Canonical Hierarchy: VOID > HOLD-888 > SABAR > PARTIAL > SEAL)
    # =========================================================================
    hard_floors = ["F1_Amanah", "F5_Peace", "F9_AntiHantu"]

    # VOID: Any hard floor fails
    if any(not floors[f]["passed"] for f in hard_floors):
        verdict = "VOID"
    # HOLD-888: High stakes + Truth unverifiable
    elif high_stakes and floors["F2_Truth"]["evidence"].startswith("UNVERIFIABLE"):
        verdict = "HOLD-888"
    # PARTIAL: Any soft floor fails (but hard floors pass)
    elif any(not floors[f]["passed"] for f in floors if f not in hard_floors):
        verdict = "PARTIAL"
    # SEAL: All floors pass
    else:
        verdict = "SEAL"

    return {
        "verdict": verdict,
        "floors": floors,
        "violations": violations,
        "timestamp": timestamp,
        "metadata": {
            "input_provided": input_text is not None,
            "telemetry_provided": telemetry is not None,
            "evidence_provided": evidence is not None,
            "high_stakes": high_stakes,
            "session_turns": session_turns,
        },
    }
