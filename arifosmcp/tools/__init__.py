"""arifOS canonical tool exports."""

from __future__ import annotations

from arifosmcp.tools.evidence import arif_evidence_fetch
from arifosmcp.tools.forge import arif_forge_execute
from arifosmcp.tools.gateway import arif_gateway_connect
from arifosmcp.tools.heart import arif_heart_critique
from arifosmcp.tools.judge import arif_judge_deliberate
from arifosmcp.tools.kernel import arif_kernel_route  # soft-deprecated, see kernel_canonical.py
from arifosmcp.tools.kernel_canonical import (
    arif_route,          # new canonical routing (RULE 14)
    arif_triage,         # session status, preflight, priority
    arif_kernel_status,   # telemetry, discover, prediction
    arif_bridge,         # direct organ tool call (bypass intent map)
    arif_kernel_attest,   # organ attestation (organ param, not name)
    arif_kernel_health,   # federation liveness snapshot
)
from arifosmcp.tools.memory import arif_memory_recall
from arifosmcp.tools.ops import arif_ops_measure
from arifosmcp.tools.reason import arif_mind_reason
from arifosmcp.tools.reply import arif_reply_compose
from arifosmcp.tools.sense import arif_sense_observe
from arifosmcp.tools.session import arif_session_init
from arifosmcp.tools.vault import arif_vault_seal
from arifosmcp.tools.shadow_geometry import arif_self_evaluate, arif_model_compare

__all__ = [
    "arif_session_init",
    "arif_sense_observe",
    "arif_evidence_fetch",
    "arif_mind_reason",
    # ── Canonical tools (RULE 14 MODE-FIRST) ──
    "arif_route",          # replaces arif_kernel_route for routing
    "arif_triage",         # replaces arif_kernel_route(mode=status|preflight|triage)
    "arif_kernel_status",  # replaces arif_kernel_route(mode=telemetry|discover)
    "arif_bridge",         # replaces arif_kernel_route(mode=bridge)
    "arif_kernel_attest",  # replaces arif_kernel_route(mode=attest)
    "arif_kernel_health", # replaces arif_kernel_route(mode=health)
    # ── Legacy (soft-deprecated, still functional) ──
    "arif_kernel_route",   # DEPRECATED: 16-mode bloat → use arif_route + arif_triage + arif_kernel_status
    "arif_reply_compose",
    "arif_memory_recall",
    "arif_heart_critique",
    "arif_gateway_connect",
    "arif_ops_measure",
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_forge_execute",
    "arif_self_evaluate",
    "arif_model_compare",
]
