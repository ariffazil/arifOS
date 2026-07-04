"""
arifOS Sovereign Fabric — Agent Authorization Envelope (Wajib Layer 6)
═══════════════════════════════════════════════════════════════════════

Every MCP tool call MUST carry an AuthorizationEnvelope.
This is the governed intent packet — it travels with every action.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────


class ActionClass(str, Enum):
    """What kind of action is being requested."""

    OBSERVE = "observe"  # Read-only, no side effects
    REASON = "reason"  # Think, plan, analyze (no mutation)
    SUGGEST = "suggest"  # Propose a change (advisory only)
    DRAFT = "draft"  # Write to buffer/staging (reversible)
    MUTATE = "mutate"  # Change state (requires lease)
    EXECUTE = "execute"  # Run code/deploy (requires lease + seal)
    SEAL = "seal"  # Write to VAULT999 (irreversible)
    DELEGATE = "delegate"  # Forward to another agent/organ


class Reversibility(str, Enum):
    """Can this action be undone?"""

    FULL = "full"  # Git revert, delete temp file
    PARTIAL = "partial"  # Revertible with data loss
    NONE = "none"  # Irreversible (VAULT999 seal, spend)
    UNKNOWN = "unknown"  # Not yet classified


class BlastRadius(str, Enum):
    """How far does this action's effect reach?"""

    NONE = "none"  # Pure read, no effect
    LOCAL = "local"  # Single file, single tool
    ORGAN = "organ"  # One organ (e.g., GEOX only)
    FEDERATION = "federation"  # Cross-organ
    EXTERNAL = "external"  # Outside the federation (API call, deploy)
    IRREVERSIBLE = "irreversible"  # Cannot be undone


class EvidenceFloor(str, Enum):
    """Minimum evidence quality required for this action."""

    NONE = "none"  # No evidence needed (read-only)
    INFERRED = "inferred"  # Reasonable inference from context
    OBSERVED = "observed"  # Direct sensor/measurement
    VERIFIED = "verified"  # Cross-checked by multiple sources
    GROUND_TRUTH = "ground_truth"  # Sealed in VAULT999


class Verdict(str, Enum):
    """Constitutional verdict from the policy engine."""

    PROCEED = "PROCEED"  # All gates passed
    HOLD = "HOLD"  # Needs review or additional evidence
    SABAR = "SABAR"  # Wait (timing or state issue)
    VOID = "VOID"  # Constitutionally forbidden
    DRY_RUN = "DRY_RUN"  # Execute in observation mode only


# ── The Envelope ───────────────────────────────────────────────────────


class AuthorizationEnvelope(BaseModel):
    """
    The governed intent packet. Every MCP tool call carries this.

    This is NOT optional. This is the membrane between
    "agent wants to do something" and "agent is allowed to do it."
    """

    # Identity
    envelope_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str  # Who is acting (e.g., "opencode-333-agi")
    principal_id: Optional[str] = None  # Delegating principal (if any)
    session_id: str  # Constitutional session from arif_init

    # Intent
    tool_name: str  # Which tool is being called
    action_class: ActionClass  # What kind of action
    intent_hash: str = ""  # SHA-256 of the action description
    intent_description: str = ""  # Human-readable intent

    # Risk Classification
    reversibility: Reversibility = Reversibility.UNKNOWN
    blast_radius: BlastRadius = BlastRadius.NONE
    evidence_floor: EvidenceFloor = EvidenceFloor.NONE

    # Evidence
    evidence_refs: list[str] = Field(default_factory=list)  # VAULT999 entry IDs or URLs
    confidence: float = 0.0  # 0.0-1.0, capped at 0.90 (F7)

    # Governance
    requires_human_ack: bool = False  # F13 — needs Arif's approval
    human_ack_token: Optional[str] = None  # F13 — approval token if granted
    lease_id: Optional[str] = None  # A-FORGE lease if executing
    constitutional_chain_id: Optional[str] = None  # cc_id from prior judge SEAL

    # Trace
    trace_id: str = Field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:12]}")
    span_id: str = Field(default_factory=lambda: f"span-{uuid.uuid4().hex[:8]}")
    parent_span_id: Optional[str] = None  # For nested calls
    timestamp: float = Field(default_factory=time.time)

    # Signature (placeholder — mTLS/DPoP will populate this)
    signature: Optional[str] = None  # Cryptographic proof of envelope integrity
    signed_by: Optional[str] = None  # Key ID that signed this envelope

    def compute_intent_hash(self) -> str:
        """Compute SHA-256 of the intent for tamper detection."""
        payload = f"{self.actor_id}:{self.tool_name}:{self.action_class}:{self.intent_description}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def seal(self) -> AuthorizationEnvelope:
        """Seal the envelope — compute intent hash and mark as sealed."""
        self.intent_hash = self.compute_intent_hash()
        return self

    def is_constitutional(self) -> bool:
        """Quick check: does this envelope pass basic constitutional gates?"""
        if self.action_class in (ActionClass.SEAL, ActionClass.EXECUTE):
            if self.reversibility == Reversibility.NONE and not self.human_ack_token:
                return False  # F1: Irreversible requires human ack
        if self.confidence > 0.90:
            return False  # F7: Humility cap
        if self.action_class == ActionClass.DELEGATE and not self.lease_id:
            return False  # Execution requires lease
        return True

    def to_audit_dict(self) -> dict[str, Any]:
        """Serialize for VAULT999 receipt."""
        return {
            "envelope_id": self.envelope_id,
            "actor_id": self.actor_id,
            "tool_name": self.tool_name,
            "action_class": self.action_class.value,
            "reversibility": self.reversibility.value,
            "blast_radius": self.blast_radius.value,
            "evidence_floor": self.evidence_floor.value,
            "confidence": self.confidence,
            "requires_human_ack": self.requires_human_ack,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "timestamp": self.timestamp,
            "intent_hash": self.intent_hash,
            "signed_by": self.signed_by,
        }


# ── Factory ────────────────────────────────────────────────────────────


def create_envelope(
    actor_id: str,
    session_id: str,
    tool_name: str,
    action_class: ActionClass,
    intent_description: str = "",
    reversibility: Reversibility = Reversibility.UNKNOWN,
    blast_radius: BlastRadius = BlastRadius.NONE,
    evidence_floor: EvidenceFloor = EvidenceFloor.NONE,
    confidence: float = 0.0,
    requires_human_ack: bool = False,
    lease_id: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> AuthorizationEnvelope:
    """Create and seal an AuthorizationEnvelope."""
    env = AuthorizationEnvelope(
        actor_id=actor_id,
        session_id=session_id,
        tool_name=tool_name,
        action_class=action_class,
        intent_description=intent_description,
        reversibility=reversibility,
        blast_radius=blast_radius,
        evidence_floor=evidence_floor,
        confidence=min(confidence, 0.90),  # F7 cap
        requires_human_ack=requires_human_ack,
        lease_id=lease_id,
        trace_id=trace_id or f"trc-{uuid.uuid4().hex[:12]}",
    )
    return env.seal()


# ── Action Class Auto-Classifier ───────────────────────────────────────

TOOL_ACTION_MAP: dict[str, ActionClass] = {
    # Observe
    "arif_observe": ActionClass.OBSERVE,
    "arif_triage": ActionClass.OBSERVE,
    "arif_floor_status": ActionClass.OBSERVE,
    "arif_organ_attest": ActionClass.OBSERVE,
    "arif_organ_attest_all": ActionClass.OBSERVE,
    "arif_retrieve_tools": ActionClass.OBSERVE,
    "arif_resolve_tool": ActionClass.OBSERVE,
    "arif_canary": ActionClass.OBSERVE,
    "arif_vault_query": ActionClass.OBSERVE,
    "arif_heartbeat": ActionClass.OBSERVE,
    "arif_wiki_search": ActionClass.OBSERVE,
    "arif_wiki_map": ActionClass.OBSERVE,
    "arif_get_affordance": ActionClass.OBSERVE,
    "arif_stack_health_probe": ActionClass.OBSERVE,
    "arif_conformance_report": ActionClass.OBSERVE,
    "arif_scan_local_instructions": ActionClass.OBSERVE,
    "arif_session_budget": ActionClass.OBSERVE,
    # Reason
    "arif_think": ActionClass.REASON,
    "arif_wiki_ask": ActionClass.REASON,
    # Suggest
    "arif_route": ActionClass.SUGGEST,
    "arif_compose": ActionClass.SUGGEST,
    # Mutate
    "arif_init": ActionClass.MUTATE,
    "arif_wiki_ingest": ActionClass.MUTATE,
    "arif_lease_issue": ActionClass.MUTATE,
    "arif_lease_revoke": ActionClass.MUTATE,
    # Execute
    "arif_act": ActionClass.EXECUTE,
    # Seal
    "arif_seal": ActionClass.SEAL,
    "arif_judge": ActionClass.SEAL,  # Judge writes to audit trail
}


def classify_action(tool_name: str) -> ActionClass:
    """Auto-classify a tool call by action class."""
    return TOOL_ACTION_MAP.get(tool_name, ActionClass.OBSERVE)
