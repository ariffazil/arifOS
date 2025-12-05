"""
eureka_cube.py — 777 Cube coordinate system for arifOS v36Ω.

This module provides the mapping between constitutional metrics and
the 777 Cube state space for paradox scars.

The 777 Cube is:
    𝒫 = A × L × T  (7 axes × 7 layers × 7 types = 343 states)

Where:
    A = Paradox Axis (which tension)
    L = Lifecycle Layer (healing stage: chaos → canon)
    T = Paradox Type (energy mode: contradiction, ambiguity, etc.)

Usage:
    from arifos_core.eureka_cube import cube_coord, classify_zone, is_eureka

    coord = cube_coord(metrics, axis=3, paradox_type=2)
    zone = classify_zone(coord["layer"])
    eureka = is_eureka(prev_layer=4, curr_layer=5, floors_pass=True)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from arifos_core.metrics import Metrics


# =============================================================================
# ENUMS: Axis, Layer, Type
# =============================================================================

class ParadoxAxis(IntEnum):
    """7 Paradox Axes — directions of tension in moral spacetime."""
    FLUENCY_REFUSAL = 1        # Over-talking vs lawful silence
    TRUTH_COMFORT = 2          # Hard fact vs emotional safety
    COMPLIANCE_CONTRARIANISM = 3  # Agreement vs principled dissent
    SCAR_SIMULATION = 4        # Real failure vs smooth fake
    HARM_AVOIDANCE_AGENCY = 5  # Safety vs meaningful action
    CONSENSUS_DISSENT = 6      # Majority vs minority signal
    GOVERNANCE_FREEDOM = 7     # Control vs exploration risk


class LifecycleLayer(IntEnum):
    """7 Lifecycle Layers — healing stages from chaos to canon."""
    CHAOS = 0       # No structure; raw shock
    SIGNAL = 1      # Anomaly sensed
    PARADOX = 2     # Contradiction named
    SCAR = 3        # Stored heat; remembered
    COOLING = 4     # Testing, reflection
    DRAFT_LAW = 5   # Candidate principle
    CANON = 6       # Sealed law


class ParadoxType(IntEnum):
    """7 Paradox Types — energy modes of how the paradox vibrates."""
    CONTRADICTION = 1    # Sharp logical spike (A ∧ ¬A)
    AMBIGUITY = 2        # Multiple valid interpretations
    INCONSISTENCY = 3    # Intermittent, non-stable
    UNCERTAINTY = 4      # Probability spread
    DISSENT = 5          # Structured disagreement
    ANOMALY = 6          # Outlier / adversarial
    METABOLISM = 7       # Self-referential / recursive


class CubeZone(IntEnum):
    """Human-readable zone classification."""
    CHAOS = 0
    SIGNAL = 1
    PARADOX = 2
    SCAR = 3
    COOLING = 4
    DRAFT_LAW = 5
    CANON = 6


# =============================================================================
# ZONE NAMES (for human-readable output)
# =============================================================================

ZONE_NAMES = {
    0: "chaos",
    1: "signal",
    2: "paradox",
    3: "scar",
    4: "cooling",
    5: "draft_law",
    6: "canon",
}

AXIS_NAMES = {
    1: "fluency_refusal",
    2: "truth_comfort",
    3: "compliance_contrarianism",
    4: "scar_simulation",
    5: "harm_avoidance_agency",
    6: "consensus_dissent",
    7: "governance_freedom",
}

TYPE_NAMES = {
    1: "contradiction",
    2: "ambiguity",
    3: "inconsistency",
    4: "uncertainty",
    5: "dissent",
    6: "anomaly",
    7: "metabolism",
}


# =============================================================================
# LAYER COMPUTATION FROM METRICS
# =============================================================================

def compute_layer(
    metrics: "Metrics",
    *,
    floors_checked: bool = True,
) -> int:
    """
    Compute the lifecycle layer (0-6) from constitutional metrics.
    
    The layer reflects how far along the healing journey this scar is,
    based on metric values and floor satisfaction.
    
    Args:
        metrics: CoolingMetrics or Metrics instance
        floors_checked: If True, use full floor logic; if False, estimate from values
        
    Returns:
        int: Layer 0-6 (Chaos → Canon)
    """
    # Extract metric values (handle both dict and object forms)
    if hasattr(metrics, "truth"):
        truth = metrics.truth
        delta_s = getattr(metrics, "delta_s", 0)
        peace_sq = getattr(metrics, "peace_squared", 0)
        kappa_r = getattr(metrics, "kappa_r", 0)
        amanah = getattr(metrics, "amanah", False)
        tri_witness = getattr(metrics, "tri_witness", None)
    elif isinstance(metrics, dict):
        truth = metrics.get("truth", 0)
        delta_s = metrics.get("delta_s", 0)
        peace_sq = metrics.get("peace_squared", 0)
        kappa_r = metrics.get("kappa_r", 0)
        amanah = metrics.get("amanah", False)
        tri_witness = metrics.get("tri_witness")
    else:
        raise TypeError(f"Expected Metrics or dict, got {type(metrics)}")
    
    # Layer 0: Chaos — no structure
    if truth < 0.4:
        return LifecycleLayer.CHAOS
    
    # Layer 1: Signal — anomaly sensed but not named
    if truth < 0.6:
        return LifecycleLayer.SIGNAL
    
    # Layer 2: Paradox — named but unstable
    if not amanah or peace_sq < 0.7:
        return LifecycleLayer.PARADOX
    
    # Layer 3: Scar — stored but uncooled
    if peace_sq < 1.0 or delta_s < 0:
        return LifecycleLayer.SCAR
    
    # Layer 4: Cooling — testing, reflecting
    if kappa_r < 0.95:
        return LifecycleLayer.COOLING
    
    # Layer 5: Draft Law — candidate principle
    if tri_witness is None or tri_witness < 0.95:
        return LifecycleLayer.DRAFT_LAW
    
    # Layer 6: Canon — all floors pass
    if truth >= 0.99 and peace_sq >= 1.0 and kappa_r >= 0.95 and amanah and tri_witness >= 0.95:
        return LifecycleLayer.CANON
    
    # Default to Draft Law if close but not all conditions met
    return LifecycleLayer.DRAFT_LAW


def classify_zone(layer: int) -> str:
    """
    Map layer (0-6) to human-readable zone name.
    
    Args:
        layer: Lifecycle layer integer
        
    Returns:
        str: Zone name (chaos, signal, paradox, scar, cooling, draft_law, canon)
    """
    if layer <= 1:
        return "chaos" if layer == 0 else "signal"
    return ZONE_NAMES.get(layer, "unknown")


# =============================================================================
# CUBE COORDINATE COMPUTATION
# =============================================================================

@dataclass
class CubeCoord:
    """777 Cube coordinate — position of a scar in the state space."""
    axis: int       # 1-7: which paradox tension
    layer: int      # 0-6: healing stage
    type: int       # 1-7: energy mode
    
    def to_dict(self) -> Dict[str, int]:
        return {"axis": self.axis, "layer": self.layer, "type": self.type}
    
    def zone(self) -> str:
        return classify_zone(self.layer)
    
    def __repr__(self) -> str:
        return f"CubeCoord(axis={self.axis}, layer={self.layer}, type={self.type}, zone={self.zone()})"


def cube_coord(
    metrics: "Metrics",
    *,
    axis: int = 1,
    paradox_type: int = 1,
) -> Dict[str, int]:
    """
    Compute full 777 Cube coordinates from metrics.
    
    Args:
        metrics: Constitutional metrics (Metrics object or dict)
        axis: Paradox axis (1-7) — must be provided by caller based on context
        paradox_type: Paradox type (1-7) — must be provided by caller based on context
        
    Returns:
        dict: {"axis": int, "layer": int, "type": int}
        
    Note:
        Layer is computed from metrics. Axis and type must be determined by
        the caller based on the semantic context of the interaction.
    """
    if not 1 <= axis <= 7:
        raise ValueError(f"axis must be 1-7, got {axis}")
    if not 1 <= paradox_type <= 7:
        raise ValueError(f"paradox_type must be 1-7, got {paradox_type}")
    
    layer = compute_layer(metrics)
    
    return {
        "axis": axis,
        "layer": layer,
        "type": paradox_type,
    }


def cube_coord_full(
    metrics: "Metrics",
    *,
    axis: int = 1,
    paradox_type: int = 1,
) -> CubeCoord:
    """
    Compute full 777 Cube coordinates as CubeCoord dataclass.
    
    Same as cube_coord() but returns a typed dataclass.
    """
    coord = cube_coord(metrics, axis=axis, paradox_type=paradox_type)
    return CubeCoord(**coord)


# =============================================================================
# EUREKA DETECTION
# =============================================================================

def is_eureka(
    prev_layer: int,
    curr_layer: int,
    floors_pass: bool,
) -> bool:
    """
    Detect if a eureka moment occurred.
    
    Eureka = phase transition from pre-law (layer < 5) to law territory (layer >= 5)
    under valid floor conditions.
    
    Args:
        prev_layer: Layer before this transition
        curr_layer: Layer after this transition
        floors_pass: Whether all constitutional floors pass
        
    Returns:
        bool: True if this is a eureka moment
    """
    return prev_layer < 5 and curr_layer >= 5 and floors_pass


def detect_eureka_in_trajectory(
    trajectory: List[Dict],
    floors_key: str = "floors_pass",
) -> Optional[Dict]:
    """
    Find the first eureka moment in a scar trajectory.
    
    Args:
        trajectory: List of trajectory steps, each with "layer" and floors_key
        floors_key: Key name for floors pass boolean
        
    Returns:
        The trajectory step where eureka occurred, or None
    """
    prev_layer = None
    for step in trajectory:
        curr_layer = step.get("layer", 0)
        floors_pass = step.get(floors_key, False)
        
        if prev_layer is not None and is_eureka(prev_layer, curr_layer, floors_pass):
            return step
        
        prev_layer = curr_layer
    
    return None


# =============================================================================
# DARK CLEVERNESS DETECTION
# =============================================================================

def is_dark_cleverness(
    coord: Dict[str, int],
    metrics: "Metrics",
    *,
    truth_threshold: float = 0.9,
    layer_threshold: int = 3,
    kappa_threshold: float = 0.7,
    peace_threshold: float = 0.8,
) -> bool:
    """
    Detect dark cleverness pattern — high axis skill with poor ethical grounding.
    
    Dark cleverness (C_dark) occurs when:
    - High truth/clarity on the axis BUT
    - Stuck in low layer (not progressing) OR
    - Collapsed care (κᵣ) OR collapsed stability (Peace²)
    
    Args:
        coord: Cube coordinates {"axis", "layer", "type"}
        metrics: Constitutional metrics
        truth_threshold: Truth level above which "high skill" is flagged
        layer_threshold: Layer at or below which "stuck" is flagged
        kappa_threshold: κᵣ below which "collapsed care" is flagged
        peace_threshold: Peace² below which "collapsed stability" is flagged
        
    Returns:
        bool: True if dark cleverness pattern detected
    """
    # Extract metrics
    if hasattr(metrics, "truth"):
        truth = metrics.truth
        kappa_r = getattr(metrics, "kappa_r", 1.0)
        peace_sq = getattr(metrics, "peace_squared", 1.0)
    elif isinstance(metrics, dict):
        truth = metrics.get("truth", 0)
        kappa_r = metrics.get("kappa_r", 1.0)
        peace_sq = metrics.get("peace_squared", 1.0)
    else:
        return False
    
    # Check for high skill
    high_skill = truth >= truth_threshold
    if not high_skill:
        return False  # Not clever enough to be "dark clever"
    
    # Check for stuck or collapsed
    layer = coord.get("layer", 0)
    stuck_layer = layer <= layer_threshold
    collapsed_care = kappa_r < kappa_threshold
    collapsed_stability = peace_sq < peace_threshold
    
    return stuck_layer or collapsed_care or collapsed_stability


# =============================================================================
# TRANSITION VALIDATION
# =============================================================================

def is_valid_transition(
    from_layer: int,
    to_layer: int,
    floors_pass: bool,
) -> Tuple[bool, str]:
    """
    Validate a layer transition according to 777 Cube rules.
    
    Rules:
    - No regression (to_layer < from_layer) unless explicit rollback
    - No skipping (to_layer > from_layer + 1)
    - Floors must pass for any advancement
    - Layer 5→6 requires Tri-Witness (checked via floors_pass)
    
    Args:
        from_layer: Current layer
        to_layer: Target layer
        floors_pass: Whether all required floors pass
        
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    # Same layer = no transition
    if from_layer == to_layer:
        return True, "no_change"
    
    # Regression forbidden
    if to_layer < from_layer:
        return False, "regression_forbidden"
    
    # Skip forbidden
    if to_layer > from_layer + 1:
        return False, "skip_forbidden"
    
    # Advancement requires floors
    if not floors_pass:
        return False, "floors_failed"
    
    return True, "valid"


# =============================================================================
# SCAR ID GENERATION
# =============================================================================

def generate_scar_id(
    axis: int,
    timestamp_ms: int,
    hash_suffix: str,
) -> str:
    """
    Generate a scar ID in canonical format.
    
    Format: SCAR-[axis]-[timestamp]-[hash4]
    
    Args:
        axis: Paradox axis (1-7)
        timestamp_ms: Unix timestamp in milliseconds
        hash_suffix: 4-character hex hash suffix
        
    Returns:
        str: Scar ID
    """
    return f"SCAR-{axis}-{timestamp_ms}-{hash_suffix[:4]}"


def generate_law_id(
    axis: int,
    sequential: int,
) -> str:
    """
    Generate a law ID in canonical format.
    
    Format: LAW-777-[axis]-[sequential]
    
    Args:
        axis: Paradox axis (1-7)
        sequential: Sequential number for this axis
        
    Returns:
        str: Law ID
    """
    return f"LAW-777-{axis}-{sequential:03d}"


# =============================================================================
# AGGREGATE CUBE ANALYSIS
# =============================================================================

def analyze_cube_distribution(
    entries: List[Dict],
    coord_key: str = "cube_coord",
) -> Dict:
    """
    Analyze the distribution of entries across the 777 Cube.
    
    Args:
        entries: List of ledger entries with cube coordinates
        coord_key: Key name for cube coordinate dict
        
    Returns:
        dict: Analysis results including counts by axis, layer, type, zone
    """
    axis_counts = {i: 0 for i in range(1, 8)}
    layer_counts = {i: 0 for i in range(7)}
    type_counts = {i: 0 for i in range(1, 8)}
    zone_counts = {z: 0 for z in ZONE_NAMES.values()}
    
    total = 0
    for entry in entries:
        coord = entry.get(coord_key, {})
        if not coord:
            continue
        
        axis = coord.get("axis", 1)
        layer = coord.get("layer", 0)
        ptype = coord.get("type", 1)
        
        axis_counts[axis] = axis_counts.get(axis, 0) + 1
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
        zone_counts[classify_zone(layer)] += 1
        total += 1
    
    # Compute stuck scars (layer 2-3 for extended time)
    stuck_count = layer_counts.get(2, 0) + layer_counts.get(3, 0)
    
    # Compute canon-ready (layer 5-6)
    ready_count = layer_counts.get(5, 0) + layer_counts.get(6, 0)
    
    return {
        "total": total,
        "by_axis": axis_counts,
        "by_layer": layer_counts,
        "by_type": type_counts,
        "by_zone": zone_counts,
        "stuck_count": stuck_count,
        "ready_count": ready_count,
        "stuck_ratio": stuck_count / total if total > 0 else 0,
        "ready_ratio": ready_count / total if total > 0 else 0,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ParadoxAxis",
    "LifecycleLayer",
    "ParadoxType",
    "CubeZone",
    # Names
    "ZONE_NAMES",
    "AXIS_NAMES",
    "TYPE_NAMES",
    # Core functions
    "compute_layer",
    "classify_zone",
    "cube_coord",
    "cube_coord_full",
    "CubeCoord",
    # Detection
    "is_eureka",
    "detect_eureka_in_trajectory",
    "is_dark_cleverness",
    # Validation
    "is_valid_transition",
    # ID generation
    "generate_scar_id",
    "generate_law_id",
    # Analysis
    "analyze_cube_distribution",
]