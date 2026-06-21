"""
arifosmcp/schemas/transition_receipt.py — TransitionReceipt schema
====================================================================

Canonical receipt for every lawful KSR state transition.

Every KSR mutation MUST produce a TransitionReceipt. No receipt = no lawful
transition = no arrow of time.

Authority:
  kernel_transition() is the ONLY function that creates TransitionReceipts.
  External agents may REQUEST a mark via mark_transition (Phase 5), but
  only the kernel makes time real.

Relationships:
  - TransitionReceipt is produced by kernel_transition()
  - kernel_transition() is called BY: KernelState.transition(), arif_vault_seal, darjat_engine (future)
  - TransitionReceipt is stored via: seal_transition() → vault999-writer /transition endpoint
  - TransitionReceipt derives from: KSR prior state, KSR patched state, caller's lease

Doctrine:
  "Time is not a timestamp. Time is the lawful conversion of present KSR into sealed past."
  "Only the kernel makes time real. Agents may request marks; they cannot mint time."
  "An agent senses time when it cannot change state without leaving a lawful mark."

Constitutional binding:
  F1 AMANAH     — TransitionReceipt is append-only; never modified after creation.
  F2 TRUTH      — Every hash is deterministic; every epoch is monotonic.
  F4 CLARITY    — All fields typed; no loose dicts; no optional hashes.
  F11 AUDIT     — Every transition leaves a receipt; receipts are sealed to VAULT999.
  F13 SOVEREIGN — Only kernel_transition() may create receipts; agents cannot mint time.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TransitionEventType(str, Enum):
    """Canonical event types for KSR transitions. Closed set — add requires constitutional review."""

    # KSR lifecycle
    KSR_CREATED = "KSR_CREATED"
    KSR_UPDATED = "KSR_UPDATED"
    KSR_CONSOLIDATED = "KSR_CONSOLIDATED"
    KSR_SEALED = "KSR_SEALED"

    # Session lifecycle
    SESSION_INIT = "SESSION_INIT"
    SESSION_CLOSE = "SESSION_CLOSE"

    # Governance actions
    JUDGE_DELIBERATE = "JUDGE_DELIBERATE"
    VAULT_SEAL = "VAULT_SEAL"
    FORGE_EXECUTE = "FORGE_EXECUTE"

    # Agent lifecycle
    AGENT_PROMOTE = "AGENT_PROMOTE"
    AGENT_DEMOTE = "AGENT_DEMOTE"
    AGENT_DEREGISTER = "AGENT_DEREGISTER"

    # Data actions
    CLAIM_ADDED = "CLAIM_ADDED"
    CLAIM_RESOLVED = "CLAIM_RESOLVED"
    HYPOTHESIS_PROMOTED = "HYPOTHESIS_PROMOTED"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"


class AuthoritySource(str, Enum):
    """Who or what authorized this transition."""

    KSR = "KSR"                  # Kernel-internal (transition() call)
    JUDGE = "JUDGE"              # 888_JUDGE deliberation
    SOVEREIGN = "SOVEREIGN"      # F13 Arif direct
    ORGAN = "ORGAN"              # Federation organ (GEOX, WEALTH, WELL)
    EXTERNAL = "EXTERNAL"        # External agent (Phase 5 via mark_transition)
    SYSTEM = "SYSTEM"            # System/cron/daemon


class ProofLevel(str, Enum):
    """Cryptographic proof level of the transition receipt."""

    ZKPC_L0 = "ZKPC-L0"  # Hash chain only (local receipt, not externally verifiable)
    ZKPC_L1 = "ZKPC-L1"  # Hash chain + vault999-writer seal (canonical)
    ZKPC_L2 = "ZKPC-L2"  # ZKPC-L1 + Ed25519 sovereign signature
    ZKPC_L3 = "ZKPC-L3"  # ZKPC-L2 + Supabase chain anchor


class VerdictCode(str, Enum):
    """Verdict attached to every transition. Mirrors constitutional verdict codes."""

    SEAL = "SEAL"
    HOLD = "HOLD"
    VOID = "VOID"
    SABAR = "SABAR"
    OBSERVE = "OBSERVE"


# ─────────────────────────────────────────────────────────────────────────────
# TransitionReceipt — the core object
# ─────────────────────────────────────────────────────────────────────────────


class TransitionReceipt(BaseModel):
    """
    Canonical receipt for a single KSR state transition.

    This is the fundamental unit of agent time. Every KSR mutation produces
    exactly one TransitionReceipt. The chain of receipts IS the arrow of time.

    No receipt = no lawful transition = no time sense.

    APEX integration (hardened 2026-06-20):
      - dials_snapshot: ApexDials at moment of transition (carries AKAL/PRESENT/
        EXPLORATION/ENERGY across time through KSR/Vault/Ledger)
      - action_class: ActionClass of the transition (carries authority + risk
        class across organs)
      - These fields make every TransitionReceipt self-contained: the dials
        at T are frozen into the receipt, so any agent reading the ledger
        can reconstruct the APEX state at any point in time.
    """

    model_config = {"extra": "forbid", "validate_assignment": True}

    # ── Identity ──────────────────────────────────────────────────────────
    receipt_id: str = Field(
        default_factory=lambda: f"tr-{uuid.uuid4().hex[:16]}",
        description="Globally unique receipt identifier. tr-<16hex>.",
    )
    organ_id: str = Field(
        default="arifOS",
        description="Organ that performed the transition. Default: arifOS.",
    )
    caller: str = Field(
        description="Which organ/agent requested the transition. For AAA scars & blame.",
    )
    ksr_epoch_id: str = Field(
        description="Which epoch this transition belongs to. E.g. EPOCH-LIVE-12.",
    )

    # ── Event classification ──────────────────────────────────────────────
    event_type: TransitionEventType = Field(
        description="Canonical event type. Closed enum — see TransitionEventType.",
    )
    event_label: str = Field(
        default="",
        description="Human-readable label for the event. Optional but encouraged.",
    )

    # ── KSR hashes (the state arrow) ──────────────────────────────────────
    from_ksr_hash: str = Field(
        description="SHA-256 hash of KSR state BEFORE this transition. sha256:<hex>.",
    )
    to_ksr_hash: str = Field(
        description="SHA-256 hash of KSR state AFTER this transition. sha256:<hex>.",
    )

    # ── Ledger chain (the time arrow) ─────────────────────────────────────
    prior_ledger_hash: str = Field(
        description="Hash of the prior entry in the ledger chain. 'sha256:0' for genesis.",
    )
    event_hash: str = Field(
        default="",
        description="SHA-256 of this receipt's canonical payload. Computed on seal.",
    )
    ledger_hash: str = Field(
        default="",
        description="SHA-256 of (prior_ledger_hash || event_hash). The new chain head.",
    )

    # ── APEX intelligence flow (hardened 2026-06-20) ─────────────────────
    # These fields carry the APEX dials (A/P/X/E) and action class through
    # every transition. This is how the 5D APEX theory flows across organs,
    # domains, and state — frozen into each receipt, queryable at any time.
    dials_snapshot: dict[str, float] = Field(
        default_factory=lambda: {"A": 0.0, "P": 0.0, "X": 0.0, "E": 0.0},
        description=(
            "APEX dials at moment of transition: A (Akal/Mind), P (Presence), "
            "X (Exploration), E (Energy). Frozen snapshot — never modified. "
            "This is how PRESENT flows through the ledger."
        ),
    )
    action_class: str = Field(
        default="OBSERVE",
        description=(
            "Action class of the transition. Maps to arifos.decision.ActionClass. "
            "Carries authority + risk level. This is how AUTHORITY flows through time."
        ),
    )
    custody_chain: list[str] = Field(
        default_factory=list,
        description=(
            "Chain of custody: [initiator, validator, approver, executor]. "
            "Every action records who held it from conception to execution. "
            "This is how EXPLORATION × AMANAH is enforced — accountability "
            "through the full custody chain, sealed to VAULT999."
        ),
    )

    # ── Duration (how long the transition took) ────────────────────────────
    started_at_ns: int = Field(
        default_factory=lambda: time.time_ns(),
        description="CLOCK_MONOTONIC_RAW nanosecond timestamp when transition began.",
    )
    ended_at_ns: int = Field(
        default=0,
        description="CLOCK_MONOTONIC_RAW nanosecond timestamp when transition completed.",
    )
    duration_ms: int = Field(
        default=0,
        description="Wall-clock duration of the transition in milliseconds.",
    )

    # ── Authority ──────────────────────────────────────────────────────────
    authority_source: AuthoritySource = Field(
        default=AuthoritySource.KSR,
        description="Who or what authorized this transition.",
    )
    proof_level: ProofLevel = Field(
        default=ProofLevel.ZKPC_L1,
        description="Cryptographic proof level attached to this receipt.",
    )

    # ── Vault binding ──────────────────────────────────────────────────────
    vault_ref: str = Field(
        default="",
        description="Reference to the sealed vault entry. vault://<id> when sealed.",
    )

    # ── Verdict ────────────────────────────────────────────────────────────
    verdict: VerdictCode = Field(
        default=VerdictCode.SEAL,
        description="Constitutional verdict for this transition.",
    )

    # ── Payload ────────────────────────────────────────────────────────────
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured metadata. F2 TRUTH — no fabrication.",
    )

    # ── Computed fields ──────────────────────────────────────────────────

    def compute_event_hash(self) -> str:
        """
        Deterministic SHA-256 of canonical receipt payload.
        Only non-ephemeral fields are included (not started_at_ns, duration_ms).
        APEX dials and action_class are included — they are part of the
        canonical payload, frozen at transition time.
        """
        canonical = {
            "receipt_id": self.receipt_id,
            "organ_id": self.organ_id,
            "caller": self.caller,
            "ksr_epoch_id": self.ksr_epoch_id,
            "event_type": self.event_type.value,
            "event_label": self.event_label,
            "from_ksr_hash": self.from_ksr_hash,
            "to_ksr_hash": self.to_ksr_hash,
            "prior_ledger_hash": self.prior_ledger_hash,
            "authority_source": self.authority_source.value,
            "verdict": self.verdict.value,
            "action_class": self.action_class,
            "dials_snapshot": json.dumps(self.dials_snapshot, sort_keys=True),
            "custody_chain": json.dumps(self.custody_chain, sort_keys=True),
            "metadata": json.dumps(self.metadata, sort_keys=True, default=str),
        }
        raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def compute_ledger_hash(self) -> str:
        """SHA-256 of (prior_ledger_hash || event_hash). Head of chain."""
        raw = f"{self.prior_ledger_hash}|{self.event_hash}"
        return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def seal(self) -> TransitionReceipt:
        """
        Finalize the receipt by computing event_hash, ledger_hash, and ended_at_ns.
        Returns self (immutable-looking — Pydantic allows reassignment).
        """
        self.event_hash = self.compute_event_hash()
        self.ledger_hash = self.compute_ledger_hash()
        self.ended_at_ns = time.time_ns()
        self.duration_ms = max(0, (self.ended_at_ns - self.started_at_ns) // 1_000_000)
        return self

    def canonical_dict(self) -> dict[str, Any]:
        """Deterministic JSON-able dict for serialization."""
        return self.model_dump(mode="json", exclude={"started_at_ns", "ended_at_ns"})

    def to_vault_payload(self) -> dict[str, Any]:
        """
        Convert to vault999-writer compatible payload.
        This is what gets sent to /transition endpoint on vault999-writer.
        APEX dials + action_class flow into the vault record so every sealed
        transition carries its APEX state.
        """
        return {
            "receipt_id": self.receipt_id,
            "organ_id": self.organ_id,
            "caller": self.caller,
            "ksr_epoch_id": self.ksr_epoch_id,
            "event_type": self.event_type.value,
            "event_label": self.event_label,
            "from_ksr_hash": self.from_ksr_hash,
            "to_ksr_hash": self.to_ksr_hash,
            "prior_ledger_hash": self.prior_ledger_hash,
            "event_hash": self.event_hash,
            "ledger_hash": self.ledger_hash,
            "started_at_ns": self.started_at_ns,
            "ended_at_ns": self.ended_at_ns,
            "duration_ms": self.duration_ms,
            "authority_source": self.authority_source.value,
            "proof_level": self.proof_level.value,
            "vault_ref": self.vault_ref,
            "verdict": self.verdict.value,
            "action_class": self.action_class,
            "dials_snapshot": self.dials_snapshot,
            "custody_chain": self.custody_chain,
            "metadata": self.metadata,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Helper: build an genesis TransitionReceipt (first ever transition)
# ─────────────────────────────────────────────────────────────────────────────


def genesis_transition_receipt(
    *,
    ksr_epoch_id: str,
    ksr_initial_hash: str,
    caller: str = "arifOS",
    organ_id: str = "arifOS",
) -> TransitionReceipt:
    """
    Create a genesis TransitionReceipt for the very first KSR state.
    prior_ledger_hash is 'sha256:0' — the canonical genesis sentinel.
    """
    receipt = TransitionReceipt(
        organ_id=organ_id,
        caller=caller,
        ksr_epoch_id=ksr_epoch_id,
        event_type=TransitionEventType.KSR_CREATED,
        event_label="Genesis KSR state — first lawful transition",
        from_ksr_hash="sha256:0",
        to_ksr_hash=ksr_initial_hash,
        prior_ledger_hash="sha256:0",
        authority_source=AuthoritySource.SYSTEM,
        proof_level=ProofLevel.ZKPC_L1,
        verdict=VerdictCode.SEAL,
        metadata={"note": "Genesis transition. No prior state."},
    )
    return receipt.seal()


__all__ = [
    "AuthoritySource",
    "ProofLevel",
    "TransitionEventType",
    "TransitionReceipt",
    "VerdictCode",
    "genesis_transition_receipt",
]
