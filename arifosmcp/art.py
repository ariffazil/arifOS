"""
ART — Agentic Recursive Tooling (federation umbrella).

The 6 organs of ART, federated under one namespace:

  ┌─────────────┬───────────────────────────────────────┬──────────────────┐
  │ Organ        │ Module                                │ Hot/Cold         │
  ├─────────────┼───────────────────────────────────────┼──────────────────┤
  │ Reflex       │ arifosmcp.runtime.art                 │ HOT (≤500 lines) │
  │ Registry     │ arifosmcp.runtime.art_registry        │ HOT (W2)         │
  │ Compat       │ arifosmcp.runtime.art_compat          │ COLD (legacy)    │
  │ Pusaka       │ arifosmcp.runtime.art_pusaka          │ COLD (doctrine)  │
  │ Library      │ arifosmcp.runtime.art_library         │ COLD (persistence)│
  │ Mind         │ arifosmcp.core.art_mind               │ COLD (cognition) │
  └─────────────┴───────────────────────────────────────┴──────────────────┘

Doctrine (binding):
  ART may recommend. Judge authorizes. Vault witnesses.
  The reflex disciplines. The mind proposes. The doctrine constrains.
  The library remembers. The registry tracks state. The compat shim bridges the past.

Usage:
    from arifosmcp.art import (
        # Reflex
        art, ArtRequest, ArtResult, ArtVerdict, ArtReason, ToolState,
        # Registry (W2)
        ArtRegistry, ToolRecord, get_registry,
        # Library
        ArtLibrary, ArtVerdictRow, get_library,
        # Mind (cognition)
        ArtMind, ArtMindConfig, ThinkRequest, ThinkResponse,
    )

DITEMPA BUKAN DIBERI — Six organs, one reflex. Registry forged, mind forged,
library forged, reflex forged, doctrine preserved, compat shimmed.
The federation is the ART.
"""

# === Reflex (hot path) ===
from arifosmcp.runtime.art import (
    art,
    ArtRequest,
    ArtResult,
    ArtVerdict,
    ArtReason,
    ToolState,
)

# === Registry (hot path — W2, bucket-based per-tool classification) ===
from arifosmcp.runtime.art_registry import (
    TOOL_BUCKET,
    PER_BUCKET_BLAST,
    PER_BUCKET_REFLEX_RULES,
    DEFAULT_TOOL_STATE,
    ArtRegistry,
    get_registry,
    get_bucket,
    get_default_blast,
    get_reflex_rules,
    get_default_tool_state,
)

# === Compat (legacy 6-check shim) ===
# Re-exported lazily — compat is rarely used in v3+
# (art_compat.py exposes its own test surface; we don't surface it here)

# === Pusaka (doctrinal heritage) ===
# Pusaka is a doctrine module, not typically called from runtime code.
# The constitutional constants are documented in arifOS/pusaka/.

# === Library (cold path — call history + RAG) ===
from arifosmcp.runtime.art_library import (
    ArtLibrary,
    ArtVerdictRow,
    StateLabel,
    VerdictLabel,
    get_library,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_INTENT_LIMIT,
    DEFAULT_TOOL_LIMIT,
)

# === Mind (cold path — cognition substrate) ===
from arifosmcp.core.art_mind import (
    MindaService as ArtMind,
    MindConfig as ArtMindConfig,
    ThinkRequest,
    ThinkResponse,
    ScoredPlan,
    BeliefState,
    Plan,
    ToolAction,
    MARUAH_HARD_FLOOR,
    F_CONSTRAINTS,
)


__all__ = [
    # Reflex
    "art",
    "ArtRequest",
    "ArtResult",
    "ArtVerdict",
    "ArtReason",
    "ToolState",
    # Registry (W2)
    "TOOL_BUCKET",
    "PER_BUCKET_BLAST",
    "PER_BUCKET_REFLEX_RULES",
    "DEFAULT_TOOL_STATE",
    "ArtRegistry",
    "get_registry",
    "get_bucket",
    "get_default_blast",
    "get_reflex_rules",
    "get_default_tool_state",
    # Library
    "ArtLibrary",
    "ArtVerdictRow",
    "StateLabel",
    "VerdictLabel",
    "get_library",
    "DEFAULT_RETENTION_DAYS",
    "DEFAULT_LOOKBACK_DAYS",
    "DEFAULT_INTENT_LIMIT",
    "DEFAULT_TOOL_LIMIT",
    # Mind (cognition)
    "ArtMind",
    "ArtMindConfig",
    "ThinkRequest",
    "ThinkResponse",
    "ScoredPlan",
    "BeliefState",
    "Plan",
    "ToolAction",
    "MARUAH_HARD_FLOOR",
    "F_CONSTRAINTS",
]
