"""
arifosmcp/schemas/memory_modes.py — arif_memory Federated Mode Enum v5
═════════════════════════════════════════════════════════════════════

Memory Kernel v1.0 (Direction 1, ratified 2026-06-21) — Day 1 schemas.

The 7 canonical modes of the federated arif_memory tool. Each mode maps to:
  - An action class (OBSERVE / MUTATE / ATOMIC).
  - A floor pre/post-check profile (see memory_payload.py).
  - A receipt shape (see memory_object.py).
  - A backend dispatcher path (existing cognitive_memory / engineering_memory
    plus new promote/forget/attest handlers).

The naming follows the existing arifOS federated-tool pattern:
  - arif_kernel_route (mode=route|stage|lane|list|status|surface_drift)
  - arif_think (mode=reason|reflect|verify|critique|plan|...)
  - arif_judge (mode=judge|validate|hold|rules|armor|probe|notify)
  - arif_seal (mode=seal|verify|ledger|changelog|audit)
  - arif_observe (mode=search|ingest|compass|atlas|entropy_dS|vitals)
  - arif_forge (mode=engineer|query|write|generate|commit|recall|dry_run)

arif_memory joins this federation with mode=recall|remember|promote|
revise|forget|attest|inspect.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal


# ── The 7 federated modes ─────────────────────────────────────────────────

class MemoryMode(str, Enum):
    """
    Canonical modes of arif_memory.

    Recall    OBSERVE  — Semantic + graph + vault retrieval.
                         Hybrid vector → graph → vault cascade.
    Inspect   OBSERVE  — Read a memory object's full state (read-only, raw view).
    Attest    OBSERVE  — Verify a memory_id against the vault seal chain.
    Remember  MUTATE   — Write a candidate memory (L1-L5). Default-deny.
    Promote   MUTATE   — Move candidate from lower tier to higher tier.
    Revise    MUTATE   — Supersede prior memory with corrected version (audit).
    Forget    ATOMIC   — Soft-delete or revoke. NEVER destructive to L6.
                         Human ack required (L13 SOVEREIGN).
    """
    RECALL   = "recall"
    INSPECT  = "inspect"
    ATTEST   = "attest"
    REMEMBER = "remember"
    PROMOTE  = "promote"
    REVISE   = "revise"
    FORGET   = "forget"


# ── Mode metadata ─────────────────────────────────────────────────────────
# Cross-reference of mode → action class, floor profile, backend path.
# This is the metadata the kernel dispatcher consults at runtime.

MODE_ACTION_CLASS: dict[MemoryMode, str] = {
    MemoryMode.RECALL:   "OBSERVE",
    MemoryMode.INSPECT:  "OBSERVE",
    MemoryMode.ATTEST:   "OBSERVE",
    MemoryMode.REMEMBER: "EXECUTE_REVERSIBLE",
    MemoryMode.PROMOTE:  "EXECUTE_HIGH_IMPACT",
    MemoryMode.REVISE:   "EXECUTE_HIGH_IMPACT",
    MemoryMode.FORGET:   "IRREVERSIBLE",
}


# Floors checked PRE-mode-execution.
# (See schemas/memory_payload.py for the full per-mode payload schema,
#  and the design doc §6.2 for the rationale per mode.)
MODE_PRE_FLOORS: dict[MemoryMode, tuple[str, ...]] = {
    MemoryMode.RECALL:   ("L02", "L12"),
    MemoryMode.INSPECT:  ("L02", "L12"),
    MemoryMode.ATTEST:   ("L02", "L11", "L12"),
    MemoryMode.REMEMBER: ("L01", "L02", "L08", "L11", "L12"),
    MemoryMode.PROMOTE:  ("L01", "L02", "L04", "L07", "L11", "L12"),
    MemoryMode.REVISE:   ("L01", "L02", "L04", "L09", "L11", "L12"),
    MemoryMode.FORGET:   ("L01", "L02", "L04", "L09", "L11", "L12", "L13"),
}


# Floors checked POST-mode-execution.
MODE_POST_FLOORS: dict[MemoryMode, tuple[str, ...]] = {
    MemoryMode.RECALL:   ("L04", "L08"),
    MemoryMode.INSPECT:  ("L04",),
    MemoryMode.ATTEST:   ("L04", "L09"),
    MemoryMode.REMEMBER: ("L04", "L05", "L09"),
    MemoryMode.PROMOTE:  ("L04", "L08", "L09"),
    MemoryMode.REVISE:   ("L04", "L08"),
    MemoryMode.FORGET:   ("L04", "L08", "L09"),
}


# Whether the mode requires a kernel-issued lease.
MODE_REQUIRES_LEASE: dict[MemoryMode, bool] = {
    MemoryMode.RECALL:   False,
    MemoryMode.INSPECT:  False,
    MemoryMode.ATTEST:   False,
    MemoryMode.REMEMBER: True,
    MemoryMode.PROMOTE:  True,
    MemoryMode.REVISE:   True,
    MemoryMode.FORGET:   True,        # + 888_HOLD if cascade=True
}


# Whether the mode requires human acknowledgement.
MODE_REQUIRES_HUMAN_ACK: dict[MemoryMode, bool] = {
    MemoryMode.RECALL:   False,
    MemoryMode.INSPECT:  False,
    MemoryMode.ATTEST:   False,
    MemoryMode.REMEMBER: False,
    MemoryMode.PROMOTE:  False,       # recommended for L4+, but not blocking
    MemoryMode.REVISE:   False,
    MemoryMode.FORGET:   True,        # MANDATORY per L13 SOVEREIGN
}


# Backend dispatcher target — which existing internal handler this mode
# routes to in Phase 2 implementation. None means NEW handler needed.
MODE_BACKEND_TARGET: dict[MemoryMode, str | None] = {
    MemoryMode.RECALL:   "cognitive_memory.cognitive_recall + graph_query + vault_attest",
    MemoryMode.INSPECT:  "cognitive_memory.graph_get + contradict_status",
    MemoryMode.ATTEST:   "NEW — vault_attest handler",
    MemoryMode.REMEMBER: "cognitive_memory.cognitive_learn + engineering_memory.vector_store",
    MemoryMode.PROMOTE:  "NEW — promote handler",
    MemoryMode.REVISE:   "cognitive_memory.contradict_resolve + supersede logic",
    MemoryMode.FORGET:   "NEW — forget/tombstone handler",
}


# Stage code — used for arifos pipeline stage labels.
MODE_STAGE: dict[MemoryMode, str] = {
    MemoryMode.RECALL:   "555m",
    MemoryMode.INSPECT:  "555m",
    MemoryMode.ATTEST:   "555m",
    MemoryMode.REMEMBER: "555m",
    MemoryMode.PROMOTE:  "555m",
    MemoryMode.REVISE:   "555m",
    MemoryMode.FORGET:   "555m",
}


# Convenience type alias — used in payload discriminator field.
MemoryModeName = Literal[
    "recall", "inspect", "attest",
    "remember", "promote", "revise", "forget",
]


# ── Backward-compat aliases (legacy v4 modes fold into v5) ───────────────
# Per design doc §3.1.1 — the 8 legacy cognitive_memory modes fold into
# 7 federated modes. The legacy mode strings are kept here so the
# Phase 2 dispatcher can route deprecated callers.

LEGACY_MODE_ALIASES: dict[str, MemoryMode] = {
    # Direct 1:1
    "cognitive_recall": MemoryMode.RECALL,
    "cognitive_learn":  MemoryMode.REMEMBER,
    "graph_get":        MemoryMode.INSPECT,
    "graph_store":      MemoryMode.REMEMBER,    # sub-mode handled via class=graph
    "graph_query":      MemoryMode.RECALL,       # sub-mode handled via class=graph
    "cognitive_cross_session": MemoryMode.RECALL,  # sub-mode via scope=cross_session
    "contradict_scan":  MemoryMode.INSPECT,     # sub-mode via aspect=contradictions
    "contradict_status": MemoryMode.ATTEST,      # sub-mode via aspect=contradictions
    "contradict_resolve": MemoryMode.REVISE,     # sub-mode via kind=resolve_contradiction
    # Engineering memory (legacy)
    "engineer":         MemoryMode.REMEMBER,
    "vector_query":     MemoryMode.RECALL,
    "vector_store":     MemoryMode.REMEMBER,
    "vector_forget":    MemoryMode.FORGET,
    "generate":         MemoryMode.REMEMBER,
    "query":            MemoryMode.RECALL,
    # Legacy v4 (from existing description in constitutional_map.py)
    "store":            MemoryMode.REMEMBER,
    "seal":             MemoryMode.ATTEST,
    "forget":           MemoryMode.FORGET,
    "update":           MemoryMode.REVISE,
    "audit":            MemoryMode.ATTEST,
    "stats":            MemoryMode.INSPECT,
    "learn":            MemoryMode.REMEMBER,
    "init_recall":      MemoryMode.RECALL,
    "search":           MemoryMode.RECALL,
    "context":          MemoryMode.RECALL,
    "quarantine":       MemoryMode.REMEMBER,
    "import":           MemoryMode.REMEMBER,
}


def resolve_legacy_mode(legacy: str) -> MemoryMode | None:
    """Map a legacy mode string to the current federated mode, if known."""
    return LEGACY_MODE_ALIASES.get(legacy)


__all__ = [
    "MemoryMode",
    "MemoryModeName",
    "LEGACY_MODE_ALIASES",
    "resolve_legacy_mode",
    "MODE_ACTION_CLASS",
    "MODE_PRE_FLOORS",
    "MODE_POST_FLOORS",
    "MODE_REQUIRES_LEASE",
    "MODE_REQUIRES_HUMAN_ACK",
    "MODE_BACKEND_TARGET",
    "MODE_STAGE",
]