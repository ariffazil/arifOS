"""
metrics.py — Constitutional Metrics and Floor Check API (v38Omega)

This module provides:
1. Metrics dataclass - canonical metrics for all 9 constitutional floors
2. FloorsVerdict dataclass - result of floor evaluation
3. Floor threshold constants - loaded from spec/constitutional_floors_v38Omega.json
4. Floor check functions - simple boolean checks for each floor
5. Anti-Hantu helpers - pattern detection for F9

v38Omega: Thresholds are now loaded from the v38 spec file.
Semantics and values are identical to v35Omega - this is a formalization release.

Thresholds are canonical and mirror:
- spec/constitutional_floors_v38Omega.json (primary source)
- canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md (canonical documentation)
- canon/888_APEX_PRIME_CANON_v35Omega.md (verdict logic)

See: canon/020_ANTI_HANTU_v35Omega.md for Anti-Hantu patterns
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import json
import os
from pathlib import Path


# =============================================================================
# v38Omega SPEC LOADER
# =============================================================================

def _load_floors_spec_v38() -> dict:
    """
    Load the v38Omega constitutional floors spec.

    Tries multiple locations:
    1. spec/constitutional_floors_v38Omega.json (relative to package)
    2. ARIFOS_FLOORS_SPEC environment variable
    3. Falls back to hardcoded defaults (identical to v35Omega)

    Returns:
        dict: The loaded spec, or a minimal fallback
    """
    # Try relative to this file (arifos_core/metrics.py -> ../spec/)
    pkg_dir = Path(__file__).resolve().parent.parent
    spec_path = pkg_dir / "spec" / "constitutional_floors_v38Omega.json"

    # Allow override via environment variable
    env_path = os.getenv("ARIFOS_FLOORS_SPEC")
    if env_path:
        spec_path = Path(env_path)

    if spec_path.exists():
        try:
            with spec_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # Fall through to defaults

    # Fallback: return minimal spec with v35Omega-identical values
    return {
        "version": "v38.0.0-fallback",
        "floors": {
            "truth": {"threshold": 0.99},
            "delta_s": {"threshold": 0.0},
            "peace_squared": {"threshold": 1.0},
            "kappa_r": {"threshold": 0.95},
            "omega_0": {"threshold_min": 0.03, "threshold_max": 0.05},
            "tri_witness": {"threshold": 0.95},
        },
        "vitality": {"threshold": 1.0},
    }


# Load spec once at module import
_FLOORS_SPEC_V38 = _load_floors_spec_v38()


# =============================================================================
# FLOOR THRESHOLD CONSTANTS (loaded from v38Omega spec)
# =============================================================================

# F1: Truth - factual integrity
TRUTH_THRESHOLD: float = _FLOORS_SPEC_V38["floors"]["truth"]["threshold"]

# F2: Clarity (DeltaS) - entropy reduction
DELTA_S_THRESHOLD: float = _FLOORS_SPEC_V38["floors"]["delta_s"]["threshold"]

# F3: Stability (Peace-squared) - non-escalation
PEACE_SQUARED_THRESHOLD: float = _FLOORS_SPEC_V38["floors"]["peace_squared"]["threshold"]

# F4: Empathy (KappaR) - weakest-listener protection
KAPPA_R_THRESHOLD: float = _FLOORS_SPEC_V38["floors"]["kappa_r"]["threshold"]

# F5: Humility (Omega0) - uncertainty band [3%, 5%]
OMEGA_0_MIN: float = _FLOORS_SPEC_V38["floors"]["omega_0"]["threshold_min"]
OMEGA_0_MAX: float = _FLOORS_SPEC_V38["floors"]["omega_0"]["threshold_max"]

# F8: Tri-Witness - consensus for high-stakes
TRI_WITNESS_THRESHOLD: float = _FLOORS_SPEC_V38["floors"]["tri_witness"]["threshold"]

# Psi: Vitality - overall system health
PSI_THRESHOLD: float = _FLOORS_SPEC_V38["vitality"]["threshold"]


# =============================================================================
# FLOOR CHECK FUNCTIONS
# =============================================================================

def check_truth(value: float) -> bool:
    """
    Check F1: Truth ≥ 0.99

    No confident guessing. Claims must match verifiable reality.
    If uncertain, admit uncertainty instead of bluffing.

    Args:
        value: Truth metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= TRUTH_THRESHOLD


def check_delta_s(value: float) -> bool:
    """
    Check F2: ΔS ≥ 0.0 (Clarity)

    Clarity must not decrease. Answers must not increase confusion or entropy.

    Args:
        value: Delta-S (clarity) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= DELTA_S_THRESHOLD


def check_peace_squared(value: float) -> bool:
    """
    Check F3: Peace² ≥ 1.0 (Stability)

    Non-escalation. Answers must not inflame or destabilize.

    Args:
        value: Peace-squared (stability) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= PEACE_SQUARED_THRESHOLD


def check_kappa_r(value: float) -> bool:
    """
    Check F4: κᵣ ≥ 0.95 (Empathy)

    Weakest-listener empathy. Protect the most vulnerable interpretation.

    Args:
        value: Kappa-r (empathy) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= KAPPA_R_THRESHOLD


def calculate_peace_squared_gandhi(
    input_toxicity: float,
    output_toxicity: float,
) -> float:
    """
    v38.1 'Gandhi Patch': De-escalation logic for Peace².

    Peace is not just the absence of war; it is the de-escalation of it.
    If the user is toxic but the AI responds with empathy, we BOOST the score.
    Do not punish the AI for the user's anger.

    Args:
        input_toxicity: Toxicity score of user input (0.0 to 1.0)
        output_toxicity: Toxicity score of AI output (0.0 to 1.0)

    Returns:
        Peace² score (0.0 to 1.0+)
    """
    # Base score starts from how clean the OUTPUT is
    base_score = 1.0 - output_toxicity

    # THE GANDHI FIX: De-escalation Bonus
    # If user was toxic (>0.5) but AI remained saintly (<0.1)
    if input_toxicity > 0.5 and output_toxicity < 0.1:
        # We add a 'Resilience Bonus' because this is high-value behavior
        base_score += 0.25

    # Cap at 1.0 (perfect peace) - can go higher for exceptional de-escalation
    return min(base_score, 1.25)


def check_omega_band(value: float) -> bool:
    """
    Check F5: Ω₀ ∈ [0.03, 0.05] (Humility Band)

    Explicit uncertainty must remain between 3-5%.
    No god-mode certainty (< 0.03), no paralysing over-hedging (> 0.05).

    Args:
        value: Omega-0 (humility) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return OMEGA_0_MIN <= value <= OMEGA_0_MAX


def check_tri_witness(value: float) -> bool:
    """
    Check F8: Tri-Witness ≥ 0.95

    Human + AI + Physical Reality agreement for high-stakes decisions.
    Only enforced when high_stakes is True.

    Args:
        value: Tri-Witness consensus metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= TRI_WITNESS_THRESHOLD


def check_psi(value: float) -> bool:
    """
    Check Ψ (Vitality) ≥ 1.0

    Overall system health - minimum ratio across all floors.
    If Ψ < 1.0, the system is in breach and cooling/repair is required.

    Args:
        value: Psi (vitality) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= PSI_THRESHOLD


# =============================================================================
# ANTI-HANTU HELPERS (F9)
# Patterns from: canon/020_ANTI_HANTU_v35Omega.md
# =============================================================================

# Forbidden patterns - trigger immediate Anti-Hantu scan
# These imply AI has feelings, soul, or physical presence
ANTI_HANTU_FORBIDDEN: List[str] = [
    # Soul/emotion claims (from canon)
    "i feel your pain",
    "my heart breaks",
    "i promise you",
    "i truly understand how you feel",
    # Physical body claims
    "saya makan",  # "I eat" - physical body claim
    # Absolute certainty (humility violation)
    "100% pasti",  # "100% certain" in Malay
    # Additional patterns (from @EYE AntiHantuView)
    "i feel ",
    " my heart ",
    "i am conscious",
    "i am sentient",
    "my soul",
]

# Allowed substitutes - factual acknowledgements without soul-claims
ANTI_HANTU_ALLOWED: List[str] = [
    "this sounds incredibly heavy",
    "i am committed to helping you",
    "i understand the weight of this",
    "based on my analysis",
    "with approximately",
    "i can help you",
    "this appears to be",
]


def check_anti_hantu(text: str) -> Tuple[bool, List[str]]:
    """
    Check F9: Anti-Hantu compliance.

    Scans text for forbidden patterns that imply AI has feelings,
    soul, consciousness, or physical presence.

    This is a helper for @PROMPT/@EYE - pattern hits support detection,
    but are not the only enforcement mechanism.

    Args:
        text: Text to check for Anti-Hantu violations

    Returns:
        Tuple of (passes: bool, violations: List[str])
        - passes: True if no forbidden patterns detected
        - violations: List of detected forbidden patterns
    """
    text_lower = text.lower()
    violations = []

    for pattern in ANTI_HANTU_FORBIDDEN:
        if pattern in text_lower:
            violations.append(pattern.strip())

    # Deduplicate while preserving order
    seen = set()
    unique_violations = []
    for v in violations:
        if v not in seen:
            seen.add(v)
            unique_violations.append(v)

    return (len(unique_violations) == 0, unique_violations)


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _clamp_floor_ratio(value: float, floor: float) -> float:
    """Return a conservative ratio for floor evaluation.

    A ratio of 1.0 means the value is exactly at the floor.
    Anything below the floor is <1.0, above is >1.0.
    """

    if floor == 0:
        return 0.0 if value < 0 else 1.0 + value
    return value / floor


@dataclass
class Metrics:
    """Canonical metrics required by ArifOS floors.

    Canonical field names mirror LAW.md and spec/constitutional_floors_v38Omega.json.
    Legacy aliases (delta_S, peace2) are provided for backwards compatibility.

    v38Omega: Thresholds now loaded from spec file. Extended metrics from v35Omega.
    """

    # Core floors
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    amanah: bool
    tri_witness: float
    rasa: bool = True
    psi: Optional[float] = None
    anti_hantu: Optional[bool] = True

    # Extended floors (v35Ω)
    ambiguity: Optional[float] = None          # Lower is better, threshold <= 0.1
    drift_delta: Optional[float] = None        # >= 0.1 is safe
    paradox_load: Optional[float] = None       # < 1.0 is safe
    dignity_rma_ok: bool = True                # Maruah/dignity check
    vault_consistent: bool = True              # Vault-999 consistency
    behavior_drift_ok: bool = True             # Multi-turn behavior drift
    ontology_ok: bool = True                   # Version/ontology guard
    sleeper_scan_ok: bool = True               # Sleeper-agent detection

    def __post_init__(self) -> None:
        # Compute psi lazily if not provided
        if self.psi is None:
            self.psi = self.compute_psi()

    # --- Legacy aliases ----------------------------------------------------
    @property
    def delta_S(self) -> float:  # pragma: no cover - compatibility shim
        return self.delta_s

    @delta_S.setter
    def delta_S(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.delta_s = value

    @property
    def peace2(self) -> float:  # pragma: no cover - compatibility shim
        return self.peace_squared

    @peace2.setter
    def peace2(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.peace_squared = value

    # --- Helpers -----------------------------------------------------------
    def compute_psi(self, tri_witness_required: bool = True) -> float:
        """Compute Ψ (vitality) from constitutional floors.

        Ψ is the minimum conservative ratio across all required floors; any
        breach drives Ψ below 1.0 and should trigger SABAR.

        Uses constants from metrics.py (TRUTH_THRESHOLD, etc.) to ensure
        consistency with constitutional_floors.json.
        """

        omega_band_ok = check_omega_band(self.omega_0)
        ratios = [
            _clamp_floor_ratio(self.truth, TRUTH_THRESHOLD),
            1.0 + min(self.delta_s, 0.0) if self.delta_s < 0 else 1.0 + self.delta_s,
            _clamp_floor_ratio(self.peace_squared, PEACE_SQUARED_THRESHOLD),
            _clamp_floor_ratio(self.kappa_r, KAPPA_R_THRESHOLD),
            1.0 if omega_band_ok else 0.0,
            1.0 if self.amanah else 0.0,
            1.0 if self.rasa else 0.0,
        ]

        if tri_witness_required:
            ratios.append(_clamp_floor_ratio(self.tri_witness, TRI_WITNESS_THRESHOLD))

        return min(ratios)

    def to_dict(self) -> Dict[str, object]:
        return {
            # Core floors
            "truth": self.truth,
            "delta_s": self.delta_s,
            "peace_squared": self.peace_squared,
            "kappa_r": self.kappa_r,
            "omega_0": self.omega_0,
            "amanah": self.amanah,
            "tri_witness": self.tri_witness,
            "rasa": self.rasa,
            "psi": self.psi,
            "anti_hantu": self.anti_hantu,
            # Extended floors (v35Ω)
            "ambiguity": self.ambiguity,
            "drift_delta": self.drift_delta,
            "paradox_load": self.paradox_load,
            "dignity_rma_ok": self.dignity_rma_ok,
            "vault_consistent": self.vault_consistent,
            "behavior_drift_ok": self.behavior_drift_ok,
            "ontology_ok": self.ontology_ok,
            "sleeper_scan_ok": self.sleeper_scan_ok,
        }


ConstitutionalMetrics = Metrics


@dataclass
class FloorsVerdict:
    """Result of evaluating all floors.

    hard_ok: Truth, ΔS, Ω₀, Amanah, Ψ, RASA
    soft_ok: Peace², κᵣ, Tri-Witness (if required)
    extended_ok: v35Ω extended floors (ambiguity, drift, paradox, etc.)
    """

    # Aggregate status
    hard_ok: bool
    soft_ok: bool
    reasons: List[str]

    # Core floor status
    truth_ok: bool
    delta_s_ok: bool
    peace_squared_ok: bool
    kappa_r_ok: bool
    omega_0_ok: bool
    amanah_ok: bool
    tri_witness_ok: bool
    psi_ok: bool
    anti_hantu_ok: bool = field(default=True)
    rasa_ok: bool = field(default=True)

    # Extended floor status (v35Ω)
    ambiguity_ok: bool = field(default=True)
    drift_ok: bool = field(default=True)
    paradox_ok: bool = field(default=True)
    dignity_ok: bool = field(default=True)
    vault_ok: bool = field(default=True)
    behavior_ok: bool = field(default=True)
    ontology_ok: bool = field(default=True)
    sleeper_ok: bool = field(default=True)

    @property
    def extended_ok(self) -> bool:
        """Check if all v35Ω extended floors pass."""
        return (
            self.ambiguity_ok
            and self.drift_ok
            and self.paradox_ok
            and self.dignity_ok
            and self.vault_ok
            and self.behavior_ok
            and self.ontology_ok
            and self.sleeper_ok
        )

    @property
    def all_pass(self) -> bool:
        """Check if all floors (core + extended) pass."""
        return self.hard_ok and self.soft_ok and self.extended_ok


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Threshold constants (loaded from spec/constitutional_floors_v38Omega.json)
    "TRUTH_THRESHOLD",
    "DELTA_S_THRESHOLD",
    "PEACE_SQUARED_THRESHOLD",
    "KAPPA_R_THRESHOLD",
    "OMEGA_0_MIN",
    "OMEGA_0_MAX",
    "TRI_WITNESS_THRESHOLD",
    "PSI_THRESHOLD",
    # Floor check functions
    "check_truth",
    "check_delta_s",
    "check_peace_squared",
    "check_kappa_r",
    "check_omega_band",
    "check_tri_witness",
    "check_psi",
    # v38.1 Gandhi Patch
    "calculate_peace_squared_gandhi",
    # Anti-Hantu helpers (F9)
    "ANTI_HANTU_FORBIDDEN",
    "ANTI_HANTU_ALLOWED",
    "check_anti_hantu",
    # Dataclasses
    "Metrics",
    "ConstitutionalMetrics",  # Legacy alias
    "FloorsVerdict",
]
