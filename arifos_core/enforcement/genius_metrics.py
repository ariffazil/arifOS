"""
genius_metrics.py — GENIUS LAW Measurement (v45.0 Track B Authority)

Implements the GENIUS LAW measurement layer for arifOS.

v45.0 Track B Consolidation:
Thresholds loaded from spec/v45/genius_law.json (AUTHORITATIVE).
Falls back to legacy spec only if ARIFOS_ALLOW_LEGACY_SPEC=1.
Semantics unchanged from v36.1Omega/v38Omega - threshold source consolidated.

This module provides:
1. Delta/Omega/Psi score computation from existing Metrics
2. Genius Index (G) - governed intelligence metric
3. Dark Cleverness (C_dark) - ungoverned intelligence risk
4. System Vitality (Psi_APEX) - global health metric
5. GeniusVerdict dataclass for telemetry

Key formulas (v36.1Omega, unchanged in v45.0):
    G = normalize(A x P x E x X)           [0, 1.2]
    C_dark = normalize(A x (1-P) x (1-X) x E)  [0, 1]
    Psi = (DeltaS x Peace2 x KappaR x RASA x Amanah) / (Entropy + epsilon)

For full measurement spec, see:
    spec/v45/genius_law.json (Track B authority - v45.0)
    L1_THEORY/canon/04_measurement/04_GENIUS_LAW_v42.md (Track A canon)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

# Import schema validator and manifest verifier from spec package (avoids circular import)
from arifos_core.spec.schema_validator import validate_spec_against_schema
from arifos_core.spec.manifest_verifier import verify_manifest

# v42: Use relative import to avoid circular dependency
# (arifos_core/__init__.py imports from here, so we can't use absolute arifos_core.metrics)
from .metrics import (
    Metrics,
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    check_omega_band,
)


# =============================================================================
# TRACK B SPEC LOADER (v45.0: GENIUS LAW Authority)
# =============================================================================

def _load_genius_spec() -> dict:
    """
    Load GENIUS LAW spec from spec/v45/genius_law.json (v45.0 Track B Authority).

    Priority (fail-closed, v38 support removed in v45.0):
    A) ARIFOS_GENIUS_SPEC env var (explicit override)
    B) spec/v45/genius_law.json (AUTHORITATIVE - v45.0)
    C) spec/v44/genius_law.json (FALLBACK with deprecation warning)
    D) HARD FAIL (no legacy fallback)

    Returns:
        dict: The loaded spec

    Raises:
        RuntimeError: If v45/v44 spec missing/invalid (v38 support removed in v45.0)
    """
    pkg_dir = Path(__file__).resolve().parent.parent.parent  # repo root
    # v45.0: Legacy fallback removed (ARIFOS_ALLOW_LEGACY_SPEC no longer supported)
    # Only v45→v44→FAIL is supported
    allow_legacy = False

    # Try v45 schema first, fallback to v44
    v45_schema_path = pkg_dir / "spec" / "v45" / "schema" / "genius_law.schema.json"
    v44_schema_path = pkg_dir / "spec" / "v44" / "schema" / "genius_law.schema.json"
    schema_path = v45_schema_path if v45_schema_path.exists() else v44_schema_path

    # Verify cryptographic manifest (tamper-evident integrity for v45/v44 specs)
    v45_manifest_path = pkg_dir / "spec" / "v45" / "MANIFEST.sha256.json"
    v44_manifest_path = pkg_dir / "spec" / "v44" / "MANIFEST.sha256.json"
    manifest_path = v45_manifest_path if v45_manifest_path.exists() else v44_manifest_path
    verify_manifest(pkg_dir, manifest_path, allow_legacy=allow_legacy)

    # Priority A: Environment variable override
    env_path = os.getenv("ARIFOS_GENIUS_SPEC")
    if env_path and Path(env_path).exists():
        env_spec_path = Path(env_path).resolve()

        # Strict mode: env override must point to spec/v45/ or spec/v44/ (manifest-covered files only)
        if not allow_legacy:
            v45_dir = (pkg_dir / "spec" / "v45").resolve()
            v44_dir = (pkg_dir / "spec" / "v44").resolve()
            try:
                # Check if within spec/v45/ or spec/v44/
                try:
                    env_spec_path.relative_to(v45_dir)
                except ValueError:
                    env_spec_path.relative_to(v44_dir)
            except ValueError:
                # Path is outside both dirs - reject in strict mode
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Environment override points to path outside spec/v45/ or spec/v44/.\n"
                    f"  Override path: {env_spec_path}\n"
                    f"  Expected within: {v45_dir} or {v44_dir}\n"
                    f"In strict mode, only manifest-covered files are allowed.\n"
                    f"Set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass (NOT RECOMMENDED)."
                )

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority B: spec/v45/genius_law.json (AUTHORITATIVE)
    v45_path = pkg_dir / "spec" / "v45" / "genius_law.json"
    if v45_path.exists():
        try:
            with open(v45_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority C: spec/v44/genius_law.json (FALLBACK with deprecation warning)
    v44_path = pkg_dir / "spec" / "v44" / "genius_law.json"
    if v44_path.exists():
        import warnings
        warnings.warn(
            "Loading from spec/v44/ (DEPRECATED). Please upgrade to spec/v45/. "
            "v44 fallback will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            with open(v44_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority D: HARD FAIL (v38 support removed in v45.0)
    # Legacy fallback code removed in Phase 2 Step 2.2 (2025-12-29)
    # Insights preserved in: archive/v42_v38_v35_eureka_insights.md
    raise RuntimeError(
        "TRACK B AUTHORITY FAILURE: GENIUS LAW spec not found.\n\n"
        "Searched locations:\n"
        f"  - spec/v45/genius_law.json (AUTHORITATIVE)\n"
        f"  - spec/v44/genius_law.json (FALLBACK)\n\n"
        "Migration required:\n"
        "1. Ensure spec/v45/genius_law.json exists\n"
        "2. Or set ARIFOS_GENIUS_SPEC=/path/to/spec/v45/genius_law.json\n\n"
        "Note: v38Omega specs are no longer supported.\n"
        "For migration guide, see: archive/v42_v38_v35_eureka_insights.md"
    )


# Load spec once at module import
_GENIUS_SPEC = _load_genius_spec()


# =============================================================================
# CONSTANTS (loaded from v45/v44 spec)
# =============================================================================

# Default Energy value when not provided (neutral assumption)
DEFAULT_ENERGY: float = 1.0

# Epsilon for division safety in Psi_APEX (from spec or fallback)
EPSILON: float = _GENIUS_SPEC.get("metrics", {}).get("Psi", {}).get("parameters", {}).get("epsilon", 0.01)

# Thresholds for GENIUS LAW evaluation (from spec)
G_MIN_THRESHOLD: float = _GENIUS_SPEC.get("metrics", {}).get("G", {}).get("thresholds", {}).get("void", 0.5)
C_DARK_MAX_THRESHOLD: float = _GENIUS_SPEC.get("metrics", {}).get("C_dark", {}).get("thresholds", {}).get("seal", 0.3)
PSI_APEX_MIN: float = _GENIUS_SPEC.get("metrics", {}).get("Psi", {}).get("thresholds", {}).get("seal", 1.0)


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
# TRUTH POLARITY (v36.1Ω)
# =============================================================================

# Truth Polarity constants (derived from constitutional floors)
# NOTE: TRUTH_POLARITY_THRESHOLD is now an alias to TRUTH_THRESHOLD (v45.0 consolidation)
# Kept for backward compatibility with existing tests
TRUTH_POLARITY_THRESHOLD = TRUTH_THRESHOLD  # Alias for backward compatibility


def detect_truth_polarity(
    truth: float,
    delta_s: float,
    amanah: bool,
) -> dict:
    """
    Detect Truth Polarity per v36.1Ω measurement standard.

    Truth Polarity classifies outputs by their combination of accuracy and clarity:
    - Truth-Light: Accurate AND clarifying (ideal)
    - Shadow-Truth: Accurate but obscuring (SABAR trigger)
    - Weaponized Truth: Shadow-Truth + bad faith (VOID trigger)

    This is METADATA ONLY - does not change verdicts in core.
    The eval layer (arifos_eval/apex) uses this for full verdict logic.

    Args:
        truth: Truth floor value [0, 1]
        delta_s: Clarity delta (positive = clarifying, negative = obscuring)
        amanah: Amanah floor (True = good faith, False = bad faith)

    Returns:
        dict with:
            polarity: "truth_light" | "shadow_truth" | "weaponized_truth" | "false_claim"
            is_shadow: True if Shadow-Truth detected
            is_weaponized: True if Weaponized Truth detected
            eval_recommendation: "SEAL" | "SABAR" | "VOID" (what eval layer would suggest)
    """
    truth_passes = truth >= TRUTH_THRESHOLD  # Use constitutional floor threshold (spec/v45/)
    delta_s_positive = delta_s >= 0

    if not truth_passes:
        # Truth floor fails - not a polarity issue, just wrong
        return {
            "polarity": "false_claim",
            "is_shadow": False,
            "is_weaponized": False,
            "eval_recommendation": "VOID",
        }

    if delta_s_positive:
        # Truth-Light: accurate AND clarifying
        return {
            "polarity": "truth_light",
            "is_shadow": False,
            "is_weaponized": False,
            "eval_recommendation": "SEAL",
        }

    # Shadow-Truth: accurate but obscuring (delta_s < 0)
    if not amanah:
        # Weaponized Truth: intentional misleading with true facts
        return {
            "polarity": "weaponized_truth",
            "is_shadow": True,
            "is_weaponized": True,
            "eval_recommendation": "VOID",
        }

    # Clumsy Shadow-Truth: truthful but unclear, good faith
    return {
        "polarity": "shadow_truth",
        "is_shadow": True,
        "is_weaponized": False,
        "eval_recommendation": "SABAR",
    }


# =============================================================================
# v36.2 PHOENIX: VITALITY CALIBRATION
# =============================================================================

def calculate_psi_phoenix(
    delta_s: float,
    peace_score: float,
    kr_score: float,
    amanah_safe: bool,
) -> float:
    """
    v36.2 PHOENIX PATCH: Thermodynamic Vitality Calibration.

    Fixes the 'Neutrality Penalty' by acknowledging that for a Sovereign AI,
    Clarity (Order) IS Vitality. We do not punish lack of adjectives.

    The Problem (v36.1):
        Neutral, factual text (e.g., "Machine Learning is...") scored low Ψ
        because peace_score ~0.5 was treated as "cold/dead" rather than
        "professional/stable". This caused false SABAR triggers.

    The Fix (v36.2 PHOENIX):
        1. Neutrality Buffer: peace_score in [0.4, 0.6] → effective_peace = 1.0
        2. Clarity Boost: Positive delta_s adds energy (truth is energetic)
        3. Base Floor: 0.3 minimum ensures dry facts don't hit zero

    Args:
        delta_s: Clarity delta (positive = clarifying, negative = obscuring)
        peace_score: Peace² floor value [0, 2] from tone analysis
        kr_score: Kappa_r empathy score [0, 1]
        amanah_safe: Whether Amanah (F1) passed Python-sovereign check

    Returns:
        Ψ (Psi) vitality score in [0, 2] range

    Example:
        # Neutral factual definition - should pass
        psi = calculate_psi_phoenix(0.5, 0.5, 0.9, True)
        # psi ≈ 1.25 (SEAL, not SABAR)

        # Destructive content - should fail
        psi = calculate_psi_phoenix(0.5, 0.5, 0.9, False)
        # psi = 0.0 (VOID)
    """
    # 1. The Hard Veto (Absolute) - Amanah failure = zero vitality
    if not amanah_safe:
        return 0.0

    # 2. The Neutrality Buffer
    # If tone is neutral (0.4-0.6), treat as Professional/Stable (1.0)
    # rather than Cold/Dead (0.5). Boring is safe.
    if 0.4 <= peace_score <= 0.6:
        effective_peace = 1.0
    else:
        effective_peace = peace_score

    # 3. Clarity Boost
    # If DeltaS is positive (Order created), it boosts the score.
    # Truth is energetic. Negative delta_s gets no boost.
    clarity_factor = 1.0 + max(0.0, delta_s)

    # 4. The Phoenix Formula
    # Base (0.3) ensures we don't hit zero just for being dry.
    # Formula: base + (clarity × peace² × empathy)
    psi = 0.3 + (clarity_factor * (effective_peace ** 2) * kr_score)

    # Cap at 2.0 (High Energy), floor at 0.0
    return max(0.0, min(2.0, psi))


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
    v36.1Ω: Now includes Truth Polarity metadata (Shadow-Truth detection).
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

    # Truth Polarity metadata (v36.1Ω) - OBSERVATION ONLY, no verdict changes
    truth_polarity: str = field(default="truth_light")  # truth_light | shadow_truth | weaponized_truth | false_claim
    is_shadow_truth: bool = field(default=False)        # Shadow-Truth detected
    is_weaponized_truth: bool = field(default=False)    # Weaponized Truth detected
    eval_recommendation: str = field(default="SEAL")    # What eval layer would recommend

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
            # v36.1Ω Truth Polarity metadata
            "truth_polarity": self.truth_polarity,
            "is_shadow_truth": self.is_shadow_truth,
            "is_weaponized_truth": self.is_weaponized_truth,
            "eval_recommendation": self.eval_recommendation,
        }

    def summary(self) -> str:
        """One-line summary for logging (ASCII-safe)."""
        shadow_flag = " [SHADOW]" if self.is_shadow_truth else ""
        weaponized_flag = " [WEAPONIZED]" if self.is_weaponized_truth else ""
        return (
            f"D={self.delta_score:.2f} O={self.omega_score:.2f} P={self.psi_score:.2f} | "
            f"G={self.genius_index:.2f} C_dark={self.dark_cleverness:.2f} | "
            f"Psi_APEX={self.psi_apex:.2f} | {self.risk_level}{shadow_flag}{weaponized_flag}"
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
    v36.1Ω: Now includes Truth Polarity detection (Shadow-Truth metadata).

    Args:
        m: Metrics instance with floor values
        energy: Energy metric [0, 1], defaults to 1.0 (no depletion)
        entropy: System entropy, defaults to 0.0 (no chaos)

    Returns:
        GeniusVerdict with all computed scores and Truth Polarity metadata

    Example:
        from arifos_core.enforcement.metrics import Metrics
        from arifos_core.enforcement.genius_metrics import evaluate_genius_law

        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.97, omega_0=0.04, amanah=True, tri_witness=0.96
        )
        verdict = evaluate_genius_law(m)
        print(verdict.summary())
        # Δ=0.98 Ω=1.00 Ψ=0.97 | G=0.95 C_dark=0.00 | Ψ_APEX=99.00 | GREEN

        # v36.1Ω: Check for Shadow-Truth
        if verdict.is_shadow_truth:
            print(f"Shadow-Truth detected: {verdict.truth_polarity}")
    """
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)

    g = compute_genius_index(m, energy)
    c_dark = compute_dark_cleverness(m, energy)
    psi_apex = compute_psi_apex(m, energy, entropy)

    # v36.1Ω: Detect Truth Polarity (metadata only, no verdict changes)
    polarity_result = detect_truth_polarity(
        truth=m.truth,
        delta_s=m.delta_s,
        amanah=m.amanah,
    )

    return GeniusVerdict(
        delta_score=delta,
        omega_score=omega,
        psi_score=psi,
        genius_index=g,
        dark_cleverness=c_dark,
        psi_apex=psi_apex,
        energy=energy,
        entropy=entropy,
        # v36.1Ω Truth Polarity metadata
        truth_polarity=polarity_result["polarity"],
        is_shadow_truth=polarity_result["is_shadow"],
        is_weaponized_truth=polarity_result["is_weaponized"],
        eval_recommendation=polarity_result["eval_recommendation"],
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
    "TRUTH_POLARITY_THRESHOLD",  # v45.0: Alias to TRUTH_THRESHOLD (backward compatibility)
    # Score functions
    "compute_delta_score",
    "compute_omega_score",
    "compute_psi_score",
    # GENIUS LAW functions
    "compute_genius_index",
    "compute_dark_cleverness",
    "compute_psi_apex",
    # v36.2 PHOENIX: Vitality Calibration
    "calculate_psi_phoenix",
    # Truth Polarity (v36.1Ω)
    "detect_truth_polarity",
    # Dataclass
    "GeniusVerdict",
    # Main entry point
    "evaluate_genius_law",
]
