"""
core/enforcement/genius.py — Constitutional Genius & Dial Derivation

This module implements the "Real Scoring" system for arifOS.
It derives the 4 APEX Dials (A/P/X/E) from the 13 Constitutional Laws.

PRIMARY PATH (N ≥ 5 observations):
  13 floor vectors → covariance matrix → eigenvalue decomposition → top 4 PCs → A,P,X,E
  The dials EMERGE from floor correlation structure, not from assigned clusters.

FALLBACK PATH (N < 5 observations):
  Geometric mean of canonical floor clusters (theory-derived prior).

G = A × P × X × E²

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from core.shared.law_audit import AuditResult
from core.shared.types import FloorScores

logger = logging.getLogger(__name__)

_FLOOR_ALIAS_MAP: dict[str, tuple[str, ...]] = {
    "f1_amanah": ("f1",),
    "f2_truth": ("f2", "truth_score", "akal"),
    "f3_tri_witness": ("f3",),
    "f4_clarity": ("f4", "clarity_score"),
    "f5_peace": ("f5", "peace2"),
    "f6_empathy": ("f6", "empathy_score", "kappa_r"),
    "f7_humility": ("f7", "omega_0", "omega0"),
    "f8_genius": ("f8", "g_prev", "G_prev", "genius_score"),
    "f9_anti_hantu": ("f9", "c_dark"),
    "f10_ontology": ("f10", "ontology_valid"),
    "f11_command_auth": ("f11", "command_auth"),
    "f12_injection": ("f12", "injection_risk"),
    "f13_sovereign": ("f13", "human_score", "sovereign_score"),
}
_BOOL_FLOORS = {"f10_ontology", "f11_command_auth"}
_FLOOR_DEFAULTS: dict[str, Any] = {
    "f1_amanah": 1.0,
    "f2_truth": 0.99,
    "f3_tri_witness": 0.95,
    "f4_clarity": 1.0,
    "f5_peace": 1.0,
    "f6_empathy": 0.95,
    "f7_humility": 0.04,
    "f8_genius": 0.80,
    "f9_anti_hantu": 0.0,
    "f10_ontology": True,
    "f11_command_auth": True,
    "f12_injection": 0.0,
    "f13_sovereign": 1.0,
}

# ── Floor vector field order (canonical 13) ──────────────────────────
_FLOOR_VECTOR_FIELDS: tuple[str, ...] = (
    "f1_amanah",
    "f2_truth",
    "f3_tri_witness",
    "f4_clarity",
    "f5_peace",
    "f6_empathy",
    "f7_humility",
    "f8_genius",
    "f9_anti_hantu",
    "f10_ontology",
    "f11_command_auth",
    "f12_injection",
    "f13_sovereign",
)

# Minimum observations before PCA dials are considered grounded
_MIN_PCA_OBSERVATIONS = 5
# Ring buffer capacity for verdict history
_MAX_HISTORY_SIZE = 50
# Variance floor to prevent degenerate eigenvalues
_VARIANCE_FLOOR = 1e-8


# ═══════════════════════════════════════════════════════════════════════
# Floor Score History — accumulates verdict floor vectors
# ═══════════════════════════════════════════════════════════════════════


class FloorScoreHistory:
    """
    Thread-safe ring buffer accumulating 13-floor vectors from verdicts.

    Used by the PCA dial derivation to build a live covariance matrix.
    When enough observations exist (N ≥ 5), the dials emerge from the
    actual correlation structure of floor scores rather than from
    theory-assigned clusters.
    """

    def __init__(self, max_size: int = _MAX_HISTORY_SIZE) -> None:
        self._buffer: deque[np.ndarray] = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def record(self, floors: FloorScores) -> None:
        """Append a 13-element floor vector from a FloorScores object."""
        vec = _floors_to_vector(floors)
        with self._lock:
            self._buffer.append(vec)

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._buffer)

    @property
    def sufficient(self) -> bool:
        return self.count >= _MIN_PCA_OBSERVATIONS

    def snapshot(self) -> np.ndarray | None:
        """
        Return a (N, 13) observation matrix, or None if insufficient data.
        """
        with self._lock:
            if len(self._buffer) < _MIN_PCA_OBSERVATIONS:
                return None
            return np.stack(list(self._buffer), axis=0)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()


# Module-level singleton history
_floor_history = FloorScoreHistory()


def get_floor_history() -> FloorScoreHistory:
    """Return the module-level floor score history singleton."""
    return _floor_history


# ═══════════════════════════════════════════════════════════════════════
# Helper: floor vector extraction
# ═══════════════════════════════════════════════════════════════════════


def _floors_to_vector(floors: FloorScores) -> np.ndarray:
    """
    Extract the 13 canonical floor scores as a numpy float64 vector.

    Boolean floors (L10, L11) are coerced: True → 1.0, False → 0.0.
    F7 (humility) is kept as-is — the narrow [0.03, 0.05] band is the
    constitutional signal, not noise to be normalized away.
    """
    values: list[float] = []
    for field in _FLOOR_VECTOR_FIELDS:
        raw = getattr(floors, field)
        if isinstance(raw, bool):
            values.append(1.0 if raw else 0.0)
        else:
            values.append(float(raw))
    return np.array(values, dtype=np.float64)


def _vector_to_dict(vec: np.ndarray) -> dict[str, float]:
    """Convert a 13-element vector back to a named dict (for logging)."""
    return {_FLOOR_VECTOR_FIELDS[i]: float(vec[i]) for i in range(13)}


# ═══════════════════════════════════════════════════════════════════════
# PCA Dial Derivation — the real eigendecomposition
# ═══════════════════════════════════════════════════════════════════════


def _compute_pca_dials(
    floors: FloorScores,
    history: FloorScoreHistory,
) -> tuple[APEXDials | None, dict[str, Any]]:
    """
    Attempt true PCA-based dial derivation from accumulated floor history.

    Returns:
        (APEXDials, metadata) on success, or (None, metadata) if insufficient data.

    Algorithm:
      1. Build (N, 13) observation matrix from history + current floors
      2. Center to zero mean
      3. Compute 13×13 covariance matrix C = XᵀX / (N-1)
      4. Eigenvalue decomposition: C v = λ v
      5. Sort eigenvectors by decreasing eigenvalue
      6. Take top 4 eigenvectors → (13, 4) loading matrix W
      7. Project current floor vector: dials_raw = floors_vec @ W
      8. Normalize to [0, 1] via min-max scaling per dial

    The 4 principal components ARE the A/P/X/E dials — they emerge from
    the covariance structure of constitutional compliance, not from
    pre-assigned floor clusters.
    """
    metadata: dict[str, Any] = {
        "derivation": "pca_eigendecomposition",
        "observations": history.count,
        "pca_sufficient": False,
        "explained_variance_ratio": [],
        "eigenvalues": [],
    }

    observations = history.snapshot()
    if observations is None:
        metadata["pca_sufficient"] = False
        return None, metadata

    # Append current floor vector to the observation matrix
    current_vec = _floors_to_vector(floors)
    X = np.vstack([observations, current_vec])  # (N+1, 13)
    N = X.shape[0]

    if N < _MIN_PCA_OBSERVATIONS + 1:
        metadata["pca_sufficient"] = False
        return None, metadata

    # Center the data (zero mean per floor)
    X_centered = X - np.mean(X, axis=0)  # (N, 13)

    # Compute covariance matrix
    C = (X_centered.T @ X_centered) / (N - 1)  # (13, 13)

    # Eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eig(C)  # eigenvalues(13,), eigenvectors(13,13)

    # Sort by decreasing eigenvalue (eigenvectors are columns)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]  # reorder columns

    # Take top 4 principal components (use np.real for pyright compat)
    W: np.ndarray = np.real(eigenvectors[:, :4])  # (13, 4) — loading matrix

    # Explained variance
    total_var: float = float(np.sum(np.real(eigenvalues)))
    if total_var > _VARIANCE_FLOOR:
        explained_var = np.real(eigenvalues[:4]) / total_var
    else:
        explained_var = np.array([0.25, 0.25, 0.25, 0.25])

    metadata["explained_variance_ratio"] = explained_var.tolist()
    metadata["eigenvalues"] = eigenvalues[:4].real.tolist()
    metadata["total_variance"] = float(total_var)
    metadata["pca_sufficient"] = True

    # Project current floor vector onto the 4 PCs
    current_centered = current_vec - np.mean(X, axis=0)
    dials_raw = current_centered @ W  # (4,)

    # Normalize each dial to [0, 1]
    # Use historical min/max per dial for normalization
    all_projected = X_centered @ W  # (N, 4)
    dial_mins = np.min(all_projected, axis=0)
    dial_maxs = np.max(all_projected, axis=0)

    dials_normalized = np.zeros(4)
    for i in range(4):
        denom = dial_maxs[i] - dial_mins[i]
        if denom < _VARIANCE_FLOOR:
            dials_normalized[i] = 0.5  # no variance → neutral
        else:
            dials_normalized[i] = np.clip((dials_raw[i] - dial_mins[i]) / denom, 0.0, 1.0)

    dials = APEXDials(
        A=round(float(dials_normalized[0]), 4),
        P=round(float(dials_normalized[1]), 4),
        X=round(float(dials_normalized[2]), 4),
        E=round(float(dials_normalized[3]), 4),
    )

    return dials, metadata


# ═══════════════════════════════════════════════════════════════════════
# Fallback: geometric mean cluster projection
# ═══════════════════════════════════════════════════════════════════════


def _compute_cluster_dials(
    floors: FloorScores,
    compute_budget_used: float = 0.5,
    compute_budget_max: float = 1.0,
    telemetry: dict[str, Any] | None = None,
) -> APEXDials:
    """
    Fallback dial derivation: geometric mean of theory-derived floor clusters.

    Used when insufficient verdict history exists for PCA eigendecomposition.
    This is the constitutional PRIOR — the theory's best guess at which floors
    cluster together — before live data can determine the actual structure.
    """
    f10 = 1.0 if floors.f10_ontology else 0.0
    f11 = 1.0 if floors.f11_command_auth else 0.0

    # F7 humility — narrow band normalization
    f7_norm = (
        1.0
        if 0.03 <= floors.f7_humility <= 0.05
        else (1.0 - min(abs(floors.f7_humility - 0.04) * 10, 1.0))
    )

    # A = AKAL (Mind/Structure): F2, F4, F7, L10
    akal = geometric_mean([floors.f2_truth, floors.f4_clarity, f7_norm, f10])

    # P = PRESENCE (Stability/Trust): F1, F5, L11
    presence_base = geometric_mean([floors.f1_amanah, floors.f5_peace, f11])
    try:
        from core.governance_kernel import get_governance_kernel

        stability_t = get_governance_kernel().temporal_stability
    except Exception:
        stability_t = 1.0
    presence = presence_base * stability_t

    # X = EXPLORATION (Navigation/Heart): F3, F6, F8, F9
    anti_hantu_compliance = 1.0 - floors.f9_anti_hantu
    w3 = floors.tri_witness_consensus
    x_breadth = 1.0
    if telemetry and "exploration" in telemetry:
        hypotheses = telemetry["exploration"].get("hypotheses", [])
        if len(hypotheses) > 0:
            x_breadth = min(1.0, 0.5 + (len(hypotheses) * 0.1))
    exploration = (
        geometric_mean([w3, floors.f6_empathy, floors.f8_genius, anti_hantu_compliance]) * x_breadth
    )

    # E = ENERGY (Vitality/Boundary): L12, L13 + thermodynamic budget
    injection_compliance = 1.0 - floors.f12_injection
    energy_from_floors = geometric_mean([injection_compliance, floors.f13_sovereign])
    energy_ratio = 1.0 - (compute_budget_used / max(compute_budget_max, 1e-6))
    energy_ratio = max(0.0, min(1.0, energy_ratio))
    uncertainty_penalty = 0.0
    if telemetry and "entropy" in telemetry:
        uncertainty_penalty = float(telemetry["entropy"].get("uncertainty_score", 0.0))
    energy_vitality = (energy_from_floors + energy_ratio) / 2.0
    energy = max(0.0, energy_vitality - (uncertainty_penalty * 0.5))

    return APEXDials(A=akal, P=presence, X=exploration, E=energy)


# ═══════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════


class APEXDials(BaseModel):
    """
    The 4 APEX dials derived from floor scores.

    Each dial represents a dimension of constitutional compliance.
    Derivation method is recorded in the metadata returned by
    calculate_genius(), not in the dials themselves — the dials
    are pure values.
    """

    A: float = Field(
        ge=0.0, le=1.0, description="Akal: Mind dimension (PC1 or F2/F4/F7/L10 cluster)"
    )
    P: float = Field(
        ge=0.0, le=1.0, description="Presence: Stability dimension (PC2 or F1/F5/L11 cluster)"
    )
    X: float = Field(
        ge=0.0,
        le=1.0,
        description="Exploration: Navigation dimension (PC3 or F3/F6/F8/F9 cluster)",
    )
    E: float = Field(
        ge=0.0,
        le=1.0,
        description="Energy: Vitality dimension (PC4 or L12/L13 + budget)",
    )

    def to_dict(self) -> dict[str, float]:
        return {"A": self.A, "P": self.P, "X": self.X, "E": self.E}


def audit_result_to_floor_scores(audit_result: Any) -> FloorScores:
    """Convert a FloorAuditor AuditResult or a raw dict to FloorScores."""
    if isinstance(audit_result, AuditResult):
        results = audit_result.law_results
    elif isinstance(audit_result, dict):
        results = audit_result.get("law_results", audit_result)
    else:
        return FloorScores()

    def get_score(fid: str, default: float = 1.0) -> float:
        res = results.get(fid)
        if hasattr(res, "score"):
            return res.score
        if isinstance(res, dict) and "score" in res:
            return res["score"]
        if res == "pass":
            return 1.0
        if res == "fail":
            return 0.0
        return default

    def get_bool(fid: str, default: bool = True) -> bool:
        res = results.get(fid)
        if hasattr(res, "passed"):
            return res.passed
        if isinstance(res, dict) and "passed" in res:
            return res["passed"]
        if res == "pass":
            return True
        if res == "fail":
            return False
        return default

    return FloorScores(
        f1_amanah=get_score("F1"),
        f2_truth=get_score("F2", 0.99),
        f3_tri_witness=get_score("F3", 0.95),
        f4_clarity=get_score("F4", 1.0),
        f5_peace=get_score("F5", 1.0),
        f6_empathy=get_score("F6", 0.95),
        f7_humility=get_score("F7", 0.04),
        f8_genius=get_score("F8", 0.80),
        f9_anti_hantu=1.0 - get_score("F9", 1.0),
        f10_ontology=get_bool("L10"),
        f11_command_auth=get_bool("L11"),
        f12_injection=1.0 - get_score("L12", 1.0),
        f13_sovereign=get_score("L13"),
    )


def _first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first present non-None value from a mapping."""
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _coerce_bool(value: Any, default: bool) -> bool:
    """Parse permissive bool-like values while preserving explicit false signals."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "pass", "approved", "seal"}:
            return True
        if lowered in {"false", "0", "no", "fail", "denied", "void"}:
            return False
    return bool(value)


def _coerce_float(value: Any, default: float) -> float:
    """Parse float-like values with stable defaults."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coerce_floor_scores(
    source: FloorScores | AuditResult | dict[str, Any] | None = None,
    *,
    defaults: dict[str, Any] | None = None,
) -> FloorScores:
    """Canonicalize heterogeneous floor payloads into a single FloorScores object."""
    if isinstance(source, FloorScores):
        return source
    if isinstance(source, AuditResult):
        return audit_result_to_floor_scores(source)
    if isinstance(source, dict) and "law_results" in source:
        return audit_result_to_floor_scores(source)

    payload = source if isinstance(source, dict) else {}
    resolved_defaults = {**_FLOOR_DEFAULTS, **(defaults or {})}
    values: dict[str, Any] = {}

    for field_name, aliases in _FLOOR_ALIAS_MAP.items():
        value = _first_present(payload, (field_name, *aliases))
        default_value = resolved_defaults[field_name]
        if field_name in _BOOL_FLOORS:
            values[field_name] = _coerce_bool(value, bool(default_value))
        else:
            values[field_name] = _coerce_float(value, float(default_value))

    return FloorScores(**values)


def get_thermodynamic_budget_window(
    session_id: str,
    *,
    fallback_used: float = 0.5,
    fallback_max: float = 1.0,
) -> tuple[float, float]:
    """Resolve the real thermodynamic budget window, with explicit fallback."""
    try:
        from core.physics.thermodynamics_hardened import get_thermodynamic_budget

        budget = get_thermodynamic_budget(session_id)
        return float(budget.consumed), float(budget.initial_budget)
    except Exception:
        return float(fallback_used), float(fallback_max)


def geometric_mean(values: list[float]) -> float:
    """
    Compute geometric mean of values.
    Returns 0.0 if any value is <= 0.0 to enforce HARD floor logic.
    """
    if not values:
        return 0.0
    if any(v <= 0 for v in values):
        return 0.0
    try:
        product = 1.0
        for v in values:
            product *= v
        return product ** (1.0 / len(values))
    except Exception as e:
        logger.error(f"Error calculating geometric mean: {e}")
        return 0.0


def floors_to_dials(
    floors: FloorScores,
    compute_budget_used: float = 0.5,
    compute_budget_max: float = 1.0,
    telemetry: dict[str, Any] | None = None,
) -> APEXDials:
    """
    Project 13 Floors + Telemetry onto 4 Dials (A/P/X/E).

    PRIMARY PATH: PCA eigendecomposition when ≥5 verdicts accumulated.
      The dials emerge from the covariance structure of live floor scores.

    FALLBACK PATH: Geometric mean of theory-derived floor clusters.
      Used when insufficient history exists for PCA.

    The caller does not need to know which path was used — the dials
    are values. The derivation method is recorded in the metadata
    returned by calculate_genius().
    """
    history = get_floor_history()

    # Attempt PCA derivation first
    pca_dials, pca_meta = _compute_pca_dials(floors, history)
    if pca_dials is not None:
        logger.debug(
            "APEX dials derived via PCA eigendecomposition "
            "(obs=%d, explained_var=%.2f/%.2f/%.2f/%.2f)",
            pca_meta["observations"],
            *pca_meta["explained_variance_ratio"],
        )
        return pca_dials

    # Fallback: geometric mean cluster projection (constitutional prior)
    logger.debug(
        "APEX dials derived via cluster projection (geometric mean) "
        "— insufficient history for PCA (obs=%d, need ≥%d)",
        history.count,
        _MIN_PCA_OBSERVATIONS,
    )
    return _compute_cluster_dials(floors, compute_budget_used, compute_budget_max, telemetry)


def calculate_genius(
    floors: FloorScores,
    h: float = 0.0,
    compute_budget_used: float = 0.5,
    compute_budget_max: float = 1.0,
    telemetry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    The Unified Genius Equation: G = (A × P × X × E²) × (1 - h)

    Dials are derived from the 13 constitutional floor scores via:
      - PCA eigendecomposition (when N ≥ 5 verdicts accumulated), or
      - Geometric mean cluster projection (fallback).

    Returns a dict with genius_score, dials, verdict, and derivation metadata.
    """
    # Record this floor observation for future PCA
    history = get_floor_history()
    history.record(floors)

    # Derive dials
    dials = floors_to_dials(floors, compute_budget_used, compute_budget_max, telemetry=telemetry)

    akal = dials.A
    presence = dials.P
    exploration = dials.X
    energy = dials.E

    # G = A * P * X * E² (APEX G Theorem)
    g_gen = akal * presence * exploration * (energy**2)
    final_g = g_gen * (1.0 - h)

    # Determine derivation method
    _, pca_meta = _compute_pca_dials(floors, history)
    if pca_meta.get("pca_sufficient"):
        derivation = "pca_eigendecomposition"
        derivation_meta = {
            "method": "pca_eigendecomposition",
            "observations": pca_meta["observations"],
            "explained_variance_ratio": pca_meta["explained_variance_ratio"],
            "eigenvalues": pca_meta["eigenvalues"],
        }
    else:
        derivation = "cluster_projection"
        derivation_meta = {
            "method": "cluster_projection_geometric_mean",
            "observations": history.count,
            "note": "Insufficient history for PCA — using theory-derived floor clusters as prior. "
            f"Need ≥{_MIN_PCA_OBSERVATIONS} verdicts for eigendecomposition.",
        }

    return {
        "genius_score": round(final_g, 4),
        "dials": dials.to_dict(),
        "hysteresis": h,
        "passed": final_g >= 0.80,
        "verdict": ("SEAL" if final_g >= 0.80 else "PARTIAL" if final_g >= 0.60 else "VOID"),
        "derivation": derivation,
        "derivation_meta": derivation_meta,
        "provenance": "constitutional_measurement",
    }


__all__ = [
    "APEXDials",
    "FloorScoreHistory",
    "audit_result_to_floor_scores",
    "calculate_genius",
    "coerce_floor_scores",
    "floors_to_dials",
    "get_floor_history",
    "get_thermodynamic_budget_window",
]
