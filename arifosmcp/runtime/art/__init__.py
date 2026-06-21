"""
ART package — Agentic Recursive Tooling.

Re-exports from submodules so callers can continue using:
    from arifosmcp.runtime.art import art, ArtRequest, ArtResult, ...

Also re-exports schema types from arifosmcp.schemas.art for convenience:
    from arifosmcp.runtime.art import ArtToolState, ArtPrecheckResult, ...

DITEMPA BUKAN DIBERI — Package is forged, not configured.
"""

from arifosmcp.runtime.art.lifecycle import (
    SILENT_FALLBACK_HOLD_THRESHOLD,
    ToolState,
    suggest_transition,
)
from arifosmcp.runtime.art.verdict import ArtReason, ArtVerdict
from arifosmcp.runtime.art.blast import (
    action_class_to_art_str,
    blast_radius_to_art_str,
)
from arifosmcp.runtime.art.trust_curve import (
    trust_score_to_band,
    update_trust_score,
)
from arifosmcp.runtime.art.reflex import ArtRequest, ArtResult, art

# Re-export schema types for convenience
from arifosmcp.schemas.art import (
    ArtPrecheckResult,
    ArtToolState,
    ToolLifecycle,
    TrustBand,
)

__all__ = [
    # Reflex
    "art",
    "ArtRequest",
    "ArtResult",
    # Verdict
    "ArtVerdict",
    "ArtReason",
    # Lifecycle
    "ToolState",
    "suggest_transition",
    "SILENT_FALLBACK_HOLD_THRESHOLD",
    # Blast
    "action_class_to_art_str",
    "blast_radius_to_art_str",
    # Trust
    "update_trust_score",
    "trust_score_to_band",
    # Schema types (re-exported for convenience)
    "ArtToolState",
    "ArtPrecheckResult",
    "ToolLifecycle",
    "TrustBand",
]
