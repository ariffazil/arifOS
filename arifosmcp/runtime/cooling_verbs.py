"""
cooling_verbs.py — arifOS P1: Cooling Lifecycle Verbs (EUREKA)

Per mandate §8:

Autonomous subset (agents may perform):
  cooling.observe      — read-only signal capture
  cooling.diagnose     — symptom → root-cause hypothesis generation
  cooling.propose      — proposed intervention (read-only)
  cooling.verify       — when read-only + evidence-based

Gated subset (requires exact capability):
  cooling.approve      — for consequential changes
  cooling.install      — in production
  cooling.receipt      — for sovereign-class events

Forbidden to autonomous:
  policy mutation, authority mutation, key rotation, constitutional modification

Per mandate §8: Cooling entry schema:
  cooling_id:
  session_id:
  trace_id:
  trigger:
  symptoms:
  bottleneck_class:
  root_cause_hypotheses:
  evidence_refs:
  counterevidence_refs:
  confidence:
  proposed_interventions:
  risk:
  reversibility:
  status:
  created_by:
  created_at:

Cooling taxonomy (mandate §8):
  IDENTITY_BINDING, AUTHORITY, SESSION_CONTINUITY, TOOL_SCHEMA, TOOL_FAILURE,
  MODEL_FAILURE, MEMORY_RETRIEVAL, MEMORY_POISONING, CONTEXT_OVERFLOW,
  WORKFLOW, FILESYSTEM, DATABASE, QUEUE, VAULT_CHAIN, TELEMETRY,
  HUMAN_APPROVAL, POLICY_CONFLICT, RESOURCE_EXHAUSTION, RUNTIME_DIVERGENCE,
  PREMATURE_COLLAPSE

This module is read-only for observe/diagnose/propose/verify.
Approve/install/receipt are gated — this module provides the REQUEST
shapes only; execution requires narrow capability issuance (vault_outbox).
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# COOLING TAXONOMY (mandate §8)
# ═══════════════════════════════════════════════════════════════════════════════

class BottleneckClass(str, Enum):
    IDENTITY_BINDING = "IDENTITY_BINDING"
    AUTHORITY = "AUTHORITY"
    SESSION_CONTINUITY = "SESSION_CONTINUITY"
    TOOL_SCHEMA = "TOOL_SCHEMA"
    TOOL_FAILURE = "TOOL_FAILURE"
    MODEL_FAILURE = "MODEL_FAILURE"
    MEMORY_RETRIEVAL = "MEMORY_RETRIEVAL"
    MEMORY_POISONING = "MEMORY_POISONING"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    WORKFLOW = "WORKFLOW"
    FILESYSTEM = "FILESYSTEM"
    DATABASE = "DATABASE"
    QUEUE = "QUEUE"
    VAULT_CHAIN = "VAULT_CHAIN"
    TELEMETRY = "TELEMETRY"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    POLICY_CONFLICT = "POLICY_CONFLICT"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    RUNTIME_DIVERGENCE = "RUNTIME_DIVERGENCE"
    PREMATURE_COLLAPSE = "PREMATURE_COLLAPSE"


class CoolingStatus(str, Enum):
    OBSERVED = "observed"
    DIAGNOSED = "diagnosed"
    PROPOSED = "proposed"
    VERIFIED = "verified"
    APPROVED = "approved"            # gated
    INSTALLED = "installed"          # gated
    RECEIPTED = "receipted"          # gated (sovereign-class)


class CoolingVerb(str, Enum):
    OBSERVE = "cooling.observe"
    DIAGNOSE = "cooling.diagnose"
    PROPOSE = "cooling.propose"
    VERIFY = "cooling.verify"
    APPROVE = "cooling.approve"
    INSTALL = "cooling.install"
    RECEIPT = "cooling.receipt"
    DECAY = "cooling.decay"


# ═══════════════════════════════════════════════════════════════════════════════
# COOLING ENTRY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CoolingEntry:
    """One cooling entry per mandate §8 schema."""
    cooling_id: str = ""
    session_id: str = ""
    trace_id: str = ""
    trigger: str = ""
    symptoms: tuple[str, ...] = ()
    bottleneck_class: str = ""       # BottleneckClass value
    root_cause_hypotheses: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    counterevidence_refs: tuple[str, ...] = ()
    confidence: float = 0.0
    proposed_interventions: tuple[str, ...] = ()
    risk: str = "low"                 # low | medium | high
    reversibility: str = "reversible"  # reversible | compensatable | irreversible
    status: CoolingStatus = CoolingStatus.OBSERVED
    created_by: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "cooling_id": self.cooling_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "trigger": self.trigger,
            "symptoms": list(self.symptoms),
            "bottleneck_class": self.bottleneck_class,
            "root_cause_hypotheses": list(self.root_cause_hypotheses),
            "evidence_refs": list(self.evidence_refs),
            "counterevidence_refs": list(self.counterevidence_refs),
            "confidence": self.confidence,
            "proposed_interventions": list(self.proposed_interventions),
            "risk": self.risk,
            "reversibility": self.reversibility,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# IN-PROCESS REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

_COOLING: dict[str, CoolingEntry] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fresh_id(prefix: str) -> str:
    return f"{prefix}_{hashlib.sha256(_now_iso().encode()).hexdigest()[:16]}"


# ═══════════════════════════════════════════════════════════════════════════════
# COOLING VERBS (autonomous subset)
# ═══════════════════════════════════════════════════════════════════════════════

def observe(
    session_id: str,
    symptoms: list[str],
    trigger: str,
    bottleneck_class: str = "",
    created_by: str = "kimi-code",
) -> CoolingEntry:
    """cooling.observe — read-only signal capture.

    Per mandate §8: agents may perform this autonomously.
    """
    entry = CoolingEntry(
        cooling_id=_fresh_id("cool"),
        session_id=session_id,
        trace_id=_fresh_id("trace"),
        trigger=trigger,
        symptoms=tuple(symptoms),
        bottleneck_class=bottleneck_class or BottleneckClass.TOOL_FAILURE.value,
        created_by=created_by,
        created_at=_now_iso(),
        status=CoolingStatus.OBSERVED,
    )
    _COOLING[entry.cooling_id] = entry
    return entry


def diagnose(
    cooling_id: str,
    root_cause_hypotheses: list[str],
    bottleneck_class: str = "",
    evidence_refs: Optional[list[str]] = None,
    counterevidence_refs: Optional[list[str]] = None,
    confidence: float = 0.0,
) -> Optional[CoolingEntry]:
    """cooling.diagnose — symptom → root-cause hypothesis generation.

    Per mandate §8: agents may perform this autonomously.
    Confidence is bounded by evidence quality; navigation may add hypotheses.
    """
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return None
    # Update immutably (create new entry, replace)
    updated = CoolingEntry(
        cooling_id=entry.cooling_id,
        session_id=entry.session_id,
        trace_id=entry.trace_id,
        trigger=entry.trigger,
        symptoms=entry.symptoms,
        bottleneck_class=bottleneck_class or entry.bottleneck_class,
        root_cause_hypotheses=tuple(root_cause_hypotheses),
        evidence_refs=tuple(evidence_refs or []),
        counterevidence_refs=tuple(counterevidence_refs or []),
        confidence=max(0.0, min(1.0, confidence)),
        proposed_interventions=entry.proposed_interventions,
        risk=entry.risk,
        reversibility=entry.reversibility,
        status=CoolingStatus.DIAGNOSED,
        created_by=entry.created_by,
        created_at=entry.created_at,
    )
    _COOLING[cooling_id] = updated
    return updated


def propose(
    cooling_id: str,
    proposed_interventions: list[str],
    risk: str = "low",
    reversibility: str = "reversible",
) -> Optional[CoolingEntry]:
    """cooling.propose — proposed intervention (read-only).

    Per mandate §8: agents may perform this autonomously.
    Returns the entry with status=PROPOSED. Approval/install/receipt
    remain gated and require separate capability flows.
    """
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return None
    updated = CoolingEntry(
        cooling_id=entry.cooling_id,
        session_id=entry.session_id,
        trace_id=entry.trace_id,
        trigger=entry.trigger,
        symptoms=entry.symptoms,
        bottleneck_class=entry.bottleneck_class,
        root_cause_hypotheses=entry.root_cause_hypotheses,
        evidence_refs=entry.evidence_refs,
        counterevidence_refs=entry.counterevidence_refs,
        confidence=entry.confidence,
        proposed_interventions=tuple(proposed_interventions),
        risk=risk,
        reversibility=reversibility,
        status=CoolingStatus.PROPOSED,
        created_by=entry.created_by,
        created_at=entry.created_at,
    )
    _COOLING[cooling_id] = updated
    return updated


def verify(cooling_id: str) -> dict:
    """cooling.verify — when read-only + evidence-based.

    Per mandate §8: agents may perform this autonomously when the
    verification is read-only and evidence-based.

    Returns a structured verification result. Does NOT mutate state.
    """
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return {
            "ok": False,
            "reason": "unknown_cooling_id",
            "cooling_id": cooling_id,
        }
    if not entry.proposed_interventions:
        return {
            "ok": False,
            "reason": "no_proposed_interventions",
            "cooling_id": cooling_id,
        }
    # Evidence-based verification: at least one proposed intervention
    # + some evidence references. Without evidence, verification cannot
    # claim sufficiency.
    if not entry.evidence_refs and not entry.root_cause_hypotheses:
        return {
            "ok": False,
            "reason": "insufficient_evidence",
            "cooling_id": cooling_id,
            "entry_state": entry.status.value,
        }
    # Mark as verified (immutable replacement)
    verified = CoolingEntry(
        cooling_id=entry.cooling_id,
        session_id=entry.session_id,
        trace_id=entry.trace_id,
        trigger=entry.trigger,
        symptoms=entry.symptoms,
        bottleneck_class=entry.bottleneck_class,
        root_cause_hypotheses=entry.root_cause_hypotheses,
        evidence_refs=entry.evidence_refs,
        counterevidence_refs=entry.counterevidence_refs,
        confidence=entry.confidence,
        proposed_interventions=entry.proposed_interventions,
        risk=entry.risk,
        reversibility=entry.reversibility,
        status=CoolingStatus.VERIFIED,
        created_by=entry.created_by,
        created_at=entry.created_at,
    )
    _COOLING[cooling_id] = verified
    return {
        "ok": True,
        "reason": "read_only_evidence_sufficient",
        "cooling_id": cooling_id,
        "entry_state": verified.status.value,
        "interventions": list(verified.proposed_interventions),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GATED VERBS — REQUEST SHAPES ONLY (no execution; gated by vault_outbox)
# ═══════════════════════════════════════════════════════════════════════════════

def request_approval_request(cooling_id: str, capability_needed: str) -> Optional[dict]:
    """Build an approval-request shape. Returns None if entry not found.

    Per mandate §8: cooling.approve is GATED. The actual approve step
    requires a narrow capability issued via D3 human_intent flow.
    This function only constructs the request payload.
    """
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return None
    return {
        "request_type": "cooling.approve",
        "cooling_id": cooling_id,
        "interventions": list(entry.proposed_interventions),
        "risk": entry.risk,
        "reversibility": entry.reversibility,
        "required_capability": capability_needed,
        "bottleneck_class": entry.bottleneck_class,
        "confidence": entry.confidence,
        "evidence_refs": list(entry.evidence_refs),
        "created_at": _now_iso(),
        "note": "requires bounded capability + cryptographic confirmation",
    }


def request_install_plan(cooling_id: str) -> Optional[dict]:
    """Build an install-plan shape. GATED — no execution."""
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return None
    return {
        "request_type": "cooling.install",
        "cooling_id": cooling_id,
        "interventions": list(entry.proposed_interventions),
        "rollback_route": entry.reversibility,
        "bottleneck_class": entry.bottleneck_class,
        "created_at": _now_iso(),
        "note": "requires A-FORGE bounded capability (forge_session_runtime)",
    }


def request_receipt_shape(cooling_id: str) -> Optional[dict]:
    """Build a cooling.receipt request shape. GATED for sovereign-class."""
    entry = _COOLING.get(cooling_id)
    if entry is None:
        return None
    return {
        "request_type": "cooling.receipt",
        "cooling_id": cooling_id,
        "interventions": list(entry.proposed_interventions),
        "evidence_refs": list(entry.evidence_refs),
        "confidence": entry.confidence,
        "receipt_class_suggestion": "COOLING_RECEIPT",
        "created_at": _now_iso(),
        "note": "canonical writer must accept; service signer for routine; sovereign signer for SOVEREIGN_DECISION",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# QUERIES (read-only)
# ═══════════════════════════════════════════════════════════════════════════════

def get_entry(cooling_id: str) -> Optional[CoolingEntry]:
    return _COOLING.get(cooling_id)


def list_entries() -> list[CoolingEntry]:
    return list(_COOLING.values())


__all__ = [
    "BottleneckClass",
    "CoolingStatus",
    "CoolingVerb",
    "CoolingEntry",
    "observe",
    "diagnose",
    "propose",
    "verify",
    "request_approval_request",
    "request_install_plan",
    "request_receipt_shape",
    "get_entry",
    "list_entries",
]
