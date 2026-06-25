"""
arifosmcp/core/decision_contract.py — Decision Fabric shared type

The anti-chaos anchor. One contract feeds:
  - conflict_resolver (#422)
  - latency_budget (#423)
  - vault_receipt (#421)

Design invariant: If you implement separately → chaos.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any


# ── Decision Class (latency budget assignment) ───────────────────


class DecisionClass(str, Enum):
    """
    Not all decisions are equal.
    Some must be instant, some can afford deep reasoning.
    """
    C0_AUTO = "C0_AUTO"          # No judge needed — rule engine
    C1_FAST = "C1_FAST"          # Cached or heuristic
    C2_STANDARD = "C2_STANDARD"  # Single-pass reasoning
    C3_DEEP = "C3_DEEP"          # Multi-stage validation
    C4_SOVEREIGN = "C4_SOVEREIGN" # Requires F13 / human


# ── Verdict Class (constitutional outcome) ───────────────────────


class VerdictClass(str, Enum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"
    PARTIAL = "PARTIAL"
    PROCEED = "PROCEED"
    UNKNOWN = "UNKNOWN"


# ── Authority Class (execution authority) ────────────────────────


class AuthorityClass(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    REASON = "REASON"
    EXECUTE = "EXECUTE"
    SOVEREIGN = "SOVEREIGN"


# ── Risk Class ───────────────────────────────────────────────────


class RiskClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ATOMIC = "atomic"


# ── Reversibility Class ─────────────────────────────────────────


class ReversibilityClass(str, Enum):
    FULL = "FULL"          # Can be undone completely
    PARTIAL = "PARTIAL"    # Can be undone with cost
    NONE = "NONE"          # Cannot be undone → F13 required


# ── Organ Type ───────────────────────────────────────────────────


class OrganType(str, Enum):
    CLERK = "clerk"
    GEOX = "geox"
    WEALTH = "wealth"
    WELL = "well"
    AAA = "aaa"
    A_FORGE = "a-forge"
    ARIFOS = "arifos"
    HUMAN = "human"


# ── Decision Contract ────────────────────────────────────────────


@dataclass(frozen=True)
class DecisionContract:
    """
    The shared contract for the Decision Fabric.
    One input → feeds resolver, judge, and receipt.

    Frozen (immutable) — once created, cannot be mutated.
    All fields are hashable for cache keys.
    """

    # ── Identity ──────────────────────────────────────────────────
    contract_id: str             # UUIDv7 or deterministic hash
    session_id: str              # Which session this belongs to
    actor_id: str                # Who initiated this decision
    organ_id: str                # Which organ is primary
    tool_name: str               # Which MCP tool generated this

    # ── Classification ────────────────────────────────────────────
    action_class: str            # OBSERVE | REASON | DRAFT | MUTATE | EXTERNAL | ATOMIC
    decision_class: str          # C0_AUTO | C1_FAST | C2_STANDARD | C3_DEEP | C4_SOVEREIGN
    risk_class: str              # low | medium | high | atomic
    reversibility_class: str     # FULL | PARTIAL | NONE

    # ── Intent ────────────────────────────────────────────────────
    intent_summary: str          # Human-readable summary (for receipts)
    intent_hash: str             # SHA256 of full intent payload

    # ── Context ───────────────────────────────────────────────────
    context_hash: str            # SHA256 of frozen input envelope
    conflict_domain: str         # earth | wealth | governance | health | law | system

    # ── State ─────────────────────────────────────────────────────
    is_irreversible: bool        # True → always escalate to 888_HOLD
    has_cached_verdict: bool     # True → can use fast path

    def to_dict(self) -> dict[str, Any]:
        """Canonical dict for hashing and serialization."""
        return {
            "contract_id": self.contract_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "organ_id": self.organ_id,
            "tool_name": self.tool_name,
            "action_class": self.action_class,
            "decision_class": self.decision_class,
            "risk_class": self.risk_class,
            "reversibility_class": self.reversibility_class,
            "intent_summary": self.intent_summary,
            "intent_hash": self.intent_hash,
            "context_hash": self.context_hash,
            "conflict_domain": self.conflict_domain,
            "is_irreversible": self.is_irreversible,
            "has_cached_verdict": self.has_cached_verdict,
        }

    def compute_context_signature(self) -> str:
        """
        Cache key for judge decisions.
        sha256(input + context_signature) — reuse for repeated decisions.
        """
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


# ── Conflict Envelope ────────────────────────────────────────────


@dataclass
class ConflictEnvelope:
    """
    A conflict between two organ conclusions.
    Fed into the resolver (#422).
    """
    conflict_id: str
    organ_a: str
    verdict_a: str
    organ_b: str
    verdict_b: str
    conflict_domain: str
    is_irreversible: bool = False


# ── Resolution Result ────────────────────────────────────────────


@dataclass(frozen=True)
class ResolutionResult:
    """Immutable result of conflict resolution."""
    winner_organ: str
    winner_verdict: str
    resolution_method: str       # dominance | authority | escalate
    reason: str
    requires_888_hold: bool
    latency_us: int              # microseconds — for latency budget tracking


# ── Judge Result ─────────────────────────────────────────────────


@dataclass(frozen=True)
class JudgeResult:
    """Immutable result of a judge decision."""
    verdict: str                 # VerdictClass value
    decision_class: str          # Which class was used
    latency_ms: float            # Actual latency
    within_budget: bool          # Did it stay within budget?
    reason: str                  # Why this verdict
    resolution: ResolutionResult | None = None  # If conflict was resolved


# ── Helpers ──────────────────────────────────────────────────────


# ── Decision Class Assignment (Rule-based Mapping) ────────────────

RISK_CLASS_MAP: dict[tuple[str, str], str] = {
    ("OBSERVE", "low"): DecisionClass.C0_AUTO.value,
    ("OBSERVE", "medium"): DecisionClass.C0_AUTO.value,
    ("REASON", "low"): DecisionClass.C1_FAST.value,
    ("REASON", "medium"): DecisionClass.C2_STANDARD.value,
    ("DRAFT", "low"): DecisionClass.C1_FAST.value,
    ("DRAFT", "medium"): DecisionClass.C2_STANDARD.value,
    ("DRAFT", "high"): DecisionClass.C3_DEEP.value,
    ("MUTATE", "low"): DecisionClass.C2_STANDARD.value,
    ("MUTATE", "medium"): DecisionClass.C2_STANDARD.value,
    ("MUTATE", "high"): DecisionClass.C3_DEEP.value,
    ("EXTERNAL", "medium"): DecisionClass.C3_DEEP.value,
    ("EXTERNAL", "high"): DecisionClass.C3_DEEP.value,
    ("ATOMIC", "high"): DecisionClass.C4_SOVEREIGN.value,
    ("ATOMIC", "atomic"): DecisionClass.C4_SOVEREIGN.value,
}

DEFAULT_DECISION_CLASS = DecisionClass.C3_DEEP.value  # conservative fallback


def classify_decision(
    action_class: str,
    risk_class: str,
    is_irreversible: bool,
    has_cached_verdict: bool,
) -> str:
    """
    Assign decision class based on action properties.
    No LLM — pure rule lookup.
    Returns DecisionClass value string.
    """
    # Irreversible → always sovereign
    if is_irreversible:
        return DecisionClass.C4_SOVEREIGN.value

    # Cached → fast path
    if has_cached_verdict and risk_class in ("low", "medium"):
        return DecisionClass.C1_FAST.value

    return RISK_CLASS_MAP.get((action_class, risk_class), DEFAULT_DECISION_CLASS)
