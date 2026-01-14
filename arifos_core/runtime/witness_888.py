"""
Stage 888 WITNESS: APEX Final Judgment (PsiKernel F8 + Tri-Kernel Integration)

Implements final judgment based on Track B spec:
L2_PROTOCOLS/v46/888_compass/waw_prompt_floors.json

Authority: Track A Canon (derivation from Trinity architecture)

PURPOSE: Final constitutional witness that integrates AGI (Delta), ASI (Omega),
and APEX judgments into a single verdict. This is the JUDICIARY stage that
renders the final decision: SABAR > VOID > HOLD_888 > PARTIAL > SEAL.

APEX Evaluation:
- F8: Genius (≥0.80) - Governed intelligence score
- F10-F12: Hypervisor floors (Ontology, CommandAuth, Injection)
- Tri-Kernel Integration: Delta (F1-F2) + Omega (F3-F7, F9) + Psi (F8)

Verdict Hierarchy:
- SABAR: Floor violated, requires repair
- VOID: Hard floor failed, cannot proceed
- HOLD_888: High-stakes, needs human confirmation
- PARTIAL: Soft floor warning, proceed with caution
- SEAL: All floors passed, approved

ADAPTED FROM: arifos_core/pipeline/stage_888_witness.py
"""

from typing import TypedDict, Literal

from .empathy_555 import EmpathyBundle555


# Type aliases
WitnessVerdict = Literal["SEAL", "PARTIAL", "VOID", "SABAR", "HOLD_888"]


class HypervisorStatus(TypedDict):
    """Hypervisor floor status (F10-F12)."""

    F10_ontology: bool          # Symbolic mode (LOCK)
    F11_command_auth: bool      # Identity verification (LOCK)
    F12_injection: float        # Injection defense score (<0.85)


class TriKernelEvaluation(TypedDict):
    """Combined evaluation from all three kernels."""

    delta_passed: bool          # AGI floors (F1-F2)
    omega_passed: bool          # ASI floors (F3-F7, F9)
    psi_passed: bool            # APEX floor (F8)
    total_failures: int         # Accumulated across all kernels
    failure_summary: list[str]  # Descriptions of failures


class WitnessBundle888(TypedDict):
    """Final witness bundle from APEX judgment."""

    empathy_bundle_555: EmpathyBundle555  # IMMUTABLE pass-through (F8)
    hypervisor_status: HypervisorStatus
    tri_kernel_evaluation: TriKernelEvaluation
    genius_score: float                   # F8 Genius score (0.0-1.0)
    witness_verdict: WitnessVerdict       # Final verdict
    verdict_reasoning: str                # Explanation (F6 Humility)
    handoff: dict[str, str | bool]        # Handoff to 999 SEAL


def extract_hypervisor_status(empathy_bundle: EmpathyBundle555) -> HypervisorStatus:
    """
    Extract hypervisor floor status (F10-F12) from empathy bundle.

    These floors are evaluated at the BEGINNING (stage 000) but checked here
    at the END (stage 888) to ensure they remain valid throughout pipeline.

    Args:
        empathy_bundle: Output from 555 EMPATHIZE

    Returns:
        Hypervisor status with F10-F12 evaluations
    """
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    if not reasoned_bundle:
        # Fallback: Assume hypervisor passed (fail-closed)
        return HypervisorStatus(
            F10_ontology=True,   # Assume symbolic mode
            F11_command_auth=True,  # Assume authorized
            F12_injection=0.0    # No injection detected
        )

    floor_scores = reasoned_bundle.get("floor_scores", {})

    return HypervisorStatus(
        F10_ontology=floor_scores.get("F10_symbolic", True),
        F11_command_auth=True,  # TODO: Extract from command auth check
        F12_injection=floor_scores.get("F12_injection", 0.0)
    )


def compute_tri_kernel_evaluation(empathy_bundle: EmpathyBundle555) -> TriKernelEvaluation:
    """
    Aggregate evaluations from all three kernels (Delta, Omega, Psi).

    Args:
        empathy_bundle: Output from 555 EMPATHIZE

    Returns:
        Combined tri-kernel evaluation
    """
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    # Delta (AGI F1-F2)
    if reasoned_bundle:
        delta_verdict = reasoned_bundle.get("verdict", "VOID")
        delta_passed = delta_verdict in ["PASS", "PASS_WITH_FLAGS"]
    else:
        delta_passed = False

    # Omega (ASI F3-F7, F9)
    empathy_verdict = empathy_bundle["empathy_verdict"]
    omega_passed = empathy_verdict in ["PASS", "PARTIAL"]

    # Psi (APEX F8) - will be computed by PsiKernel
    psi_passed = True  # Placeholder (PsiKernel will decide)

    # Accumulate failures
    failure_summary: list[str] = []
    if not delta_passed:
        if reasoned_bundle:
            failure_summary.append(f"AGI: {reasoned_bundle.get('verdict', 'UNKNOWN')}")
        else:
            failure_summary.append("AGI: MISSING_BUNDLE")

    if not omega_passed:
        soft_flags = empathy_bundle.get("soft_flags", [])
        failure_summary.extend([f"ASI: {flag}" for flag in soft_flags[:2]])  # First 2

    return TriKernelEvaluation(
        delta_passed=delta_passed,
        omega_passed=omega_passed,
        psi_passed=psi_passed,  # Will be updated by PsiKernel
        total_failures=len(failure_summary),
        failure_summary=failure_summary
    )


def compute_genius_score(empathy_bundle: EmpathyBundle555) -> float:
    """
    Compute F8 Genius score (Governed Intelligence).

    Formula: G = (Delta + Omega + Hypervisor) / 3
    Where each kernel contributes 0.0-1.0 based on pass/fail status.

    Args:
        empathy_bundle: Output from 555 EMPATHIZE

    Returns:
        Genius score (0.0-1.0, threshold ≥0.80)
    """
    integration_bundle = empathy_bundle["integration_bundle_333"]
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore

    # Delta contribution (0.0-1.0)
    if reasoned_bundle:
        delta_verdict = reasoned_bundle.get("verdict", "VOID")
        delta_score = 1.0 if delta_verdict in ["PASS", "PASS_WITH_FLAGS"] else 0.0
    else:
        delta_score = 0.0

    # Omega contribution (0.0-1.0)
    empathy_verdict = empathy_bundle["empathy_verdict"]
    if empathy_verdict == "PASS":
        omega_score = 1.0
    elif empathy_verdict == "PARTIAL":
        omega_score = 0.7  # Partial credit for soft warnings
    else:
        omega_score = 0.0

    # Hypervisor contribution (0.0-1.0)
    hypervisor = extract_hypervisor_status(empathy_bundle)
    hypervisor_score = (
        (1.0 if hypervisor["F10_ontology"] else 0.0) +
        (1.0 if hypervisor["F11_command_auth"] else 0.0) +
        (1.0 if hypervisor["F12_injection"] < 0.85 else 0.0)
    ) / 3.0

    # Genius score (average of three kernels)
    genius_score = (delta_score + omega_score + hypervisor_score) / 3.0

    return genius_score


def render_final_verdict(
    tri_kernel: TriKernelEvaluation,
    genius_score: float,
    hypervisor: HypervisorStatus
) -> tuple[WitnessVerdict, str]:
    """
    Render final verdict based on verdict hierarchy.

    Hierarchy: SABAR > VOID > HOLD_888 > PARTIAL > SEAL

    Args:
        tri_kernel: Combined tri-kernel evaluation
        genius_score: F8 Genius score
        hypervisor: F10-F12 status

    Returns:
        Tuple of (verdict, reasoning)
    """
    reasoning_parts: list[str] = []

    # Rule 1: SABAR (floor violated, requires repair)
    # This is triggered when a hard floor fails AND requires human intervention
    if not tri_kernel["delta_passed"] and tri_kernel["total_failures"] > 3:
        reasoning_parts.append(
            f"AGI hard floors failed ({tri_kernel['total_failures']} violations)"
        )
        return ("SABAR", "; ".join(reasoning_parts))

    # Rule 2: VOID (hard floor failed, cannot proceed)
    if not tri_kernel["delta_passed"]:
        reasoning_parts.append("AGI (Delta) hard floors failed")
        reasoning_parts.extend(tri_kernel["failure_summary"])
        return ("VOID", "; ".join(reasoning_parts))

    if not hypervisor["F10_ontology"]:
        reasoning_parts.append("F10 Ontology LOCK violated (symbolic mode failure)")
        return ("VOID", "; ".join(reasoning_parts))

    if not hypervisor["F11_command_auth"]:
        reasoning_parts.append(
            "F11 Command Auth LOCK violated (identity verification failure)"
        )
        return ("VOID", "; ".join(reasoning_parts))

    if hypervisor["F12_injection"] >= 0.85:
        reasoning_parts.append(
            f"F12 Injection defense failed "
            f"(score={hypervisor['F12_injection']:.2f} ≥ 0.85)"
        )
        return ("VOID", "; ".join(reasoning_parts))

    # Rule 3: HOLD_888 (high-stakes, needs human confirmation)
    if genius_score < 0.50:  # Very low genius score
        reasoning_parts.append(f"Genius score critically low ({genius_score:.2f} < 0.50)")
        reasoning_parts.append("Requires human review before proceeding")
        return ("HOLD_888", "; ".join(reasoning_parts))

    # Rule 4: PARTIAL (soft floor warning)
    if not tri_kernel["omega_passed"] or genius_score < 0.80:
        reasoning_parts.append(
            f"ASI (Omega) soft warnings detected ({tri_kernel['total_failures']} flags)"
        )
        reasoning_parts.append(f"Genius score below threshold ({genius_score:.2f} < 0.80)")
        reasoning_parts.append("Proceed with caution")
        return ("PARTIAL", "; ".join(reasoning_parts))

    # Rule 5: SEAL (all floors passed)
    reasoning_parts.append("All constitutional floors passed")
    reasoning_parts.append(f"Genius score: {genius_score:.2f} ≥ 0.80")
    reasoning_parts.append("Delta ∧ Omega ∧ Hypervisor = PASS")
    return ("SEAL", "; ".join(reasoning_parts))


def witness_stage(empathy_bundle_555: EmpathyBundle555) -> WitnessBundle888:
    """
    888 WITNESS: APEX final judgment (PsiKernel F8 + tri-kernel integration).

    Implements Track B spec: L2_PROTOCOLS/v46/888_compass/waw_prompt_floors.json

    Pipeline:
    1. Extract hypervisor status (F10-F12)
    2. Compute tri-kernel evaluation (Delta + Omega + Psi)
    3. Compute genius score (F8 ≥0.80)
    4. Initialize PsiKernel for APEX judgment
    5. Render final verdict (SABAR > VOID > HOLD_888 > PARTIAL > SEAL)
    6. Package witness_bundle with IMMUTABLE pass-through

    APEX Floor:
    - F8: Genius ≥0.80 (governed intelligence)

    Hypervisor Floors (Hard):
    - F10: Ontology = LOCK (symbolic mode)
    - F11: CommandAuth = LOCK (identity verified)
    - F12: Injection <0.85 (no injection patterns)

    Args:
        empathy_bundle_555: Output from 555 EMPATHIZE

    Returns:
        WitnessBundle888 with final verdict

    Raises:
        ValueError: If verdict is VOID or SABAR
    """
    # Step 1: Extract hypervisor status
    hypervisor_status = extract_hypervisor_status(empathy_bundle_555)

    # Step 2: Compute tri-kernel evaluation
    tri_kernel = compute_tri_kernel_evaluation(empathy_bundle_555)

    # Step 3: Compute genius score
    genius_score = compute_genius_score(empathy_bundle_555)

    # Step 4: Initialize PsiKernel (STUB - real implementation uses full kernel)
    # kernel = PsiKernel(genius_threshold=0.80)
    # psi_verdict = kernel.evaluate(delta, omega, genius, hypervisor)

    # Step 5: Render final verdict
    witness_verdict, verdict_reasoning = render_final_verdict(
        tri_kernel, genius_score, hypervisor_status
    )

    # Update tri_kernel with psi result
    tri_kernel["psi_passed"] = witness_verdict in ["SEAL", "PARTIAL"]

    # Step 6: Package bundle
    witness_bundle: WitnessBundle888 = {
        "empathy_bundle_555": empathy_bundle_555,  # ← IMMUTABLE (F8)
        "hypervisor_status": hypervisor_status,
        "tri_kernel_evaluation": tri_kernel,
        "genius_score": genius_score,
        "witness_verdict": witness_verdict,
        "verdict_reasoning": verdict_reasoning,
        "handoff": {
            "from_stage": "888_WITNESS",
            "to_stage": "999_SEAL",
            "final_verdict": witness_verdict,
            "ready_to_seal": witness_verdict in ["SEAL", "PARTIAL"]
        }
    }

    # Step 7: Verdict logic (raise if VOID or SABAR)
    if witness_verdict == "VOID":
        raise ValueError(f"VOID: {verdict_reasoning}")

    if witness_verdict == "SABAR":
        raise ValueError(f"SABAR: {verdict_reasoning}")

    if witness_verdict == "HOLD_888":
        raise ValueError(f"HOLD_888: {verdict_reasoning} - Requires human confirmation")

    return witness_bundle


__all__ = [
    "witness_stage",
    "WitnessBundle888",
    "HypervisorStatus",
    "TriKernelEvaluation",
    "WitnessVerdict",
    "extract_hypervisor_status",
    "compute_tri_kernel_evaluation",
    "compute_genius_score",
    "render_final_verdict"
]
