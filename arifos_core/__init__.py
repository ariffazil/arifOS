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

This module exposes the primitives and integrations to apply these checks,
run APEX verdicts, and interact with the Cooling Ledger and Vault-999.
It intentionally does not implement "agency" as metaphysics — it implements
a controllable, auditable governance metabolism.

See PHYSICS_CODEX.md (CHAPTER 6) for the full technical statement and diagram.
"""

# Import base types first
from .metrics import Metrics, FloorsVerdict

# Import APEX components
from .APEX_PRIME import apex_review, ApexVerdict, Verdict, check_floors, APEXPrime

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

# Import guard LAST (after all its dependencies are loaded)
try:
    from .guard import apex_guardrail, GuardrailError
except ImportError:
    # Guard requires memory module, make it optional
    apex_guardrail = None
    GuardrailError = None

__all__ = [
    # Metrics
    "Metrics",
    "FloorsVerdict",
    # APEX
    "apex_review",
    "check_floors",
    "ApexVerdict",
    "Verdict",
    "APEXPrime",
    # Memory
    "log_cooling_entry",
    # Guard (may be None if memory unavailable)
    "apex_guardrail",
    "GuardrailError",
]