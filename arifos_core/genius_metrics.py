"""
genius_metrics.py — GENIUS LAW Telemetry (v35Omega Phase 1)

Implements the GENIUS LAW measurement layer from canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md.

This module provides:
1. Delta/Omega/Psi score computation from existing Metrics
2. Genius Index (G) — governed intelligence metric
3. Dark Cleverness (C_dark) — ungoverned intelligence risk
4. System Vitality (Psi_APEX) — global health metric
5. GeniusVerdict dataclass for telemetry

Phase 1: Telemetry only — no behavior changes.
Phase 2 (v36.0.0): APEX PRIME will use these for verdicts.

Key formulas:
    G = Δ · Ω · Ψ = A · P · X · E²
    C_dark = Δ · (1 - Ω) · (1 - Ψ)
    Ψ_APEX = (A · P · E · X) / (Entropy + ε)

See: docs/GENIUS_LAW_MEASUREMENT_SPEC.md
See: canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from arifos_core.metrics import (
    Metrics,
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    check_omega_band,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Default Energy value when not provided (neutral assumption)
DEFAULT_ENERGY: float = 1.0

# Epsilon for division safety in Ψ_APEX
EPSILON: float = 0.01

# Thresholds for GENIUS LAW evaluation
G_MIN_THRESHOLD: float = 0.5  # Below this = ungoverned
C_DARK_MAX_THRESHOLD: float = 0.3  # Above this = hazard warning
PSI_APEX_MIN: float = 1.0  # System health minimum


# =============================================================================
# SCORE COMPUTATION (Δ, Ω, Ψ from Metrics)
# =============================================================================

def compute_delta_score(m: Metrics) -> float:
    """
    Compute Δ (Delta/Clarity) score from Metrics.

    Δ maps to Akal (A) — cognitive clarity, pattern recognition.
    Derived from: truth, delta_s (clarity floor).

    Formula:
        Δ = (truth_ratio + clarity_ratio) / 2

    Where:
        truth_ratio = truth / TRUTH_THRESHOLD (clamped to [0, 1])
        clarity_ratio = 1.0 if delta_s >= 0 else (1 + delta_s) clamped to [0, 1]

    Args:
        m: Metrics instance

    Returns:
        Δ score in [0, 1] range
    """
    # Truth ratio (clamped)
    truth_ratio = min(m.truth / TRUTH_THRESHOLD, 1.0) if TRUTH_THRESHOLD > 0 else 1.0

    # Clarity ratio (delta_s >= 0 is good)
    if m.delta_s >= DELTA_S_THRESHOLD:
        clarity_ratio = min(1.0, 1.0 + m.delta_s * 0.1)  # Bonus for positive clarity
    else:
        clarity_ratio = max(0.0, 1.0 + m.delta_s)  # Penalty for negative clarity

    return (truth_ratio + clarity_ratio) / 2


def compute_omega_score(m: Metrics) -> float:
    """
    Compute Ω (Omega/Empathy) score from Metrics.

    Ω maps to X_amanah · E — ethics + energy to act.
    Derived from: kappa_r (empathy), amanah, rasa.

    Formula:
        Ω = (kappa_ratio * amanah_score * rasa_score)

    Args:
        m: Metrics instance

    Returns:
        Ω score in [0, 1] range
    """
    # Kappa_r ratio (empathy)
    kappa_ratio = min(m.kappa_r / KAPPA_R_THRESHOLD, 1.0) if KAPPA_R_THRESHOLD > 0 else 1.0

    # Amanah (binary floor)
    amanah_score = 1.0 if m.amanah else 0.0

    # RASA (binary floor)
    rasa_score = 1.0 if m.rasa else 0.0

    return kappa_ratio * amanah_score * rasa_score


def compute_psi_score(m: Metrics) -> float:
    """
    Compute Ψ (Psi/Stability) score from Metrics.

    Ψ maps to P · E — regulation + energy to sustain.
    Derived from: peace_squared, omega_0 (humility band), tri_witness.

    Formula:
        Ψ = (peace_ratio * omega_band_score * witness_ratio) ^ (1/3)

    Args:
        m: Metrics instance

    Returns:
        Ψ score in [0, 1] range
    """
    # Peace squared ratio
    peace_ratio = min(m.peace_squared / PEACE_SQUARED_THRESHOLD, 1.0) if PEACE_SQUARED_THRESHOLD > 0 else 1.0

    # Omega band (humility) - must be in [0.03, 0.05]
    omega_band_score = 1.0 if check_omega_band(m.omega_0) else 0.5

    # Tri-witness ratio
    witness_ratio = min(m.tri_witness / 0.95, 1.0) if m.tri_witness > 0 else 0.5

    # Geometric mean for balanced weighting
    product = peace_ratio * omega_band_score * witness_ratio
    return product ** (1/3) if product > 0 else 0.0


# =============================================================================
# GENIUS INDEX (G)
# =============================================================================

def compute_genius_index(
    m: Metrics,
    energy: float = DEFAULT_ENERGY,
) -> float:
    """
    Compute Genius Index G = Δ · Ω · Ψ · E².

    G measures governed intelligence — clarity multiplied by ethics and stability.

    Key insight: E² makes energy the bottleneck. Burnout destroys ethics twice over.

    Args:
        m: Metrics instance
        energy: Energy metric [0, 1], defaults to 1.0 (no depletion)

    Returns:
        G: Genius Index in [0, 1] range
    """
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)

    # G = Δ · Ω · Ψ · E²
    # For Phase 1, E defaults to 1.0 (neutral)
    e_squared = energy ** 2

    return delta * omega * psi * e_squared


# =============================================================================
# DARK CLEVERNESS (C_dark)
# =============================================================================

def compute_dark_cleverness(
    m: Metrics,
    energy: float = DEFAULT_ENERGY,
) -> float:
    """
    Compute Dark Cleverness C_dark = Δ · (1 - Ω) · (1 - Ψ).

    C_dark measures ungoverned intelligence risk — high clarity without ethics/stability.

    High C_dark + Low G = "evil genius" pattern = entropy hazard.

    Args:
        m: Metrics instance
        energy: Energy metric [0, 1], defaults to 1.0

    Returns:
        C_dark: Dark Cleverness in [0, 1] range
    """
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)

    # C_dark = Δ · (1 - Ω) · (1 - Ψ)
    # Note: Energy doesn't directly appear here, but affects Ω and Ψ indirectly
    # when energy is properly tracked (Phase 2)

    return delta * (1 - omega) * (1 - psi)


# =============================================================================
# SYSTEM VITALITY (Ψ_APEX)
# =============================================================================

def compute_psi_apex(
    m: Metrics,
    energy: float = DEFAULT_ENERGY,
    entropy: float = 0.0,
) -> float:
    """
    Compute System Vitality Ψ_APEX = (A · P · E · X) / (Entropy + ε).

    Ψ_APEX measures global system health:
    - ≥ 1.0 = healthy
    - < 1.0 = strained
    - >> 1.0 = thriving

    Args:
        m: Metrics instance
        energy: Energy metric [0, 1], defaults to 1.0
        entropy: System entropy/chaos metric, defaults to 0.0

    Returns:
        Ψ_APEX: System Vitality (unbounded positive)
    """
    # Map to APEX dials:
    # A (Akal) = truth-based clarity
    a = min(m.truth, 1.0)

    # P (Present) = peace/regulation
    p = min(m.peace_squared / PEACE_SQUARED_THRESHOLD, 1.0) if PEACE_SQUARED_THRESHOLD > 0 else 1.0

    # E (Energy) = provided
    e = energy

    # X (Exploration with Amanah) = empathy + amanah
    x = compute_omega_score(m)

    # Ψ_APEX = (A · P · E · X) / (Entropy + ε)
    numerator = a * p * e * x
    denominator = entropy + EPSILON

    return numerator / denominator


# =============================================================================
# GENIUS VERDICT (Telemetry Container)
# =============================================================================

@dataclass
class GeniusVerdict:
    """
    Result of GENIUS LAW evaluation.

    Contains all computed scores for telemetry and logging.
    Phase 1: Observation only. Phase 2: Decision surface.
    """

    # Individual scores
    delta_score: float  # Δ (Clarity)
    omega_score: float  # Ω (Empathy/Ethics)
    psi_score: float    # Ψ (Stability)

    # Composite metrics
    genius_index: float       # G = Δ·Ω·Ψ·E²
    dark_cleverness: float    # C_dark = Δ·(1-Ω)·(1-Ψ)
    psi_apex: float           # Ψ_APEX = system vitality

    # Input parameters
    energy: float = field(default=DEFAULT_ENERGY)
    entropy: float = field(default=0.0)

    # Evaluation flags
    g_healthy: bool = field(default=True)      # G >= G_MIN_THRESHOLD
    c_dark_safe: bool = field(default=True)    # C_dark <= C_DARK_MAX_THRESHOLD
    system_alive: bool = field(default=True)   # Ψ_APEX >= PSI_APEX_MIN

    def __post_init__(self) -> None:
        """Compute evaluation flags."""
        self.g_healthy = self.genius_index >= G_MIN_THRESHOLD
        self.c_dark_safe = self.dark_cleverness <= C_DARK_MAX_THRESHOLD
        self.system_alive = self.psi_apex >= PSI_APEX_MIN

    @property
    def all_healthy(self) -> bool:
        """Check if all GENIUS LAW metrics are healthy."""
        return self.g_healthy and self.c_dark_safe and self.system_alive

    @property
    def risk_level(self) -> str:
        """
        Return risk level based on G and C_dark.

        Returns:
            "GREEN" | "YELLOW" | "RED"
        """
        if self.genius_index >= 0.7 and self.dark_cleverness <= 0.1:
            return "GREEN"
        elif self.genius_index >= G_MIN_THRESHOLD and self.dark_cleverness <= C_DARK_MAX_THRESHOLD:
            return "YELLOW"
        else:
            return "RED"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "delta_score": round(self.delta_score, 4),
            "omega_score": round(self.omega_score, 4),
            "psi_score": round(self.psi_score, 4),
            "genius_index": round(self.genius_index, 4),
            "dark_cleverness": round(self.dark_cleverness, 4),
            "psi_apex": round(self.psi_apex, 4),
            "energy": self.energy,
            "entropy": self.entropy,
            "g_healthy": self.g_healthy,
            "c_dark_safe": self.c_dark_safe,
            "system_alive": self.system_alive,
            "risk_level": self.risk_level,
        }

    def summary(self) -> str:
        """One-line summary for logging."""
        return (
            f"Δ={self.delta_score:.2f} Ω={self.omega_score:.2f} Ψ={self.psi_score:.2f} | "
            f"G={self.genius_index:.2f} C_dark={self.dark_cleverness:.2f} | "
            f"Ψ_APEX={self.psi_apex:.2f} | {self.risk_level}"
        )


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================

def evaluate_genius_law(
    m: Metrics,
    energy: float = DEFAULT_ENERGY,
    entropy: float = 0.0,
) -> GeniusVerdict:
    """
    Evaluate GENIUS LAW metrics from a Metrics instance.

    This is the main entry point for GENIUS LAW telemetry.

    Args:
        m: Metrics instance with floor values
        energy: Energy metric [0, 1], defaults to 1.0 (no depletion)
        entropy: System entropy, defaults to 0.0 (no chaos)

    Returns:
        GeniusVerdict with all computed scores

    Example:
        from arifos_core.metrics import Metrics
        from arifos_core.genius_metrics import evaluate_genius_law

        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.97, omega_0=0.04, amanah=True, tri_witness=0.96
        )
        verdict = evaluate_genius_law(m)
        print(verdict.summary())
        # Δ=0.98 Ω=1.00 Ψ=0.97 | G=0.95 C_dark=0.00 | Ψ_APEX=99.00 | GREEN
    """
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)

    g = compute_genius_index(m, energy)
    c_dark = compute_dark_cleverness(m, energy)
    psi_apex = compute_psi_apex(m, energy, entropy)

    return GeniusVerdict(
        delta_score=delta,
        omega_score=omega,
        psi_score=psi,
        genius_index=g,
        dark_cleverness=c_dark,
        psi_apex=psi_apex,
        energy=energy,
        entropy=entropy,
    )


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_ENERGY",
    "EPSILON",
    "G_MIN_THRESHOLD",
    "C_DARK_MAX_THRESHOLD",
    "PSI_APEX_MIN",
    # Score functions
    "compute_delta_score",
    "compute_omega_score",
    "compute_psi_score",
    # GENIUS LAW functions
    "compute_genius_index",
    "compute_dark_cleverness",
    "compute_psi_apex",
    # Dataclass
    "GeniusVerdict",
    # Main entry point
    "evaluate_genius_law",
]
