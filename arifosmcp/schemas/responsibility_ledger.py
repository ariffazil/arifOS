"""
VAULT999 Responsibility Ledger — Chapter 6 Upgrade P3
═══════════════════════════════════════════════════════

The vault must record not only what happened, but who can answer for it.

Every consequential seal MUST include:
  - What changed
  - Who authorized
  - Who ratified
  - Evidence used
  - Uncertainty left
  - People affected
  - Rollback plan
  - Repair plan
  - Moral owner

The question is not only "what happened?" — it is:
"Who can answer for what happened?"

This is Chapter 6 in runtime form.

DITEMPA BUKAN DIBERI — Responsibility is the human signature on the machine's action.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSIBILITY CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


class MoralOwner(StrEnum):
    """Who bears the moral weight of this action."""

    SOVEREIGN = "sovereign"  # Arif personally
    DELEGATE = "delegate"  # Delegated human operator
    INSTITUTION = "institution"  # The federation itself (policy-bound)
    AGENT = "agent"  # Agent acting within scope
    UNASSIGNED = "unassigned"  # No moral owner — this is a problem


class ResponsibilityClass(StrEnum):
    """How consequential is the responsibility for this action."""

    ROUTINE = "routine"  # Low-consequence, reversible
    SIGNIFICANT = "significant"  # Moderate consequence, needs review
    CONSEQUENTIAL = "consequential"  # High consequence, needs moral owner
    IRREVERSIBLE = "irreversible"  # Cannot be undone, requires sovereign
    HISTORIC = "historic"  # Changes the federation's trajectory


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSIBILITY RECEIPT
# ═══════════════════════════════════════════════════════════════════════════════


class ResponsibilityReceipt(BaseModel):
    """
    Attached to every VAULT999 seal for consequential actions.

    This turns the vault from a simple audit log into a responsibility ledger.
    Every seal now answers: who can be held accountable for this action?

    The moral_owner is the person or entity who carries the weight of the decision.
    If moral_owner is UNASSIGNED, the seal should be treated as HOLD.
    """

    # ── Identity ────────────────────────────────────────────────────────
    receipt_id: str = Field(
        default_factory=lambda: f"RESP-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        description="Unique responsibility receipt identifier",
    )
    seal_id: str = Field(description="VAULT999 seal this receipt accompanies")
    session_id: str = Field(description="Governing session")
    actor_id: str = Field(description="Who triggered the action")

    # ── What happened ───────────────────────────────────────────────────
    what_changed: str = Field(description="Human-readable description of what changed")
    domain: str = Field(default="arifOS", description="Which organ domain")

    # ── Authority chain ─────────────────────────────────────────────────
    who_authorized: str = Field(description="Who authorized the action (may differ from actor)")
    who_ratified: str = Field(description="Who ratified the seal")
    moral_owner: MoralOwner = Field(
        default=MoralOwner.UNASSIGNED,
        description="Who carries the moral weight of this decision",
    )
    responsibility_class: ResponsibilityClass = Field(
        default=ResponsibilityClass.ROUTINE,
        description="How consequential this action is",
    )
    authority_chain: list[str] = Field(
        default_factory=list,
        description="Full authority chain: [delegator → delegatee → ... → ratifier]",
    )

    # ── Evidence ────────────────────────────────────────────────────────
    evidence_used: list[str] = Field(
        default_factory=list,
        description="Evidence IDs that informed this decision",
    )
    uncertainty_left: str = Field(
        default="",
        description="What uncertainty was not resolved before acting",
    )
    confidence_at_seal: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence level when the seal was written",
    )

    # ── Impact ──────────────────────────────────────────────────────────
    people_affected: list[str] = Field(
        default_factory=list,
        description="Who is affected by this action (roles, not names)",
    )
    blast_radius_actual: str = Field(
        default="local",
        description="Actual blast radius: local | account | org | public | financial | infra",
    )

    # ── Recovery ────────────────────────────────────────────────────────
    rollback_plan: str = Field(
        default="",
        description="How to reverse this action if it was wrong",
    )
    repair_plan: str = Field(
        default="",
        description="How to repair harm caused by this action",
    )
    reversibility_assessment: str = Field(
        default="unknown",
        description="Honest assessment: reversible | partial | irreversible",
    )
    recovery_timeline_hours: int = Field(
        default=0,
        description="Estimated hours to fully recover",
    )

    # ── Accountability ──────────────────────────────────────────────────
    can_be_contested: bool = Field(
        default=True,
        description="Can this seal be appealed?",
    )
    contest_deadline_iso: str | None = Field(
        default=None,
        description="Deadline for contesting this seal (ISO 8601)",
    )
    review_required: bool = Field(
        default=False,
        description="Does this seal require periodic review?",
    )
    review_interval_days: int = Field(
        default=0,
        description="Days between periodic reviews (0 = no review needed)",
    )

    # ── Metadata ────────────────────────────────────────────────────────
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When this receipt was created",
    )
    tags: list[str] = Field(default_factory=list, description="Classification tags")

    def is_accountable(self) -> bool:
        """True if someone can be held accountable for this action."""
        return self.moral_owner != MoralOwner.UNASSIGNED

    def is_safe(self) -> bool:
        """True if this action has a recovery path."""
        return bool(self.rollback_plan) and bool(self.repair_plan)

    def to_log_dict(self) -> dict[str, Any]:
        """Serialize for audit (no sensitive content)."""
        return {
            "receipt_id": self.receipt_id,
            "seal_id": self.seal_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "who_authorized": self.who_authorized,
            "who_ratified": self.who_ratified,
            "moral_owner": self.moral_owner.value,
            "responsibility_class": self.responsibility_class.value,
            "evidence_count": len(self.evidence_used),
            "people_affected_count": len(self.people_affected),
            "can_be_contested": self.can_be_contested,
            "is_accountable": self.is_accountable(),
            "is_safe": self.is_safe(),
            "created_at": self.created_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT999 MIGRATION SQL — Responsibility Columns
# ═══════════════════════════════════════════════════════════════════════════════

# This migration adds responsibility columns to vault_sealed_events.
# Run via Supabase SQL Editor or psql.

VAULT999_RESPONSIBILITY_MIGRATION = """
-- Chapter 6 P3: VAULT999 Responsibility Ledger Migration
-- Adds moral ownership, recovery, and accountability columns to vault_sealed_events

ALTER TABLE public.vault_sealed_events
ADD COLUMN IF NOT EXISTS moral_owner TEXT DEFAULT 'unassigned',
ADD COLUMN IF NOT EXISTS responsibility_class TEXT DEFAULT 'routine',
ADD COLUMN IF NOT EXISTS who_authorized TEXT,
ADD COLUMN IF NOT EXISTS who_ratified TEXT,
ADD COLUMN IF NOT EXISTS authority_chain JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS evidence_ids JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS uncertainty_left TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS confidence_at_seal REAL DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS people_affected JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS rollback_plan TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS repair_plan TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS reversibility_assessment TEXT DEFAULT 'unknown',
ADD COLUMN IF NOT EXISTS recovery_timeline_hours INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS can_be_contested BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS contest_deadline TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS review_required BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS review_interval_days INTEGER DEFAULT 0;

-- Backfill existing seals with conservative defaults
-- Existing seals without moral_owner inherit 'institution' as default
UPDATE public.vault_sealed_events
SET moral_owner = 'institution'
WHERE moral_owner IS NULL OR moral_owner = 'unassigned';

COMMENT ON COLUMN public.vault_sealed_events.moral_owner IS
'Chapter 6 P3: Who carries the moral weight of this decision (sovereign/delegate/institution/agent/unassigned)';
COMMENT ON COLUMN public.vault_sealed_events.responsibility_class IS
'Chapter 6 P3: How consequential this action is (routine/significant/consequential/irreversible/historic)';
COMMENT ON COLUMN public.vault_sealed_events.rollback_plan IS
'Chapter 6 P3: How to reverse this action if it was wrong';
COMMENT ON COLUMN public.vault_sealed_events.repair_plan IS
'Chapter 6 P3: How to repair harm caused by this action';
"""


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY — build a responsibility receipt
# ═══════════════════════════════════════════════════════════════════════════════


def build_responsibility_receipt(
    seal_id: str,
    session_id: str,
    actor_id: str,
    what_changed: str,
    who_authorized: str,
    who_ratified: str,
    moral_owner: MoralOwner = MoralOwner.UNASSIGNED,
    responsibility_class: ResponsibilityClass = ResponsibilityClass.ROUTINE,
    evidence_used: list[str] | None = None,
    uncertainty_left: str = "",
    confidence: float = 0.5,
    people_affected: list[str] | None = None,
    rollback_plan: str = "",
    repair_plan: str = "",
    reversibility: str = "unknown",
    recovery_hours: int = 0,
    authority_chain: list[str] | None = None,
    contest_deadline: str | None = None,
) -> ResponsibilityReceipt:
    """
    Build a ResponsibilityReceipt for a VAULT999 seal.

    Use this factory for EVERY consequential seal. A seal without
    responsibility is a seal without accountability.
    """
    from datetime import timedelta

    # Default contest deadline: 30 days from now
    if contest_deadline is None and moral_owner != MoralOwner.UNASSIGNED:
        contest_deadline = (datetime.now(UTC) + timedelta(days=30)).isoformat()

    return ResponsibilityReceipt(
        seal_id=seal_id,
        session_id=session_id,
        actor_id=actor_id,
        what_changed=what_changed,
        who_authorized=who_authorized,
        who_ratified=who_ratified,
        moral_owner=moral_owner,
        responsibility_class=responsibility_class,
        authority_chain=authority_chain or [],
        evidence_used=evidence_used or [],
        uncertainty_left=uncertainty_left,
        confidence_at_seal=confidence,
        people_affected=people_affected or [],
        rollback_plan=rollback_plan,
        repair_plan=repair_plan,
        reversibility_assessment=reversibility,
        recovery_timeline_hours=recovery_hours,
        can_be_contested=True,
        contest_deadline_iso=contest_deadline,
        review_required=responsibility_class
        in (
            ResponsibilityClass.CONSEQUENTIAL,
            ResponsibilityClass.IRREVERSIBLE,
            ResponsibilityClass.HISTORIC,
        ),
        review_interval_days=90
        if responsibility_class
        in (ResponsibilityClass.CONSEQUENTIAL, ResponsibilityClass.IRREVERSIBLE)
        else 0,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "MoralOwner",
    "ResponsibilityClass",
    # Schema
    "ResponsibilityReceipt",
    # Migration
    "VAULT999_RESPONSIBILITY_MIGRATION",
    # Factory
    "build_responsibility_receipt",
]
