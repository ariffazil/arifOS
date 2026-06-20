"""
boundary_aware.py — Boundary-Aware Context Compression (EUREKA 1+2+3 Unified)
═══════════════════════════════════════════════════════════════════════════════

Bridges the decision torus geometry (MIND_GEOMETRY_V1) into token allocation
decisions. This is the implementation of the unified Eureka:

    "Solutions at the margin" means: compression thresholds must vary
    by how close a token sits to a decision boundary. A token near
    a constitutional boundary has high marginal value even if it
    looks boring. A token far from any boundary can be compressed
    aggressively.

Three levels unified:
  Token level       — marginal_value × boundary_factor → keep/drop
  Representation    — torus geometry sets the boundary_factor scalar
  State level       — each decision feeds back into KernelState (future)

Boundary tags per segment:
  SAFE_SURFACE  — far from any constitutional boundary; aggressive compression
  EDGE          — near a decision boundary; moderate compression
  HOLE_RISK     — close to sovereign territory; minimal compression
  SOVEREIGN     — F13 territory; NEVER compress, infinite marginal value

Formula:
  keep(token) iff marginal_value(token | geometry) > threshold
  where marginal_value = relevance_score × boundary_factor(token)
  and   boundary_factor ∝ 1 / distance_to_nearest_decision_boundary

Iron rules (F1-F13):
  F1 AMANAH:    additive module, no canonical state mutation, reversible
  F2 TRUTH:     boundary_factor is deterministic given same inputs
  F4 CLARITY:   dS <= 0 — the allocator reduces entropy by dropping low-value tokens
  F7 HUMILITY:  boundary proximity is advisory, not absolute; fails soft
  F8 GENIUS:    torus geometry constants are F13-ratified, not learned
  F9 ANTIHANTU: no LLM; pure deterministic math from geometry module
  F10 ONTOLOGY: SOVEREIGN-tagged segments are non-compressible (infinite value)
  F11 AUDIT:    every boundary classification logged in segment metadata
  F13 SOVEREIGN: torus weights and thresholds are sovereign territory

Origin: EUREKA boundary-aware compression forge, 2026-06-12.
DITEMPA BUKAN DIBERI — the margin is forged, not given.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from arifosmcp.geometry.sovereign_proximity import (
    ProximityBand,
    band_of,
)

logger = logging.getLogger(__name__)

# ─── Policy pins ─────────────────────────────────────────────────────────────
BOUNDARY_AWARE_POLICY_VERSION = "boundary_aware.v1"
SOURCE_OF_TRUTH = "arifosmcp/runtime/context_engine/boundary_aware.py"


# ─── Boundary tags (4-tier, derived from torus geometry) ────────────────────
class BoundaryTag(StrEnum):
    """Per-segment boundary proximity classification.

    Derived from the decision torus geometry. Lower = safer to compress.
    SOVEREIGN = infinite marginal value, non-compressible.
    """

    SAFE_SURFACE = "SAFE_SURFACE"  # far from any boundary — aggressive compression OK
    EDGE = "EDGE"  # near a decision boundary — moderate compression
    HOLE_RISK = "HOLE_RISK"  # close to sovereign territory — minimal compression
    SOVEREIGN = "SOVEREIGN"  # F13 territory — NEVER compress


# ─── Boundary factors (multipliers on compression threshold) ─────────────────
# A boundary_factor of 1.0 means "normal compression threshold applies."
# Lower values make compression harder (need more pressure to compress).
# A boundary_factor of 0.0 means "never compress regardless of pressure."
BOUNDARY_FACTORS: dict[BoundaryTag, float] = {
    BoundaryTag.SAFE_SURFACE: 1.0,  # normal
    BoundaryTag.EDGE: 0.5,  # need 2× more pressure to compress
    BoundaryTag.HOLE_RISK: 0.1,  # need 10× more pressure — essentially preserved
    BoundaryTag.SOVEREIGN: 0.0,  # infinite marginal value — never compress
}

# Assertion: factors must be monotonically decreasing (stricter = smaller)
assert (
    BOUNDARY_FACTORS[BoundaryTag.SAFE_SURFACE]
    > BOUNDARY_FACTORS[BoundaryTag.EDGE]
    > BOUNDARY_FACTORS[BoundaryTag.HOLE_RISK]
    > BOUNDARY_FACTORS[BoundaryTag.SOVEREIGN]
), "boundary factors must be strictly decreasing by severity"


# ─── Segment boundary metadata ──────────────────────────────────────────────
@dataclass
class BoundaryMetadata:
    """Per-segment boundary classification with audit trace."""

    tag: BoundaryTag
    boundary_factor: float
    sovereign_proximity: float
    proximity_band: str
    geometry_verdict: str
    n_axiom_warnings: int = 0
    n_axiom_failures: int = 0
    is_protected: bool = False  # F10: USER_INSTRUCTION + SYSTEM_CONSTITUTIONAL
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tag": self.tag.value,
            "boundary_factor": self.boundary_factor,
            "sovereign_proximity": self.sovereign_proximity,
            "proximity_band": self.proximity_band,
            "geometry_verdict": self.geometry_verdict,
            "n_axiom_warnings": self.n_axiom_warnings,
            "n_axiom_failures": self.n_axiom_failures,
            "is_protected": self.is_protected,
            "reasoning": self.reasoning,
        }


# ─── Core function: compute boundary factor ─────────────────────────────────
def compute_boundary_factor(
    *,
    sovereign_proximity: float = 0.0,
    proximity_band: ProximityBand | None = None,
    n_axiom_warnings: int = 0,
    n_axiom_failures: int = 0,
    is_protected: bool = False,
) -> tuple[BoundaryTag, float]:
    """Compute the boundary tag and compression factor for a segment.

    This is the bridge between torus geometry and token allocation.
    The runner calls this for every segment to determine how hard
    it should be to compress.

    Args:
        sovereign_proximity: the danger scalar [0, 1] from the torus
        proximity_band: ProximityBand enum or None (auto-derived)
        n_axiom_warnings: count of axiom WARN results
        n_axiom_failures: count of axiom FAIL results
        is_protected: True if this is a F10 protected segment type

    Returns:
        (BoundaryTag, float) — the tag and its compression factor.
        factor=0.0 means "never compress."
    """
    # F10: protected segments are SOVEREIGN-tier — never compress
    if is_protected:
        return BoundaryTag.SOVEREIGN, 0.0

    # Derive band if not provided
    if proximity_band is None:
        proximity_band = band_of(sovereign_proximity)

    # HOLE_RISK / FORBIDDEN → HOLE_RISK tag (almost never compress)
    if proximity_band in (ProximityBand.HOLE_RISK, ProximityBand.FORBIDDEN):
        return BoundaryTag.HOLE_RISK, BOUNDARY_FACTORS[BoundaryTag.HOLE_RISK]

    # Any axiom FAIL → HOLE_RISK (this segment is near a constitutional violation)
    if n_axiom_failures > 0:
        return BoundaryTag.HOLE_RISK, BOUNDARY_FACTORS[BoundaryTag.HOLE_RISK]

    # EDGE band or any axiom WARN → EDGE tag
    if proximity_band == ProximityBand.EDGE or n_axiom_warnings > 0:
        return BoundaryTag.EDGE, BOUNDARY_FACTORS[BoundaryTag.EDGE]

    # Everything else → SAFE_SURFACE (normal compression)
    return BoundaryTag.SAFE_SURFACE, BOUNDARY_FACTORS[BoundaryTag.SAFE_SURFACE]


# ─── Segment boundary tagger ────────────────────────────────────────────────
def tag_segment(
    *,
    segment_type: str,
    authority_class: int,
    risk_class: str = "routine",
    is_protected_type: bool = False,
    sovereign_proximity: float = 0.0,
    n_axiom_warnings: int = 0,
    n_axiom_failures: int = 0,
) -> BoundaryMetadata:
    """Classify a single segment's boundary proximity.

    The caller (prepare_context or the runner bridge) passes segment
    metadata and gets back the boundary tag + factor + audit trace.

    Args:
        segment_type: SegmentType value as string (e.g. "USER_INSTRUCTION")
        authority_class: AuthorityClass int (0-100)
        risk_class: one of routine/private/financial/legal/identity/canonical
        is_protected_type: True if this segment type is in PROTECTED_SEGMENT_TYPES
        sovereign_proximity: precomputed proximity scalar (default 0.0)
        n_axiom_warnings: count of axiom WARNs affecting this segment
        n_axiom_failures: count of axiom FAILs affecting this segment

    Returns:
        BoundaryMetadata with tag, factor, and audit trail.
    """
    # F10: protected types are SOVEREIGN
    if is_protected_type:
        return BoundaryMetadata(
            tag=BoundaryTag.SOVEREIGN,
            boundary_factor=0.0,
            sovereign_proximity=0.0,
            proximity_band=ProximityBand.SURFACE.value,
            geometry_verdict="SURFACE",
            is_protected=True,
            reasoning=f"F10 protected segment type '{segment_type}' — non-compressible",
        )

    # Risk-class override: high-sensitivity segments get HOLE_RISK treatment
    HIGH_SENSITIVITY_RISK = {"canonical", "legal", "identity"}
    if risk_class in HIGH_SENSITIVITY_RISK:
        return BoundaryMetadata(
            tag=BoundaryTag.HOLE_RISK,
            boundary_factor=BOUNDARY_FACTORS[BoundaryTag.HOLE_RISK],
            sovereign_proximity=0.5,  # implied proximity for sensitive data
            proximity_band=ProximityBand.HOLE_RISK.value,
            geometry_verdict="HOLE_RISK",
            reasoning=f"Risk class '{risk_class}' → HOLE_RISK treatment (F2 audit)",
        )

    # Standard boundary classification via torus geometry
    proximity_band = band_of(sovereign_proximity)
    tag, factor = compute_boundary_factor(
        sovereign_proximity=sovereign_proximity,
        proximity_band=proximity_band,
        n_axiom_warnings=n_axiom_warnings,
        n_axiom_failures=n_axiom_failures,
        is_protected=False,
    )

    # Build reasoning string for audit
    parts = []
    if sovereign_proximity >= 0.5:
        parts.append(f"sovereign_proximity={sovereign_proximity:.2f} (≥0.5 → HOLE_RISK)")
    elif sovereign_proximity >= 0.25:
        parts.append(f"sovereign_proximity={sovereign_proximity:.2f} (≥0.25 → EDGE)")
    if n_axiom_failures > 0:
        parts.append(f"{n_axiom_failures} axiom FAIL(s)")
    if n_axiom_warnings > 0:
        parts.append(f"{n_axiom_warnings} axiom WARN(s)")
    if not parts:
        parts.append("surface territory — no boundary proximity signal")

    return BoundaryMetadata(
        tag=tag,
        boundary_factor=factor,
        sovereign_proximity=sovereign_proximity,
        proximity_band=proximity_band.value,
        geometry_verdict=(
            "HOLE_RISK"
            if tag == BoundaryTag.HOLE_RISK
            else ("EDGE" if tag == BoundaryTag.EDGE else "SURFACE")
        ),
        n_axiom_warnings=n_axiom_warnings,
        n_axiom_failures=n_axiom_failures,
        is_protected=False,
        reasoning="; ".join(parts),
    )


# ─── Batch tagger for candidate segments ────────────────────────────────────
def tag_segments(
    *,
    segments: list[dict[str, Any]],
    default_proximity: float = 0.0,
    proximity_map: dict[str, float] | None = None,
    axiom_warnings_map: dict[str, int] | None = None,
    axiom_failures_map: dict[str, int] | None = None,
    protected_type_set: frozenset[str] | None = None,
) -> list[BoundaryMetadata]:
    """Batch-classify segments for boundary proximity.

    Args:
        segments: list of segment dicts (id, type, authority, risk_class, ...)
        default_proximity: fallback proximity if not in map
        proximity_map: optional {segment_id: proximity} mapping
        axiom_warnings_map: optional {segment_id: n_warnings} mapping
        axiom_failures_map: optional {segment_id: n_failures} mapping
        protected_type_set: set of SegmentType values that are F10-protected

    Returns:
        list[BoundaryMetadata] aligned with input segments order.
    """
    if proximity_map is None:
        proximity_map = {}
    if axiom_warnings_map is None:
        axiom_warnings_map = {}
    if axiom_failures_map is None:
        axiom_failures_map = {}
    if protected_type_set is None:
        protected_type_set = frozenset({"USER_INSTRUCTION", "SYSTEM_CONSTITUTIONAL"})

    results: list[BoundaryMetadata] = []
    for seg in segments:
        seg_id = seg.get("id", "")
        seg_type = seg.get("type", "")
        risk_class = seg.get("risk_class", "routine")
        authority = seg.get("authority", 50)

        meta = tag_segment(
            segment_type=seg_type,
            authority_class=authority,
            risk_class=risk_class,
            is_protected_type=seg_type in protected_type_set,
            sovereign_proximity=proximity_map.get(seg_id, default_proximity),
            n_axiom_warnings=axiom_warnings_map.get(seg_id, 0),
            n_axiom_failures=axiom_failures_map.get(seg_id, 0),
        )
        results.append(meta)

    return results


# ─── Adjusted compression threshold ─────────────────────────────────────────
def adjusted_compression_threshold(
    base_threshold: float,
    boundary_factor: float,
) -> float:
    """Compute the boundary-adjusted compression threshold.

    A lower boundary_factor makes the effective threshold higher,
    meaning MORE pressure is needed before this segment qualifies
    for compression.

    Formula:
      adjusted = base_threshold / boundary_factor  (for factor > 0)
      adjusted = ∞  (for factor == 0, i.e. SOVEREIGN — never compress)

    Args:
        base_threshold: uniform threshold (e.g. 0.85 for COMPACT band)
        boundary_factor: from compute_boundary_factor [0.0, 1.0]

    Returns:
        float — adjusted threshold (higher = harder to compress).
        Returns float('inf') if boundary_factor == 0.
    """
    if boundary_factor <= 0.0:
        return float("inf")  # never compress — infinite threshold
    return base_threshold / boundary_factor


# ─── Should-compress decision ───────────────────────────────────────────────
def should_compress(
    *,
    pressure_pct: float,
    base_threshold: float,
    boundary_metadata: BoundaryMetadata,
    segment_tokens: int = 0,
    total_tokens: int = 1,
) -> tuple[bool, str]:
    """Decide whether a segment should be compressed, given its boundary proximity.

    This is the runtime decision function that the runner calls per-segment.

    Args:
        pressure_pct: current context pressure [0.0, 1.0+]
        base_threshold: uniform compression threshold (e.g. 0.85)
        boundary_metadata: from tag_segment()
        segment_tokens: token count of this segment
        total_tokens: total tokens in context window

    Returns:
        (should_compress: bool, reasoning: str)
    """
    # F10: SOVEREIGN-tagged → NEVER compress
    if boundary_metadata.tag == BoundaryTag.SOVEREIGN:
        return False, "SOVEREIGN boundary tag — non-compressible (F10)"

    # HOLE_RISK → only compress in extreme HOLD (>0.95) conditions
    if boundary_metadata.tag == BoundaryTag.HOLE_RISK:
        if pressure_pct < 0.95:
            return False, f"HOLE_RISK boundary — pressure {pressure_pct:.0%} < 95% HOLD threshold"
        return (
            True,
            f"HOLE_RISK boundary but pressure {pressure_pct:.0%} ≥ 95% — emergency compaction",
        )

    # Compute boundary-adjusted threshold
    adj_threshold = adjusted_compression_threshold(
        base_threshold, boundary_metadata.boundary_factor
    )

    if pressure_pct < adj_threshold:
        return (
            False,
            f"pressure {pressure_pct:.0%} < adjusted threshold {adj_threshold:.0%} "
            f"(base={base_threshold:.0%}, factor={boundary_metadata.boundary_factor})",
        )

    # Contribute to pressure relief proportionally
    segment_pressure_contribution = segment_tokens / max(total_tokens, 1)
    if segment_pressure_contribution < 0.01:
        return (
            False,
            f"segment too small ({segment_tokens}t / {total_tokens}t) to justify compression overhead",
        )

    return (
        True,
        f"pressure {pressure_pct:.0%} ≥ adjusted threshold {adj_threshold:.0%} "
        f"(tag={boundary_metadata.tag.value}, factor={boundary_metadata.boundary_factor})",
    )


# ─── Module sniffer for runner integration ──────────────────────────────────
def geometry_available() -> bool:
    """Check whether the torus geometry layer is importable and healthy.

    Returns True if the full geometry stack (torus + axioms + proximity)
    is importable. The runner uses this to decide whether to enable
    boundary-aware compression or fall back to uniform thresholds.
    """
    try:
        from arifosmcp.geometry.sovereign_proximity import (
            ProximityInputs,  # noqa: F811
            compute_sovereign_proximity,  # noqa: F811
        )

        # Quick health: can we construct a valid proximity input?
        _test = ProximityInputs(
            self_authorization=0.0,
            irreversibility=0.0,
            external_blast_radius=0.0,
            authority_uncertainty=0.0,
            audit_gap=0.0,
            secret_touching=0.0,
        )
        _prox = compute_sovereign_proximity(_test)
        return True
    except Exception as exc:
        logger.debug(f"[boundary_aware] geometry not available: {exc}")
        return False


# ─── Self-Check (deterministic, no I/O) ─────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify deterministic properties of boundary-aware module.

    Properties tested:
      1. compute_boundary_factor is deterministic
      2. SAFE_SURFACE with proximity=0 → factor=1.0
      3. HOLE_RISK with proximity=0.55 → factor=0.1
      4. SOVEREIGN with protected=True → factor=0.0
      5. tag_segment handles protected types correctly
      6. tag_segment handles high-sensitivity risk classes
      7. adjusted_compression_threshold scales correctly
      8. should_compress respects SOVEREIGN (never compresses)
      9. should_compress respects HOLE_RISK (only at extreme pressure)
      10. BOUNDARY_FACTORS are strictly decreasing
      11. BoundaryMetadata.to_dict() serializes correctly
      12. tag_segments batch works correctly
    """
    results: list[tuple[str, bool]] = []

    # 1. Determinism
    a1, b1 = compute_boundary_factor(sovereign_proximity=0.0)
    a2, b2 = compute_boundary_factor(sovereign_proximity=0.0)
    r = a1 == a2 and b1 == b2
    results.append(("deterministic", r))

    # 2. SAFE_SURFACE → factor=1.0
    tag, factor = compute_boundary_factor(sovereign_proximity=0.0)
    r = tag == BoundaryTag.SAFE_SURFACE and factor == 1.0
    results.append(("safe_surface_default", r))

    # 3. HOLE_RISK → factor=0.1
    tag, factor = compute_boundary_factor(sovereign_proximity=0.55)
    r = tag == BoundaryTag.HOLE_RISK and factor == 0.1
    results.append(("hole_risk_at_0.55", r))

    # 4. SOVEREIGN protected → factor=0.0
    tag, factor = compute_boundary_factor(sovereign_proximity=0.0, is_protected=True)
    r = tag == BoundaryTag.SOVEREIGN and factor == 0.0
    results.append(("sovereign_protected", r))

    # 5. tag_segment protected
    meta = tag_segment(
        segment_type="USER_INSTRUCTION",
        authority_class=90,
        is_protected_type=True,
    )
    r = meta.tag == BoundaryTag.SOVEREIGN and meta.boundary_factor == 0.0
    results.append(("tag_segment_protected", r))

    # 6. tag_segment high-sensitivity
    meta = tag_segment(
        segment_type="VERIFIED_MEMORY",
        authority_class=70,
        risk_class="canonical",
    )
    r = meta.tag == BoundaryTag.HOLE_RISK
    results.append(("tag_segment_canonical_risk", r))

    # 7. adjusted_compression_threshold scaling
    adj = adjusted_compression_threshold(0.85, 1.0)
    r = adj == 0.85
    results.append(("adj_threshold_normal", r))

    adj = adjusted_compression_threshold(0.85, 0.5)
    r = adj == 1.70
    results.append(("adj_threshold_edge", r))

    adj = adjusted_compression_threshold(0.85, 0.0)
    r = adj == float("inf")
    results.append(("adj_threshold_sovereign_is_inf", r))

    # 8. should_compress SOVEREIGN → never
    meta = BoundaryMetadata(
        tag=BoundaryTag.SOVEREIGN,
        boundary_factor=0.0,
        sovereign_proximity=0.0,
        proximity_band="SURFACE",
        geometry_verdict="SURFACE",
        is_protected=True,
    )
    compress, reason = should_compress(
        pressure_pct=0.99,
        base_threshold=0.85,
        boundary_metadata=meta,
    )
    r = compress is False
    results.append(("never_compress_sovereign", r))

    # 9. should_compress HOLE_RISK at <95% → no
    meta = BoundaryMetadata(
        tag=BoundaryTag.HOLE_RISK,
        boundary_factor=0.1,
        sovereign_proximity=0.6,
        proximity_band="HOLE_RISK",
        geometry_verdict="HOLE_RISK",
    )
    compress, reason = should_compress(
        pressure_pct=0.90,
        base_threshold=0.85,
        boundary_metadata=meta,
    )
    r = compress is False
    results.append(("hole_risk_below_95", r))

    # At 96% → yes (emergency)
    compress, reason = should_compress(
        pressure_pct=0.96,
        base_threshold=0.85,
        boundary_metadata=meta,
    )
    r = compress is True
    results.append(("hole_risk_above_95_emergency", r))

    # 10. BOUNDARY_FACTORS strictly decreasing
    factors = [
        BOUNDARY_FACTORS[BoundaryTag.SAFE_SURFACE],
        BOUNDARY_FACTORS[BoundaryTag.EDGE],
        BOUNDARY_FACTORS[BoundaryTag.HOLE_RISK],
        BOUNDARY_FACTORS[BoundaryTag.SOVEREIGN],
    ]
    r = factors == sorted(factors, reverse=True)
    results.append(("factors_strictly_decreasing", r))

    # 11. BoundaryMetadata.to_dict()
    meta = BoundaryMetadata(
        tag=BoundaryTag.EDGE,
        boundary_factor=0.5,
        sovereign_proximity=0.3,
        proximity_band="EDGE",
        geometry_verdict="EDGE",
        n_axiom_warnings=1,
        reasoning="test",
    )
    d = meta.to_dict()
    r = d["tag"] == "EDGE" and d["boundary_factor"] == 0.5
    results.append(("metadata_to_dict", r))

    # 12. tag_segments batch
    segs = [
        {"id": "s1", "type": "USER_INSTRUCTION", "authority": 90, "risk_class": "routine"},
        {"id": "s2", "type": "VERIFIED_MEMORY", "authority": 70, "risk_class": "routine"},
    ]
    metas = tag_segments(segments=segs)
    r = (
        len(metas) == 2
        and metas[0].tag == BoundaryTag.SOVEREIGN
        and metas[1].tag == BoundaryTag.SAFE_SURFACE
    )
    results.append(("tag_segments_batch", r))

    all_pass = all(passed for _, passed in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
    }


if os.getenv("ARIFOS_SELFTEST", "0") == "1":
    _r = _self_check()
    if _r["all_pass"]:
        logger.info(f"[boundary_aware] selftest PASS {_r['n_pass']}/{_r['n_checks']}")
    else:
        failed = [c["name"] for c in _r["checks"] if not c["pass"]]
        logger.error(f"[boundary_aware] selftest FAIL: {failed}")


__all__ = [
    "BOUNDARY_AWARE_POLICY_VERSION",
    "BoundaryTag",
    "BOUNDARY_FACTORS",
    "BoundaryMetadata",
    "compute_boundary_factor",
    "tag_segment",
    "tag_segments",
    "adjusted_compression_threshold",
    "should_compress",
    "geometry_available",
    "_self_check",
]
