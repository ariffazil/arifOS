"""
ART — Agentic Recursive Tooling (re-export shim)

Delegates to runtime/art/ subpackage for all logic.
This file exists for backward compatibility only.

Usage (unchanged):
    from arifosmcp.runtime.art import art, ArtRequest, ArtVerdict

The reflex is now in runtime/art/reflex.py.
The ceiling guard is now a docstring, not a runtime assertion —
the subpackage enforces modularity through structure.

DITEMPA BUKAN DIBERI — Reflex is forged, not configured.
"""

# Re-export everything from the subpackage
from arifosmcp.runtime.art.blast import (
    action_class_to_art_str,
    blast_radius_to_art_str,
)
from arifosmcp.runtime.art.lifecycle import (
    SILENT_FALLBACK_HOLD_THRESHOLD,
    ToolState,
)
from arifosmcp.runtime.art.lifecycle import (
    suggest_transition as _suggest_transition,
)
from arifosmcp.runtime.art.reflex import ArtRequest, ArtResult, art
from arifosmcp.runtime.art.trust_curve import (
    trust_score_to_band,
    update_trust_score,
)
from arifosmcp.runtime.art.verdict import ArtReason, ArtVerdict

# Schema types for convenience
from arifosmcp.schemas.art import (
    ArtPrecheckResult,
    ArtToolState,
    ToolLifecycle,
    TrustBand,
)

__all__ = [
    "art",
    "ArtRequest",
    "ArtResult",
    "ArtVerdict",
    "ArtReason",
    "ToolState",
    "_suggest_transition",
    "SILENT_FALLBACK_HOLD_THRESHOLD",
    "action_class_to_art_str",
    "blast_radius_to_art_str",
    "update_trust_score",
    "trust_score_to_band",
    "ArtToolState",
    "ArtPrecheckResult",
    "ToolLifecycle",
    "TrustBand",
]
