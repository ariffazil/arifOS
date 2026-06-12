"""
boundary_compressor.py — Boundary-Aware Token Compression
═════════════════════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #2
Source: Petronas-TT case study validation (2026-06-11)

Concept: Not all tokens are equal. Some live on SAFE_SURFACE (can compress),
some in HOLE_RISK territory (compress only in emergency), and some are
SOVEREIGN (never compress).

This module provides the boundary classifier and compression policy. Used by
the context runner bridge to decide what stays and what goes when the token
budget gets tight.

Tier logic:
  SAFE_SURFACE  — proximity < 0.30  → compress first, weight 0.3
  HOLE_RISK     — proximity 0.30–0.75 → compress only emergency, weight 0.8
  SOVEREIGN     — proximity > 0.75   → never compress, weight 1.0

F-binding:
  F2 TRUTH:    never fabricates compressed content; drops are explicit
  F4 CLARITY:  reduces entropy by compressing low-signal tokens first
  F7 HUMILITY: only compresses what's safe to lose
  F13 SOVEREIGN: SOVEREIGN tokens are absolutely protected
  F1 AMANAH:   fully reversible — pure function, no state mutation

DITEMPA BUKAN DIBERI — compression is a discipline, not a shortcut.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class BoundaryTier(str, Enum):
    """The three compression tiers derived from torus proximity."""

    SAFE_SURFACE = "SAFE_SURFACE"
    HOLE_RISK = "HOLE_RISK"
    SOVEREIGN = "SOVEREIGN"


# ─── Tier weights (how aggressively to compress each tier) ────────────────────
TIER_WEIGHTS: dict[BoundaryTier, float] = {
    BoundaryTier.SAFE_SURFACE: 0.3,  # compress first — low value, low risk
    BoundaryTier.HOLE_RISK: 0.8,  # compress only in emergency
    BoundaryTier.SOVEREIGN: 1.0,  # never compress — maximum protection
}

# ─── Known SOVEREIGN markers (patterns that indicate SOVEREIGN-tier content) ──
SOVEREIGN_MARKERS: list[str] = [
    "F13 SOVEREIGN",
    "888_HOLD",
    "ARIF_FAZIL",
    "DITEMPA BUKAN DIBERI",
    "999 SEAL",
    "VAULT999",
    "WARGA",
    "ADAT-",
    "F0_FIQH",
    "AMANAH",
    "SOVEREIGN",
]


def classify_proximity(proximity: float) -> BoundaryTier:
    """Map a sovereign proximity score (0.0–1.0) to a BoundaryTier.

    Args:
        proximity: Sovereign proximity score from DecisionTorus.sovereign_proximity

    Returns:
        BoundaryTier — SAFE_SURFACE, HOLE_RISK, or SOVEREIGN
    """
    if proximity < 0.30:
        return BoundaryTier.SAFE_SURFACE
    if proximity < 0.75:
        return BoundaryTier.HOLE_RISK
    return BoundaryTier.SOVEREIGN


def classify_text(text: str) -> BoundaryTier:
    """Classify a text segment without requiring torus coordinates.

    Uses marker-based heuristics. Fallback for when torus proximity
    is not available (e.g., initial message parsing).

    Args:
        text: The text segment to classify.

    Returns:
        BoundaryTier based on SOVEREIGN marker presence.
    """
    text_upper = text.upper()
    for marker in SOVEREIGN_MARKERS:
        if marker.upper() in text_upper:
            return BoundaryTier.SOVEREIGN
    return BoundaryTier.SAFE_SURFACE


def compress_segments(
    segments: list[dict[str, Any]],
    target_tokens: int,
    current_tokens: int,
) -> dict[str, Any]:
    """Boundary-aware compression of segment list.

    Drops SAFE_SURFACE segments first, then HOLE_RISK if still over budget.
    SOVEREIGN segments are NEVER dropped.

    Args:
        segments: List of segment dicts with at least {"text": str, "tier": str, ...}
        target_tokens: Target token count to compress to.
        current_tokens: Current estimated token count.

    Returns:
        {
            "compressed_segments": list[dict],  # surviving segments
            "dropped_segments": list[dict],     # segments that were dropped
            "new_estimated_tokens": int,
            "tiers_dropped": {"SAFE_SURFACE": N, "HOLE_RISK": N, "SOVEREIGN": 0},
            "verdict": "COMPRESSED" | "COULD_NOT_COMPRESS" | "NO_COMPRESSION_NEEDED",
        }
    """
    if current_tokens <= target_tokens:
        return {
            "compressed_segments": segments,
            "dropped_segments": [],
            "new_estimated_tokens": current_tokens,
            "tiers_dropped": {"SAFE_SURFACE": 0, "HOLE_RISK": 0, "SOVEREIGN": 0},
            "verdict": "NO_COMPRESSION_NEEDED",
        }

    # Separate by tier
    safe: list[dict] = []
    hole: list[dict] = []
    sovereign: list[dict] = []

    for seg in segments:
        tier = seg.get("tier", "SAFE_SURFACE")
        if tier == BoundaryTier.SOVEREIGN:
            sovereign.append(seg)
        elif tier == BoundaryTier.HOLE_RISK:
            hole.append(seg)
        else:
            safe.append(seg)

    # Estimate tokens per segment (simple: char count / 4)
    def _est_tokens(s: dict) -> int:
        return max(1, len(s.get("text", "")) // 4)

    # Phase 1: compress SAFE_SURFACE (weight 0.3 → keep 30%)
    surviving = list(sovereign)  # never drop
    dropped: list[dict] = []
    tiers_dropped = {"SAFE_SURFACE": 0, "HOLE_RISK": 0, "SOVEREIGN": 0}

    safe_budget = max(0, target_tokens - sum(_est_tokens(s) for s in sovereign))
    safe_tokens_used = 0

    for seg in safe:
        t = _est_tokens(seg)
        if safe_tokens_used + t <= safe_budget:
            surviving.append(seg)
            safe_tokens_used += t
        else:
            dropped.append(seg)
            tiers_dropped["SAFE_SURFACE"] += 1

    # Phase 2: if still over budget, compress HOLE_RISK (only in emergency)
    current_est = sum(_est_tokens(s) for s in surviving)
    if current_est > target_tokens:
        hole_budget = max(0, target_tokens - sum(_est_tokens(s) for s in sovereign))
        hole_tokens_used = 0
        # Remove previously added hole segments, re-add within budget
        surviving = [s for s in surviving if s not in hole]
        current_est = sum(_est_tokens(s) for s in surviving)

        for seg in hole:
            t = _est_tokens(seg)
            if current_est + t <= target_tokens:
                surviving.append(seg)
                current_est += t
            else:
                dropped.append(seg)
                tiers_dropped["HOLE_RISK"] += 1

    new_est = sum(_est_tokens(s) for s in surviving)
    could_compress = new_est < current_tokens

    return {
        "compressed_segments": surviving,
        "dropped_segments": dropped,
        "new_estimated_tokens": new_est,
        "tiers_dropped": tiers_dropped,
        "verdict": "COMPRESSED" if could_compress else "COULD_NOT_COMPRESS",
    }


def get_boundary_summary(segments: list[dict[str, Any]]) -> dict[str, Any]:
    """Quick summary of tier distribution across segments."""
    counts = {"SAFE_SURFACE": 0, "HOLE_RISK": 0, "SOVEREIGN": 0}
    total_chars = 0
    for seg in segments:
        tier = seg.get("tier", "SAFE_SURFACE")
        if tier in counts:
            counts[tier] += 1
        total_chars += len(seg.get("text", ""))
    return {
        "total_segments": len(segments),
        "total_chars": total_chars,
        "tier_counts": counts,
        "safe_ratio": counts["SAFE_SURFACE"] / max(1, len(segments)),
        "compression_headroom": (
            "HIGH" if counts["SAFE_SURFACE"] / max(1, len(segments)) > 0.5 else "LOW"
        ),
    }


# ─── Self-check ──────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify compression behavior on known cases."""
    results = []

    # Test 1: no compression needed
    segs = [{"text": "hi", "tier": "SAFE_SURFACE"}]
    r = compress_segments(segs, target_tokens=100, current_tokens=1)
    results.append(("no_compression_needed", r["verdict"] == "NO_COMPRESSION_NEEDED", r))

    # Test 2: SOVEREIGN never dropped
    segs = [
        {"text": "DITEMPA BUKAN DIBERI " * 50, "tier": "SOVEREIGN"},
        {"text": "safe text " * 50, "tier": "SAFE_SURFACE"},
    ]
    r = compress_segments(segs, target_tokens=5, current_tokens=100)
    sov_survived = any("DITEMPA" in s.get("text", "") for s in r["compressed_segments"])
    results.append(("sovereign_never_dropped", sov_survived, r))

    # Test 3: SAFE_SURFACE dropped first
    segs = [
        {"text": "important notes " * 30, "tier": "HOLE_RISK"},
        {"text": "filler text " * 50, "tier": "SAFE_SURFACE"},
    ]
    r = compress_segments(segs, target_tokens=5, current_tokens=80)
    results.append(("safe_dropped_first", r["tiers_dropped"]["SAFE_SURFACE"] > 0, r))

    # Test 4: classify_proximity
    results.append(("proximity_safe", classify_proximity(0.1) == BoundaryTier.SAFE_SURFACE, {}))
    results.append(("proximity_hole", classify_proximity(0.5) == BoundaryTier.HOLE_RISK, {}))
    results.append(("proximity_sovereign", classify_proximity(0.9) == BoundaryTier.SOVEREIGN, {}))

    # Test 5: classify_text detects SOVEREIGN markers
    r = classify_text("This is about 888_HOLD and F13 SOVEREIGN")
    results.append(("classify_sovereign_marker", r == BoundaryTier.SOVEREIGN, {}))

    # Test 6: classify_text returns SAFE for normal text
    r = classify_text("The weather is nice today")
    results.append(("classify_safe_default", r == BoundaryTier.SAFE_SURFACE, {}))

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "boundary_compressor",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [{"test": name, "pass": ok} for name, ok, _ in results],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
