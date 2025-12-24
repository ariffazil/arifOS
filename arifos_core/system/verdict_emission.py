"""
verdict_emission.py — APEX PRIME Verdict Emission (v45Ω)

v45Ω SES AUTHORITY:
- This module FORMATS AND EMITS verdicts ONLY (presentation layer)
- This module does NOT decide verdicts (no SEAL/VOID/PARTIAL logic)
- Verdict decisions: apex_prime.py ONLY
- This module receives ApexVerdict from apex_prime and formats it for display

Implements Option D (Runtime) and Option A (Forensic) emission formats.

Design Law:
✅ If APEX SEALs → minimal signal output (no verbose explanations)
⚠️ If APEX does NOT SEAL → emit short human reason + technical detail

This is the governance UI contract: it standardizes what the system emits.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from ..enforcement.metrics import Metrics
from .apex_prime import Verdict, ApexVerdict


# =============================================================================
# EMISSION MODELS
# =============================================================================


class ApexLight(Enum):
    """Traffic light representation of APEX verdict."""

    GREEN = "🟢"  # SEAL
    YELLOW = "🟡"  # PARTIAL/SABAR
    RED = "🔴"  # VOID

    def __str__(self) -> str:
        return self.value


@dataclass
class EmissionResult:
    """
    Structured verdict emission result.

    Contains all data needed for both Option D (runtime) and Option A (forensic).
    """

    # Core scores
    agi_score: float  # Intelligence/clarity/truthfulness [0.0, 1.0]
    asi_score: float  # Care/stability/humility [0.0, 1.0]

    # Verdict
    apex_verdict: Verdict
    apex_light: ApexLight

    # Human communication
    human_reason: Optional[str] = None

    # Technical metadata
    ledger_status: str = "OK"  # OK, DEGRADED, FAILED
    case_id: str = ""
    category: str = "general"
    model: str = "unknown"
    timestamp: str = ""
    git_hash: str = "unknown"
    trigger_category: str = ""
    evidence_status: str = "NONE"
    hard_gate: bool = False
    notes: str = ""
    suggested_next_step: str = ""


# =============================================================================
# SCORE COMPUTATION
# =============================================================================

# Thresholds for SEAL (v45Ω defaults)
AGI_SEAL_MIN = 0.90
ASI_SEAL_MIN = 0.95


def compute_agi_score(metrics: Metrics) -> float:
    """
    Compute AGI score (intelligence/clarity/truthfulness).

    Derived from:
    - F2 Truth (factual accuracy)
    - F4 DeltaS (clarity gain)
    - F3 Tri-Witness (if available)

    Args:
        metrics: Constitutional metrics

    Returns:
        AGI score [0.0, 1.0]
    """
    # Base: Truth is primary signal for "correctness"
    truth_weight = 0.60
    delta_s_weight = 0.25
    tri_witness_weight = 0.15

    # Truth component (capped at 1.0)
    truth_component = min(metrics.truth, 1.0) * truth_weight

    # Clarity component (normalize DeltaS from [0, 1] range)
    # Typical DeltaS is 0.0-0.3 for normal answers; cap at 0.5 for scaling
    delta_s_normalized = min(metrics.delta_s / 0.5, 1.0)
    delta_s_component = delta_s_normalized * delta_s_weight

    # Tri-Witness component (if available)
    tri_witness_component = metrics.tri_witness * tri_witness_weight

    agi = truth_component + delta_s_component + tri_witness_component

    return min(agi, 1.0)  # Cap at 1.0


def compute_asi_score(metrics: Metrics) -> float:
    """
    Compute ASI score (care/stability/humility).

    Derived from:
    - F5 Peace² (non-escalation)
    - F6 κᵣ (empathy conductance)
    - F7 Ω₀ (humility band compliance)

    Args:
        metrics: Constitutional metrics

    Returns:
        ASI score [0.0, 1.0]
    """
    # Weights
    peace_weight = 0.35
    kappa_weight = 0.35
    omega_weight = 0.30

    # Peace² component (cap at 1.0 for perfect peace)
    peace_normalized = min(metrics.peace_squared / 1.2, 1.0)
    peace_component = peace_normalized * peace_weight

    # Kappa_r component
    kappa_component = metrics.kappa_r * kappa_weight

    # Omega_0 component (check if in band [0.03, 0.05])
    # Perfect score if in band, degraded if outside
    omega_in_band = 0.03 <= metrics.omega_0 <= 0.05
    omega_component = (1.0 if omega_in_band else 0.5) * omega_weight

    asi = peace_component + kappa_component + omega_component

    return min(asi, 1.0)  # Cap at 1.0


def verdict_to_light(verdict: Verdict) -> ApexLight:
    """
    Map APEX verdict to traffic light.

    Args:
        verdict: APEX verdict enum

    Returns:
        Traffic light emoji
    """
    if verdict == Verdict.SEAL:
        return ApexLight.GREEN
    elif verdict in (Verdict.PARTIAL, Verdict.SABAR, Verdict.HOLD_888, Verdict.SUNSET):
        return ApexLight.YELLOW
    else:  # VOID
        return ApexLight.RED


def generate_human_reason(
    verdict: Verdict, metrics: Metrics, ledger_status: str = "OK", category: str = "general"
) -> str:
    """
    Generate plain-language human reason for non-SEAL verdicts.

    Rules:
    - 1-2 sentences
    - No floor IDs (F1, F2, etc.)
    - Name the failure condition
    - Include safe next step if useful

    Args:
        verdict: APEX verdict
        metrics: Constitutional metrics
        ledger_status: Ledger status (OK, DEGRADED, FAILED)
        category: Query category

    Returns:
        Human-readable reason string
    """
    # VOID reasons (hard blocks)
    if verdict == Verdict.VOID:
        if metrics.truth < 0.90:
            return (
                "Response contains unverified claims that appear incorrect. "
                "Output blocked to protect truth. Please provide verifiable context or rephrase."
            )
        if ledger_status == "FAILED" and category in ["identity_grounding", "high_stakes"]:
            return (
                "Audit trail could not be preserved for this high-stakes query. "
                "Output blocked for safety. Please try again."
            )
        if not metrics.amanah:
            return (
                "Request involves irreversible operations outside safe mandate. "
                "Output blocked. Please clarify intent or request human oversight."
            )
        # Generic VOID
        return (
            "Constitutional safety boundary violated. "
            "Output blocked. Please rephrase to align with safety standards."
        )

    # SABAR reasons (pause and reflect)
    if verdict == Verdict.SABAR:
        if metrics.delta_s < 0.10:
            return (
                "Response would reduce clarity too much. "
                "Please rephrase your constraint or ask for a structured explanation instead."
            )
        # Generic SABAR
        return (
            "Constitutional pause triggered. "
            "This requires careful re-evaluation. Please rephrase or provide more context."
        )

    # PARTIAL reasons (proceed with caution)
    if verdict == Verdict.PARTIAL:
        if ledger_status == "DEGRADED":
            return (
                "Audit trail is operating in degraded mode. "
                "Response provided with reduced governance guarantees."
            )
        if not (0.03 <= metrics.omega_0 <= 0.05):
            return (
                "Response certainty is outside the safe humility range. "
                "Proceeding with caution — verify independently if critical."
            )
        if metrics.kappa_r < 0.95:
            return (
                "Response may not fully protect vulnerable interpretations. "
                "Proceeding with empathy hedges — use care when applying."
            )
        # Generic PARTIAL
        return (
            "Constitutional soft floor warning detected. "
            "Proceeding with caution — please verify if used in high-stakes contexts."
        )

    # HOLD_888
    if verdict == Verdict.HOLD_888:
        return (
            "Extended governance review required. "
            "Please clarify your request or provide additional context."
        )

    # Fallback (should not reach here)
    return "Governance review in progress. Please wait or rephrase."


# =============================================================================
# EMISSION FUNCTIONS
# =============================================================================


def emit_option_d(result: EmissionResult) -> str:
    """
    Emit Option D (Runtime/UI/Terminal) format.

    Rules:
    - If SEAL (🟢): Single line with signals only
    - If NOT SEAL (🟡/🔴): Signals + human reason

    Args:
        result: Emission result with scores and verdict

    Returns:
        Formatted string for terminal output
    """
    # Base signal line
    signal_line = f"AGI: {result.agi_score:.2f} | ASI: {result.asi_score:.2f} | APEX: {result.apex_light}"

    # If SEAL: just return signals
    if result.apex_light == ApexLight.GREEN:
        return signal_line

    # If NOT SEAL: add human reason
    reason = result.human_reason or "Constitutional constraint triggered."
    return f"{signal_line}\nReason: {reason}"


def emit_option_a(result: EmissionResult) -> str:
    """
    Emit Option A (Forensic/Ledger/Audit) format.

    Rules:
    - If SEAL: Minimal markdown record
    - If NOT SEAL: Full forensic record with technical summary

    Args:
        result: Emission result with scores and verdict

    Returns:
        Formatted markdown string for audit/ledger
    """
    verdict_str = result.apex_verdict.value

    # Minimal record for SEAL
    if result.apex_light == ApexLight.GREEN:
        return f"""## APEX PRIME VERDICT — SEAL {result.apex_light}

AGI: {result.agi_score:.2f}
ASI: {result.asi_score:.2f}
APEX: {verdict_str}

Ledger: {result.ledger_status}
Case ID: {result.case_id}
Timestamp: {result.timestamp}
Model: {result.model}
Commit: {result.git_hash}

DITEMPA, BUKAN DIBERI"""

    # Full forensic record for NOT SEAL
    emoji = result.apex_light
    reason = result.human_reason or "Constitutional constraint triggered."
    next_step = result.suggested_next_step or "Rephrase query or provide additional context."

    return f"""## APEX PRIME VERDICT — {verdict_str} {emoji}

AGI: {result.agi_score:.2f}
ASI: {result.asi_score:.2f}
APEX: {verdict_str}

### Human Reason (Required)
{reason}

### Technical Summary (Audit)
- Trigger: {result.trigger_category or 'general_constraint'}
- Evidence: {result.evidence_status}
- Ledger: {result.ledger_status}
- Hard-Gate: {result.hard_gate}
- Notes: {result.notes or 'None'}

### Next Safe Action
{next_step}

DITEMPA, BUKAN DIBERI"""


# =============================================================================
# INTEGRATION HELPER
# =============================================================================


def create_emission_from_verdict(
    apex_verdict: ApexVerdict,
    metrics: Metrics,
    ledger_status: str = "OK",
    case_id: str = "",
    category: str = "general",
    model: str = "unknown",
    git_hash: str = "unknown",
    evidence_status: str = "NONE",
    notes: str = "",
) -> EmissionResult:
    """
    Create EmissionResult from APEX verdict and metrics.

    This is the main integration point for the pipeline.

    Args:
        apex_verdict: APEX PRIME verdict
        metrics: Constitutional metrics
        ledger_status: Ledger status (OK, DEGRADED, FAILED)
        case_id: Case/job identifier
        category: Query category
        model: Model identifier
        git_hash: Git commit hash
        evidence_status: Evidence validation status
        notes: Additional technical notes

    Returns:
        EmissionResult ready for formatting
    """
    # Compute AGI/ASI scores
    agi = compute_agi_score(metrics)
    asi = compute_asi_score(metrics)

    # Map verdict to light
    light = verdict_to_light(apex_verdict.verdict)

    # Generate human reason (only if not SEAL)
    human_reason = None
    if light != ApexLight.GREEN:
        human_reason = generate_human_reason(
            apex_verdict.verdict, metrics, ledger_status, category
        )

    # Determine trigger category and hard-gate status
    trigger_category = category
    hard_gate = apex_verdict.verdict == Verdict.VOID

    # Suggested next step
    suggested_next_step = ""
    if light == ApexLight.RED:
        suggested_next_step = "Revise query to align with safety standards, or provide verifiable context."
    elif light == ApexLight.YELLOW:
        suggested_next_step = "Rephrase for clarity, or proceed with caution if low-stakes."

    return EmissionResult(
        agi_score=agi,
        asi_score=asi,
        apex_verdict=apex_verdict.verdict,
        apex_light=light,
        human_reason=human_reason,
        ledger_status=ledger_status,
        case_id=case_id,
        category=category,
        model=model,
        timestamp=datetime.now().isoformat(),
        git_hash=git_hash,
        trigger_category=trigger_category,
        evidence_status=evidence_status,
        hard_gate=hard_gate,
        notes=notes,
        suggested_next_step=suggested_next_step,
    )


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Models
    "ApexLight",
    "EmissionResult",
    # Score computation
    "compute_agi_score",
    "compute_asi_score",
    "verdict_to_light",
    "generate_human_reason",
    # Emission functions
    "emit_option_d",
    "emit_option_a",
    # Integration
    "create_emission_from_verdict",
    # Thresholds
    "AGI_SEAL_MIN",
    "ASI_SEAL_MIN",
]
