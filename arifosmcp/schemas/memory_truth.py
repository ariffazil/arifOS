"""
arifosmcp/schemas/memory_truth.py — Truth-Class Taxonomy v5
════════════════════════════════════════════════════════════

Memory Kernel v1.0 (Direction 1, ratified 2026-06-21) — Day 1 schemas.

7 epistemic truth-classes for any MemoryObject. The class governs:
  - Which substrate tiers the memory may inhabit (L1-L6).
  - Default TTL behaviour.
  - Whether the memory is eligible for recall by default.
  - Floor pre/post-check requirements.

This file is FOUNDATIONAL — memory_modes.py and memory_payload.py
both depend on the TruthClass enum and its helpers.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal


# ── The 7 truth-classes ────────────────────────────────────────────────────


class TruthClass(str, Enum):
    """
    Epistemic status of a memory object across its lifecycle.

    Lifecycle arrow (§7.9 doctrine):
        observed → claimed → derived → approved → sealed
                                                    ↘
                                              contested (parallel)
                                                    ↘
                                            deprecated (terminal)

    OBSERVED:    Direct tool/user evidence. Highest initial authority.
    CLAIMED:     Asserted by model or external source; requires source_receipt.
    DERIVED:     Inferred from ≥2 evidence points. Has derivation lineage.
    APPROVED:    Human accepted. Eligible for L4 promotion.
    SEALED:      Constitutionally finalised in vault (L6). Hash-chained.
    CONTESTED:   Contradiction unresolved. Excluded from default recall.
    DEPRECATED:  Superseded by later fact. Tombstoned, never deleted.
    """

    OBSERVED = "observed"
    CLAIMED = "claimed"
    DERIVED = "derived"
    APPROVED = "approved"
    SEALED = "sealed"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"


# ── Tier allowance per truth-class ─────────────────────────────────────────
# A memory's truth-class determines which substrate tiers it may inhabit.
# L1 = ephemeral Redis; L6 = VAULT999 immutable.
# This is a HARD constraint enforced at write time (remember) and at
# promotion time (promote).

_TRUTH_TIER_ALLOWANCE: dict[TruthClass, frozenset[str]] = {
    TruthClass.OBSERVED: frozenset({"L1", "L2", "L3", "L4"}),
    TruthClass.CLAIMED: frozenset({"L3"}),  # vector only w/ receipts
    TruthClass.DERIVED: frozenset({"L3", "L4"}),
    TruthClass.APPROVED: frozenset({"L3", "L4", "L5"}),
    TruthClass.SEALED: frozenset({"L6"}),  # vault only
    TruthClass.CONTESTED: frozenset({"L3", "L4"}),  # both sides retained
    TruthClass.DEPRECATED: frozenset({"L4", "L5", "L6"}),  # tombstone lineage
}


def tier_allowed(truth: TruthClass, tier: str) -> bool:
    """Return True iff a memory of this truth-class may inhabit the given tier."""
    return tier in _TRUTH_TIER_ALLOWANCE.get(truth, frozenset())


def allowed_tiers(truth: TruthClass) -> frozenset[str]:
    """Return the full set of tiers allowed for this truth-class."""
    return _TRUTH_TIER_ALLOWANCE.get(truth, frozenset())


# ── Default TTL per truth-class ────────────────────────────────────────────
# Used when PolicyBlock.ttl is not explicitly set.

_TRUTH_DEFAULT_TTL_HOURS: dict[TruthClass, int | None] = {
    TruthClass.OBSERVED: 24,  # one working day; promote or lose
    TruthClass.CLAIMED: 72,  # 3 days to verify or claim decays
    TruthClass.DERIVED: 2160,  # 90 days; revisit periodically
    TruthClass.APPROVED: 8760,  # 1 year
    TruthClass.SEALED: None,  # forever — vault retains
    TruthClass.CONTESTED: 168,  # 1 week to resolve or escalate
    TruthClass.DEPRECATED: 8760,  # 1 year tombstone, then retire
}


def default_ttl_hours(truth: TruthClass) -> int | None:
    """Return the default TTL in hours for this truth-class, or None for forever."""
    return _TRUTH_DEFAULT_TTL_HOURS.get(truth)


# ── Default recall eligibility ─────────────────────────────────────────────
# CONTESTED is excluded by default; DEPRECATED is excluded; the rest pass.

_TRUTH_DEFAULT_RECALL: dict[TruthClass, bool] = {
    TruthClass.OBSERVED: True,
    TruthClass.CLAIMED: True,
    TruthClass.DERIVED: True,
    TruthClass.APPROVED: True,
    TruthClass.SEALED: True,
    TruthClass.CONTESTED: False,
    TruthClass.DEPRECATED: False,
}


def default_recall_eligible(truth: TruthClass) -> bool:
    """Return True iff this truth-class is eligible for recall by default."""
    return _TRUTH_DEFAULT_RECALL.get(truth, False)


# ── Truth-class transitions ───────────────────────────────────────────────
# Defines the legal forward transitions in the memory lifecycle.
# Backward transitions require a `revise` operation with audit.

_LEGAL_TRANSITIONS: dict[TruthClass, frozenset[TruthClass]] = {
    TruthClass.OBSERVED: frozenset(
        {TruthClass.CLAIMED, TruthClass.DERIVED, TruthClass.APPROVED, TruthClass.SEALED}
    ),
    TruthClass.CLAIMED: frozenset(
        {TruthClass.DERIVED, TruthClass.APPROVED, TruthClass.CONTESTED, TruthClass.DEPRECATED}
    ),
    TruthClass.DERIVED: frozenset(
        {TruthClass.APPROVED, TruthClass.CONTESTED, TruthClass.DEPRECATED}
    ),
    TruthClass.APPROVED: frozenset(
        {TruthClass.SEALED, TruthClass.CONTESTED, TruthClass.DEPRECATED}
    ),
    TruthClass.SEALED: frozenset({TruthClass.CONTESTED}),  # vault can be contested
    TruthClass.CONTESTED: frozenset(
        {TruthClass.APPROVED, TruthClass.DEPRECATED, TruthClass.SEALED}
    ),
    TruthClass.DEPRECATED: frozenset(),  # terminal
}


def can_transition(from_cls: TruthClass, to_cls: TruthClass) -> bool:
    """Return True iff a forward transition from→to is allowed without revise."""
    return to_cls in _LEGAL_TRANSITIONS.get(from_cls, frozenset())


def legal_next(from_cls: TruthClass) -> frozenset[TruthClass]:
    """Return the set of truth-classes reachable from this one in one step."""
    return _LEGAL_TRANSITIONS.get(from_cls, frozenset())


# ── Memory-class taxonomy (cognitive dimension) ───────────────────────────
# Distinct from truth-class: memory-class is WHAT the memory IS, while
# truth-class is HOW CONFIDENT we are in it.


class MemoryClass(str, Enum):
    """
    Cognitive class of a memory object.

    WORKING:     Immediate token-budgeted context (L1/L2 only).
    SESSION:     Continuity across one thread/session (L2).
    EPISODIC:    What happened, when, under what task (L3/L4).
    SEMANTIC:    Stable facts, concepts, preferences, entity profiles (L3/L4).
    PROCEDURAL:  How to do recurring workflows (L3/L4/L5).
    GOVERNANCE:  Holds, vetoes, exceptions, floor violations, approvals (L4/L6).
    """

    WORKING = "working"
    SESSION = "session"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    GOVERNANCE = "governance"


# ── Floor requirements per truth-class ─────────────────────────────────────
# Which floors must be satisfied before a memory of this class is written.

_TRUTH_FLOORS_REQUIRED: dict[TruthClass, frozenset[str]] = {
    TruthClass.OBSERVED: frozenset({"L01", "L02", "L12"}),
    TruthClass.CLAIMED: frozenset({"L01", "L02", "L11", "L12"}),
    TruthClass.DERIVED: frozenset({"L01", "L02", "L04", "L12"}),
    TruthClass.APPROVED: frozenset({"L01", "L02", "L11", "L13"}),  # human ack
    TruthClass.SEALED: frozenset({"L01", "L02", "L09", "L11", "L13"}),
    TruthClass.CONTESTED: frozenset({"L01", "L02", "L04", "L09", "L12"}),
    TruthClass.DEPRECATED: frozenset({"L01", "L04", "L11"}),
}


def floors_required(truth: TruthClass) -> frozenset[str]:
    """Return the floor codes that must be satisfied for writes of this class."""
    return _TRUTH_FLOORS_REQUIRED.get(truth, frozenset({"L01", "L02"}))


# ── Convenience type aliases ───────────────────────────────────────────────

TruthClassName = Literal[
    "observed",
    "claimed",
    "derived",
    "approved",
    "sealed",
    "contested",
    "deprecated",
]

MemoryClassName = Literal[
    "working",
    "session",
    "episodic",
    "semantic",
    "procedural",
    "governance",
]

TierCode = Literal["L1", "L2", "L3", "L4", "L5", "L6"]


__all__ = [
    "TruthClass",
    "MemoryClass",
    "TruthClassName",
    "MemoryClassName",
    "TierCode",
    # Functions
    "tier_allowed",
    "allowed_tiers",
    "default_ttl_hours",
    "default_recall_eligible",
    "can_transition",
    "legal_next",
    "floors_required",
]
