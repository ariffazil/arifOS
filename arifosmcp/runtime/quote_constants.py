"""
arifosmcp/runtime/quote_constants.py — Single source of truth for APEX constants

Centralizes APEX_ORGANS, stage bindings, and re-exports compute_apex_fingerprint
for Path Y dedup (2026-07-19). All three consumers (quote_registry.py,
philosophy_registry.py, tests) import from here.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# APEX ORGANS — Seven conservation laws (tuple, not list)
# ═══════════════════════════════════════════════════════════════════════════════
# APEX canon: organ set, not sequence. Tuple for immutability.
# G = Reality · Governance · Civilization · Execution · Memory · Witness · Meaning
# Multiplicative — zero anywhere = collapse. C_dark = shadow term.
APEX_ORGANS: tuple[str, ...] = (
    "Reality",
    "Governance",
    "Civilization",
    "Execution",
    "Memory",
    "Witness",
    "Meaning",
)

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE BINDING — Quotes are resources, not tools
# ═══════════════════════════════════════════════════════════════════════════════
PERMITTED_STAGES: frozenset[str] = frozenset({"555_HEART", "999_RECEIPT"})
FORBIDDEN_STAGES: frozenset[str] = frozenset(
    {"000_INIT", "111_OBSERVE", "333_THINK", "444_ROUTE", "777_FORGE", "888_AUDIT"}
)

# ═══════════════════════════════════════════════════════════════════════════════
# DEPLOY THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════════
# G_DEPLOY_THRESHOLD = 0.50 (matches APEX verdict threshold)
# C_DARK_CEILING = 0.30 (Pillar VI GOVERNED state)
G_DEPLOY_THRESHOLD: float = 0.50
C_DARK_CEILING: float = 0.30


# ═══════════════════════════════════════════════════════════════════════════════
# RE-EXPORT compute_apex_fingerprint (canonical impl lives in quote_registry.py)
# ═══════════════════════════════════════════════════════════════════════════════
# Lazy import avoids circular dependency: quote_registry imports from
# quote_constants, so quote_constants cannot import quote_registry at module
# level. The re-export is a function wrapper — loaded on first call.
def compute_apex_fingerprint(*args, **kwargs):
    """Wrapper around quote_registry.compute_apex_fingerprint.

    Re-exported here for convenience. Canonical implementation lives in
    arifosmcp.runtime.quote_registry.
    """
    from arifosmcp.runtime.quote_registry import (
        compute_apex_fingerprint as _impl,
    )

    return _impl(*args, **kwargs)
