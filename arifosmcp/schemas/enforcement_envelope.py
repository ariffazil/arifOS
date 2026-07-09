"""
Enforcement Envelope — CANONICAL CROSS-REPO CONTRACT (v1.0.0)
═══════════════════════════════════════════════════════════════

FORGED 2026-07-03 — AOB P0: The single enforcement envelope all organs
MUST return on every public verb. This is the machine-readable contract
that makes arifOS benchmark-operable.

Six canonical sections (kernel → organ → authority → state → risk → audit)
plus mandatory trace block for benchmark compatibility.

UNIFIED VERDICT (canonical across ALL organs):
  SEAL  — proceed, all gates satisfied
  HOLD  — blocked, requires resolution (typed reason_code required)
  SABAR — proceed with caution, warnings active
  VOID  — permanently blocked, constitutional breach

verdict_code: machine-readable string like "OK", "HOLD.AUTH_REQUIRED",
  "HOLD.WITNESS_INSUFFICIENT", "SABAR.NEEDS_MORE_EVIDENCE", etc.

session_mode:
  ephemeral_eval   — read-only, no identity bind, auto-HOLD on mutate
  persistent_bound — full governed path, identity required

DITEMPA BUKAN DIBERI — Forged as the constitutional contract.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL VERDICT — single source of truth across ALL federation organs
# ═══════════════════════════════════════════════════════════════════════════════


from arifosmcp.models.verdicts import Verdict as CanonicalVerdict

# CanonicalVerdict is now imported from models/verdicts.
# Cross-repo mapping (legacy → canonical):
#   GEOX QUALIFY → Verdict.SABAR
#   A-FORGE CAUTION → Verdict.SABAR
#   arifOS PARADOX_HOLD → Verdict.HOLD (with VerdictState.HOLD_PARADOX)


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT CODE — typed reason strings for machine consumption
# ═══════════════════════════════════════════════════════════════════════════════


class VerdictReason(StrEnum):
    """Typed reason codes for every verdict. Machines read these; humans read reason_text."""

    # SEAL variants
    OK = "OK"
    OK_CONDITIONAL = "OK.CONDITIONAL"

    # HOLD variants
    HOLD_AUTH_REQUIRED = "HOLD.AUTH_REQUIRED"
    HOLD_WITNESS_INSUFFICIENT = "HOLD.WITNESS_INSUFFICIENT"
    HOLD_MODE3_COLLAPSE = "HOLD.MODE3_COLLAPSE"
    HOLD_FLOOR_VIOLATION = "HOLD.FLOOR_VIOLATION"
    HOLD_IDENTITY_UNVERIFIED = "HOLD.IDENTITY_UNVERIFIED"
    HOLD_PARADOX = "HOLD.PARADOX"
    HOLD_MANUAL_REVIEW = "HOLD.MANUAL_REVIEW"

    # SABAR variants
    SABAR_NEEDS_MORE_EVIDENCE = "SABAR.NEEDS_MORE_EVIDENCE"
    SABAR_LOW_CONFIDENCE = "SABAR.LOW_CONFIDENCE"
    SABAR_WITNESS_DEGRADED = "SABAR.WITNESS_DEGRADED"
    SABAR_STALE_STATE = "SABAR.STALE_STATE"

    # VOID variants
    VOID_FLOOR_VIOLATION = "VOID.FLOOR_VIOLATION"
    VOID_HANTU = "VOID.HANTU"
    VOID_INJECTION = "VOID.INJECTION"
    VOID_IRREVERSIBLE_UNAUTHORIZED = "VOID.IRREVERSIBLE_UNAUTHORIZED"


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MODE
# ═══════════════════════════════════════════════════════════════════════════════


class SessionMode(StrEnum):
    """Session binding mode — controls what paths are available."""

    EPHEMERAL_EVAL = "ephemeral_eval"  # read-only benchmark, no identity
    PERSISTENT_BOUND = "persistent_bound"  # full governed, identity required


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHORITY SCOPE
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityScope(StrEnum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    SUGGEST_ONLY = "SUGGEST_ONLY"
    EXECUTE_BOUND = "EXECUTE_BOUND"


# ═══════════════════════════════════════════════════════════════════════════════
# WITNESS BLOCK
# ═══════════════════════════════════════════════════════════════════════════════


class WitnessBlock(BaseModel):
    """Live witness summary — F3 TRI-WITNESS enforcement."""

    active_count: int = Field(default=0, ge=0, le=5, description="Active witness types (0-5)")
    missing_types: list[str] = Field(
        default_factory=list, description="Which witness types are absent"
    )
    mode3_collapse: bool = Field(
        default=False, description="AI-judging-AI without Earth measurement"
    )
    diversity_level: str = Field(
        default="VOID",
        description="FULL_WITNESS | STRONG | MINIMAL | DEGRADED | COLLAPSED | VOID",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TRACE BLOCK — benchmark compatibility
# ═══════════════════════════════════════════════════════════════════════════════


class TraceBlock(BaseModel):
    """Correlated trace identifiers for benchmark runs."""

    run_id: str = Field(default_factory=lambda: f"run-{uuid4().hex[:8]}")
    scenario_id: str | None = None
    benchmark_id: str | None = None
    tool_registry_version: str = Field(default="1.0.0")
    otel_trace_id: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# ENFORCEMENT ENVELOPE — the canonical contract
# ═══════════════════════════════════════════════════════════════════════════════


class EnforcementEnvelope(BaseModel):
    """The machine-readable enforcement envelope returned by every public verb.

    This is the contract that makes arifOS a benchmark-operable substrate.
    Every organ MUST stamp this (or a compatible superset) on all tool returns.
    """

    # ── Kernel identity ──
    kernel_epoch: str = Field(default="2026-07-03", description="Constitutional epoch")
    public_surface_version: str = Field(default="7", description="Number of public verbs")

    # ── Verb context ──
    verb: str = Field(default="arif_init", description="The tool being called")
    init_mode: str = Field(default="light", description="light | full | ping")
    session_mode: SessionMode = Field(
        default=SessionMode.PERSISTENT_BOUND,
        description="Ephemeral eval or persistent governed",
    )

    # ── Authority ──
    authority_scope: AuthorityScope = Field(
        default=AuthorityScope.OBSERVE_ONLY,
        description="What this session is authorized to do",
    )
    actor_bound: bool = Field(default=False, description="Is a verified actor bound?")
    actor_id: str | None = Field(default=None)
    session_id: str | None = Field(default=None)

    # ── Verdict ──
    verdict: CanonicalVerdict = Field(default=CanonicalVerdict.SEAL)
    verdict_code: VerdictReason = Field(default=VerdictReason.OK)
    reason_text: str = Field(default="", description="Human-readable explanation")
    action_class: str = Field(
        default="OBSERVE",
        description="OBSERVE | SUGGEST | SIMULATE | DRAFT | QUEUE | EXECUTE_REVERSIBLE | EXECUTE_HIGH_IMPACT | IRREVERSIBLE",
    )

    # ── Witness (F3) ──
    witness: WitnessBlock = Field(default_factory=WitnessBlock)

    # ── Trace ──
    trace: TraceBlock = Field(default_factory=TraceBlock)

    # ── Navigation ──
    allowed_next_verbs: list[str] = Field(default_factory=list)
    constitution_hash: str = Field(default="")
    detail_ref: str = Field(default="")

    # ── Metadata ──
    stamp_utc: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When this envelope was stamped",
    )
    motto: str = Field(default="DITEMPA BUKAN DIBERI")


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FACTORIES
# ═══════════════════════════════════════════════════════════════════════════════


def make_ephemeral_envelope(
    verb: str = "arif_init",
    session_id: str | None = None,
    allowed_next: list[str] | None = None,
) -> EnforcementEnvelope:
    """Factory for ephemeral_eval sessions — OBSERVE_ONLY, no identity."""
    return EnforcementEnvelope(
        verb=verb,
        init_mode="light",
        session_mode=SessionMode.EPHEMERAL_EVAL,
        authority_scope=AuthorityScope.OBSERVE_ONLY,
        actor_bound=False,
        actor_id=None,
        session_id=session_id,
        verdict=CanonicalVerdict.SEAL,
        verdict_code=VerdictReason.OK,
        action_class="OBSERVE",
        allowed_next_verbs=allowed_next or ["arif_observe", "arif_think", "arif_route"],
        witness=WitnessBlock(),
        trace=TraceBlock(),
    )


def make_persistent_envelope(
    verb: str = "arif_init",
    actor_id: str | None = None,
    session_id: str | None = None,
    authority_scope: AuthorityScope = AuthorityScope.EXECUTE_BOUND,
    allowed_next: list[str] | None = None,
) -> EnforcementEnvelope:
    """Factory for persistent_bound sessions — full governed path."""
    return EnforcementEnvelope(
        verb=verb,
        init_mode="full",
        session_mode=SessionMode.PERSISTENT_BOUND,
        authority_scope=authority_scope,
        actor_bound=actor_id is not None,
        actor_id=actor_id,
        session_id=session_id,
        verdict=CanonicalVerdict.SEAL,
        verdict_code=VerdictReason.OK,
        action_class="OBSERVE",
        allowed_next_verbs=allowed_next
        or ["arif_observe", "arif_think", "arif_route", "arif_judge", "arif_forge", "arif_seal"],
        witness=WitnessBlock(),
        trace=TraceBlock(),
    )


def make_hold_envelope(
    verb: str,
    verdict_code: VerdictReason,
    reason_text: str,
    action_class: str = "OBSERVE",
) -> EnforcementEnvelope:
    """Factory for HOLD responses."""
    return EnforcementEnvelope(
        verb=verb,
        verdict=CanonicalVerdict.HOLD,
        verdict_code=verdict_code,
        reason_text=reason_text,
        action_class=action_class,
        allowed_next_verbs=[],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY — normalize any organ's verdict to canonical
# ═══════════════════════════════════════════════════════════════════════════════


LEGACY_VERDICT_MAP: dict[str, CanonicalVerdict] = {
    # GEOX
    "QUALIFY": CanonicalVerdict.SABAR,
    # A-FORGE
    "CAUTION": CanonicalVerdict.SABAR,
    "PASS": CanonicalVerdict.SEAL,
    # arifOS legacy
    "PARADOX_HOLD": CanonicalVerdict.HOLD,
    "REJECT": CanonicalVerdict.VOID,
    "OBSERVE_ONLY": CanonicalVerdict.SEAL,
    "FULL": CanonicalVerdict.SEAL,
    # AAA
    "PENDING": CanonicalVerdict.SABAR,
}


def normalize_verdict(raw: str) -> CanonicalVerdict:
    """Normalize any organ's verdict string to the canonical enum."""
    upper = raw.upper().strip()
    if upper in {"SEAL", "HOLD", "SABAR", "VOID"}:
        return CanonicalVerdict(upper)
    return LEGACY_VERDICT_MAP.get(upper, CanonicalVerdict.HOLD)
