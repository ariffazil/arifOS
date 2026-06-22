"""arifOS canonical tool exports."""

from __future__ import annotations

from arifosmcp.tools.evidence import arif_fetch
from arifosmcp.tools.forge import arif_forge
from arifosmcp.tools.heart import arif_critique
from arifosmcp.tools.judge import arif_judge
from arifosmcp.tools.kernel_canonical import (
    arif_route,  # new canonical routing (RULE 14)
    arif_triage,  # session status, preflight, priority
)
from arifosmcp.tools.ops import arif_measure
from arifosmcp.tools.reason import arif_think
from arifosmcp.tools.reply import arif_compose
from arifosmcp.tools.sense import arif_observe
from arifosmcp.tools.session import arif_init
from arifosmcp.tools.shadow_geometry import arif_model_compare, arif_self_evaluate
from arifosmcp.tools.vault import arif_seal

__all__ = [
    "arif_init",
    "arif_observe",
    "arif_fetch",
    "arif_think",
    # ── Canonical tools (RULE 14 MODE-FIRST) ──
    "arif_route",          # replaces arif_kernel_route for routing
    "arif_triage",         # replaces arif_kernel_route(mode=status|preflight|triage)
    # ── Legacy (soft-deprecated, still functional) ──
    "arif_compose",
    "arif_critique",
    "arif_measure",
    "arif_judge",
    "arif_seal",
    "arif_forge",
    "arif_self_evaluate",
    "arif_model_compare",
]
