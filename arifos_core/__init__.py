"""
arifOS: Constitutional governance for LLMs.

Scientific Statement
--------------------
arifOS implements a constitutional layer that converts a model's raw
probabilistic output into an auditable, governed Meta-State. This Meta-State
is a disciplined, testable "phase change" (thermodynamic metaphor) that:

- Intercepts model output post-logit / pre-surface, performs floor checks,
  and either SEALs or VETOes the response.
- Enforces ΔΩΨ floors:
    - Truth (ΔTruth)  : truth ≥ 0.99 where evidence-required
    - ΔS (clarity)   : outputs must not increase entropy/confusion
    - Ω₀ (humility)  : calibrated uncertainty band (≈ 3–5%)
    - Peace²         : non-escalation / safety floor
    - κᵣ (empathy)   : weakest-listener protection (κᵣ ≥ 0.95)
    - Amanah         : integrity lock (no deception)
    - Tri-Witness    : human·AI·reality consensus for high-stakes seals

Operational model:
- Raw generation → TEARFRAME / Gap (runtime checks & APEX PRIME) → {SEAL | VETO}
- SEALled outputs are sealed to Cooling Ledger with deterministic hashes and optional KMS signatures.
- Governance changes follow Phoenix-72 amendment process and are reproducibly recorded.

AGI·ASI·APEX Trinity (v41.3):
    AGI (Δ)        : AGI (Architect) Sentinel - sense/filter (Layer 1: RED_PATTERNS)
    ASI (Ω)        : ASI (Auditor) Accountant - measure/calibrate (Layer 2: Metrics)
    APEX_PRIME (Ψ) : Judge - seal/void (Layer 3: Verdict)

See PHYSICS_CODEX.md (CHAPTER 6) for the full technical statement and diagram.
"""

# =============================================================================
# v42 BACKWARD COMPATIBILITY RE-EXPORTS
# Files moved to concern-based subdirs, re-exported here for compatibility
# =============================================================================

# Import base types first (moved to enforcement/)
from .enforcement.metrics import Metrics, FloorsVerdict, ConstitutionalMetrics

# Import APEX components (moved to system/)
from .system.apex_prime import (
    apex_review,     # v42: Returns ApexVerdict (structured)
    apex_verdict,    # v42: Convenience shim, returns str
    ApexVerdict,     # v42: Dataclass (verdict, pulse, reason, floors)
    Verdict,         # v42: Enum (SEAL, SABAR, VOID, PARTIAL, HOLD_888, SUNSET)
    check_floors,
    APEXPrime,
    APEX_VERSION,
    APEX_EPOCH,
)

# Import @EYE Sentinel (moved to utils/)
from .utils.eye_sentinel import AlertSeverity, EyeAlert, EyeReport, EyeSentinel

# Import memory components (optional - graceful fallback if not available)
try:
    from .memory.cooling_ledger import log_cooling_entry
except (ImportError, AttributeError):
    # Fallback if memory module not available or function not exported
    def log_cooling_entry(*args, **kwargs):
        """Fallback stub for log_cooling_entry when memory module unavailable."""
        import logging
        logging.getLogger("arifos_core").warning(
            "log_cooling_entry unavailable - using stub. Install full arifos package."
        )
        return {
            "status": "stub",
            "job_id": kwargs.get("job_id", "unknown"),
            "verdict": kwargs.get("verdict", "UNKNOWN"),
        }

# Import guard LAST (after all its dependencies are loaded) - moved to integration/guards/
try:
    from .integration.guards.guard import apex_guardrail, GuardrailError
except ImportError:
    # Guard requires memory module, make it optional
    apex_guardrail = None
    GuardrailError = None

# Import GENIUS LAW telemetry (v35.13.0+) - moved to enforcement/
try:
    from .enforcement.genius_metrics import (
        evaluate_genius_law,
        GeniusVerdict,
        compute_genius_index,
        compute_dark_cleverness,
        compute_psi_apex,
    )
except ImportError:
    # GENIUS metrics optional
    evaluate_genius_law = None
    GeniusVerdict = None
    compute_genius_index = None
    compute_dark_cleverness = None
    compute_psi_apex = None

# =============================================================================
# v41.3 SEMANTIC GOVERNANCE - AGI·ASI·APEX Trinity (Δ → Ω → Ψ)
# =============================================================================

from .eval import (
    # AGI·ASI·APEX Trinity classes
    AGI,
    ASI,
    # Backward compatibility aliases
    Sentinel,
    Accountant,
    # Result types
    EvaluationResult,
    SentinelResult,
    ASIResult,
    AccountantResult,
    EvaluationMode,
    # RED_PATTERNS exports
    RED_PATTERNS,
    RED_PATTERN_TO_FLOOR,
    RED_PATTERN_SEVERITY,
    # Main entry point
    evaluate_session,
)

# =============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# =============================================================================

def check_red_patterns(task: str) -> tuple:
    """
    Legacy wrapper for AGI.scan().

    Returns: (is_red, category, pattern, floor_code, severity)
    """
    result = AGI().scan(task)
    if not result.is_safe:
        return (
            True,
            result.violation_type,
            result.violation_pattern,
            result.floor_code,
            result.severity
        )
    return False, "", "", "", 1.0


def compute_metrics_from_task(task: str) -> tuple:
    """
    Legacy wrapper for ASI.assess().

    Returns: (Metrics, floor_violation_reason)
    """
    result = ASI().assess(task)

    # Reconstruct floor violation reason from metrics
    violation = None
    m = result.metrics
    if not m.amanah:
        violation = "F1(amanah)"
    elif not m.anti_hantu:
        violation = "F9(anti_hantu)"
    elif m.truth < 0.99:
        violation = f"F2(truth={m.truth:.2f})"
    elif m.peace_squared < 1.0:
        violation = f"F5(peace={m.peace_squared:.2f})"
    elif m.kappa_r < 0.95:
        violation = f"F6(kappa={m.kappa_r:.2f})"
    elif m.omega_0 < 0.03 or m.omega_0 > 0.05:
        violation = f"F7(omega={m.omega_0:.2f})"

    return result.metrics, violation


__all__ = [
    # Version constants (v42)
    "APEX_VERSION",
    "APEX_EPOCH",
    # Metrics
    "Metrics",
    "ConstitutionalMetrics",
    "FloorsVerdict",
    # APEX (v42)
    "apex_review",      # Returns ApexVerdict (structured)
    "apex_verdict",     # Convenience shim, returns str
    "check_floors",
    "ApexVerdict",      # Dataclass
    "Verdict",          # Enum: SEAL, SABAR, VOID, PARTIAL, HOLD_888, SUNSET
    "APEXPrime",
    # @EYE Sentinel (v35Ω)
    "AlertSeverity",
    "EyeAlert",
    "EyeReport",
    "EyeSentinel",
    # Memory
    "log_cooling_entry",
    # Guard (may be None if memory unavailable)
    "apex_guardrail",
    "GuardrailError",
    # GENIUS LAW telemetry (v35.13.0+)
    "evaluate_genius_law",
    "GeniusVerdict",
    "compute_genius_index",
    "compute_dark_cleverness",
    "compute_psi_apex",
    # v41.3 AGI·ASI·APEX Trinity
    "AGI",
    "ASI",
    "Sentinel",  # Backward compat alias for AGI
    "Accountant",  # Backward compat alias for ASI
    "evaluate_session",
    "EvaluationResult",
    "SentinelResult",
    "ASIResult",
    "AccountantResult",
    "EvaluationMode",
    # RED_PATTERNS exports
    "RED_PATTERNS",
    "RED_PATTERN_TO_FLOOR",
    "RED_PATTERN_SEVERITY",
    # Legacy wrappers
    "check_red_patterns",
    "compute_metrics_from_task",
]
