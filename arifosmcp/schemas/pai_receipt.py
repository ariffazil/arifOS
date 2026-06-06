"""
PAI Receipt — Provenance + Authority + Intent
═══════════════════════════════════════════════════════════════════
The single federation-wide envelope that every cross-organ output MUST carry.

Ratified: 2026-06-06  by Arif Fazil (F13 SOVEREIGN) — agent forge (Ω)
Status:   CANONICAL v1  — single source of truth
Location: arifOS/arifosmcp/schemas/pai_receipt.py  (this file)
Mirrored: every other organ gets a local `pai_receipt.py` with the same schema
          (independent implementations, identical contract — this file is the
          authoritative definition).

Why this exists
---------------
Without an envelope, the federation cannot distinguish:
  - a human draft from a tool claim
  - an AI synthesis from a sealed verdict
  - a sovereign-authorized spend from a vibe-driven transaction
  - a reversible analysis from an irreversible consequence

A PAI Receipt says explicitly: WHO/WHAT produced this, WHO authorized it,
WHAT it is allowed to affect, WHAT tier of consequence it crosses, and WHERE
its audit trail lives. Without the receipt, the object is UNVERIFIED/DRAFT
— not false, not useless, just not allowed to cross into consequence.

Five-Tier Boundary Rules
------------------------
Tier | Example                   | Receipt required                | Consequence
-----+---------------------------+---------------------------------+-----------------
  1  | Draft thought             | none (local metadata only)      | private
  2  | Internal analysis         | provenance receipt              | local
  3  | External claim            | provenance + authority receipt  | publishable
  4  | Consequential action       | full PAI + human intent         | spend/deploy
  5  | Atomic action              | full PAI + 888 HOLD signature   | irreversible

Kernel Rules (arifOS)
--------------------
  - No receipt              → no consequence.
  - Invalid receipt         → HOLD.
  - Receipt mismatch        → VOID.
  - High-risk receipt (T4+) → 888 human confirmation.
  - Atomic receipt (T5)     → 888 explicit HOLD approval.

Non-Negotiables (F13, F11, F9)
------------------------------
  1. Behavioral biometrics = signal only. NEVER identity root, NEVER sovereign
     proof, NEVER final authority. (WELL may flag coercion risk; it does NOT
     authorize.)
  2. Organs do NOT sign their own receipts. Receipt signing is separated from
     organ execution. arifOS verifies. VAULT records.
  3. Avoid universal-receipt surveillance. Drafts are local metadata. Consequential
     actions get full PAI. Atomic gets 888 HOLD.

DITEMPA BUKAN DIBERI — the boundary object, forged.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


# ═══════════════════════════════════════════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class ProducerType(StrEnum):
    """WHO/WHAT produced this object."""

    HUMAN = "human"
    AI = "ai"
    HUMAN_ASSISTED_AI = "human_assisted_ai"
    TOOL = "tool"
    UNKNOWN = "unknown"
    MIXED = "mixed"  # ensemble — multiple producer_types; record all in evidence.sources


class Organ(StrEnum):
    """Which federation organ produced/owns this receipt."""

    ARIFOS = "arifOS"
    GEOX = "GEOX"
    WEALTH = "WEALTH"
    WELL = "WELL"
    A_FORGE = "A-FORGE"
    APEX = "APEX"
    AAA = "AAA"
    EXTERNAL = "EXTERNAL"


class IntentAction(StrEnum):
    """WHAT exact action is this allowed to perform."""

    DRAFT = "draft"  # thinking, brainstorming
    ANALYZE = "analyze"  # read-only compute
    PUBLISH = "publish"  # public-facing claim
    SPEND = "spend"  # capital action
    TRADE = "trade"  # market action
    ALLOCATE = "allocate"  # budget action
    INVEST = "invest"  # commitment action
    PRICE = "price"  # publish financial claim
    TRANSFER = "transfer"  # move resource
    DELETE = "delete"  # remove data
    DEPLOY = "deploy"  # ship code
    SEAL = "seal"  # immutable record
    MODIFY_TREASURY = "modify_treasury"
    ADVISORY = "advisory"  # emit readiness/reflection signal (WELL)


class RiskClass(StrEnum):
    """Blast-radius classification. Maps directly to Tier."""

    LOW = "low"  # T1-T2 — drafts, internal analysis
    MEDIUM = "medium"  # T3 — external claims
    HIGH = "high"  # T4 — consequential
    ATOMIC = "atomic"  # T5 — irreversible, high blast radius


class Reversibility(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class Tier(StrEnum):
    """Five-tier boundary classification. Maps to RiskClass."""

    DRAFT = "draft"  # T1
    INTERNAL = "internal"  # T2
    EXTERNAL_CLAIM = "external_claim"  # T3
    CONSEQUENTIAL = "consequential"  # T4
    ATOMIC = "atomic"  # T5


# ═══════════════════════════════════════════════════════════════════════════════
#  CANONICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════


PAI_RECEIPT_TYPE = "arifOS.PAI.v1"
"""The single receipt-type identifier. arifOS verifier rejects any other."""

CANONICAL_HUMAN_ROOT = "did:web:arif-fazil.com"
"""The F13 SOVEREIGN human root. All authority chains must terminate here."""

# Map RiskClass → Tier
RISK_TO_TIER: dict[RiskClass, Tier] = {
    RiskClass.LOW: Tier.DRAFT,  # default for low is DRAFT; explicit intent sets higher
    RiskClass.MEDIUM: Tier.EXTERNAL_CLAIM,
    RiskClass.HIGH: Tier.CONSEQUENTIAL,
    RiskClass.ATOMIC: Tier.ATOMIC,
}

# Map IntentAction → minimum Tier required
INTENT_MIN_TIER: dict[IntentAction, Tier] = {
    IntentAction.DRAFT: Tier.DRAFT,
    IntentAction.ANALYZE: Tier.INTERNAL,
    IntentAction.ADVISORY: Tier.INTERNAL,
    IntentAction.PUBLISH: Tier.EXTERNAL_CLAIM,
    IntentAction.PRICE: Tier.EXTERNAL_CLAIM,
    IntentAction.SEAL: Tier.EXTERNAL_CLAIM,
    IntentAction.SPEND: Tier.CONSEQUENTIAL,
    IntentAction.TRADE: Tier.CONSEQUENTIAL,
    IntentAction.ALLOCATE: Tier.CONSEQUENTIAL,
    IntentAction.INVEST: Tier.CONSEQUENTIAL,
    IntentAction.TRANSFER: Tier.CONSEQUENTIAL,
    IntentAction.MODIFY_TREASURY: Tier.ATOMIC,
    IntentAction.DEPLOY: Tier.CONSEQUENTIAL,
    IntentAction.DELETE: Tier.ATOMIC,  # data loss is atomic unless reversible
}


# ═══════════════════════════════════════════════════════════════════════════════
#  PAI RECEIPT MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class PAIOrigin(BaseModel):
    """WHO/WHAT produced this object."""

    producer_type: ProducerType
    producer_id: str  # did:web:..., agent_id, tool_id, "anonymous"
    organ: Organ
    model_id: Optional[str] = None  # e.g. "MiniMax-M3", "bge-m3", "geox_petrophysics_v1"
    tool_id: Optional[str] = None  # e.g. "geox_data_qc_bundle"


class PAIAuthority(BaseModel):
    """WHO authorized this. Authority chain must terminate at CANONICAL_HUMAN_ROOT."""

    human_root: str = CANONICAL_HUMAN_ROOT
    delegate: str  # agent_id or tool_id that holds this authority
    authority_chain: list[str] = Field(default_factory=list)  # ["root", "grant:N", "delegation:N"]
    expires_at: Optional[datetime] = None  # None = no expiry; bounded = short-lived
    subdelegation_allowed: bool = False  # true only with explicit grant


class PAIIntent(BaseModel):
    """WHAT is this allowed to affect."""

    action: IntentAction
    scope: str  # bounded description, e.g. "claim:horizon_contrast_layang_layang"
    risk_class: RiskClass
    external_effect: bool  # does this cross the federation boundary?
    reversibility: Reversibility = Reversibility.FULL
    requires_human_intent: bool = False  # true if T4+
    requires_888_hold: bool = False  # true if T5

    @model_validator(mode="after")
    def _enforce_intent_floor(self) -> "PAIIntent":
        """T4 needs human intent. T5 needs 888 HOLD. No surprise escalations."""
        tier = RISK_TO_TIER[self.risk_class]
        if tier in (Tier.CONSEQUENTIAL, Tier.ATOMIC) and not self.requires_human_intent:
            object.__setattr__(self, "requires_human_intent", True)
        if tier == Tier.ATOMIC and not self.requires_888_hold:
            object.__setattr__(self, "requires_888_hold", True)
        if self.requires_888_hold and self.reversibility == Reversibility.FULL:
            # 888 HOLD implies non-reversible by definition
            object.__setattr__(self, "reversibility", Reversibility.NONE)
        return self


class PAIEvidence(BaseModel):
    """WHAT evidence backs this object."""

    sources: list[str] = Field(default_factory=list)  # evidence_refs, file paths, URLs
    tool_calls: list[str] = Field(default_factory=list)  # tool invocations used
    confidence: str = "unknown"  # CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN
    human_reviewed: bool = False
    reviewer_id: Optional[str] = None  # did of human reviewer, if any


class PAIAudit(BaseModel):
    """WHERE the audit trail lives."""

    destination: str = "VAULT999"  # canonical audit destination
    previous_receipt: Optional[str] = None  # content hash of parent receipt, for chains
    receipt_hash: Optional[str] = None  # computed at finalize-time
    signature: Optional[str] = None  # ed25519 / HMAC; not self-signed by organ
    vault_ref: Optional[str] = None  # VAULT999 seal id, if sealed


class PAIReceipt(BaseModel):
    """
    The PAI Receipt — Provenance + Authority + Intent.

    One envelope. One schema. Every cross-organ output carries it, or the
    federation treats the object as UNVERIFIED/DRAFT.
    """

    receipt_type: str = PAI_RECEIPT_TYPE
    object_id: str  # uuid or content hash of the object this receipt covers
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    origin: PAIOrigin
    authority: PAIAuthority
    intent: PAIIntent
    evidence: PAIEvidence = Field(default_factory=PAIEvidence)
    audit: PAIAudit = Field(default_factory=PAIAudit)

    @model_validator(mode="after")
    def _enforce_receipt_type(self) -> "PAIReceipt":
        if self.receipt_type != PAI_RECEIPT_TYPE:
            raise ValueError(
                f"receipt_type must be '{PAI_RECEIPT_TYPE}', got {self.receipt_type!r}. "
                "arifOS verifier rejects foreign receipt types."
            )
        return self


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def tier_of(receipt: PAIReceipt | dict[str, Any]) -> Tier:
    """Return the Tier classification for a receipt.

    Tier is derived from intent.risk_class via RISK_TO_TIER. Cross-checks that
    the action's required minimum tier is not higher than the declared tier.
    """
    if isinstance(receipt, dict):
        risk = receipt.get("intent", {}).get("risk_class", "low")
        action = receipt.get("intent", {}).get("action", "draft")
    else:
        risk = receipt.intent.risk_class
        action = receipt.intent.action

    declared_tier = RISK_TO_TIER[RiskClass(risk)]
    min_tier = INTENT_MIN_TIER[IntentAction(action)]
    # Take the higher of the two (more conservative)
    tier_order = [Tier.DRAFT, Tier.INTERNAL, Tier.EXTERNAL_CLAIM, Tier.CONSEQUENTIAL, Tier.ATOMIC]
    if tier_order.index(min_tier) > tier_order.index(declared_tier):
        return min_tier
    return declared_tier


def content_hash(obj: Any) -> str:
    """Stable SHA-256 hash of an object's canonical JSON form.

    Used for object_id and receipt_hash. Sorts keys for determinism.
    """
    canonical = json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def mint_pai_receipt(
    *,
    object_id: str,
    producer_type: ProducerType,
    producer_id: str,
    organ: Organ,
    action: IntentAction,
    scope: str,
    risk_class: RiskClass,
    external_effect: bool = False,
    reversibility: Reversibility = Reversibility.FULL,
    delegate: str = "anonymous",
    authority_chain: Optional[list[str]] = None,
    expires_at: Optional[datetime] = None,
    subdelegation_allowed: bool = False,
    sources: Optional[list[str]] = None,
    tool_calls: Optional[list[str]] = None,
    confidence: str = "unknown",
    human_reviewed: bool = False,
    reviewer_id: Optional[str] = None,
    model_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    previous_receipt: Optional[str] = None,
    destination: str = "VAULT999",
    signature: Optional[str] = None,
) -> PAIReceipt:
    """Construct a new PAI Receipt. The single forge for receipts across the federation."""
    intent = PAIIntent(
        action=action,
        scope=scope,
        risk_class=risk_class,
        external_effect=external_effect,
        reversibility=reversibility,
    )
    authority = PAIAuthority(
        delegate=delegate,
        authority_chain=authority_chain or ["root"],
        expires_at=expires_at,
        subdelegation_allowed=subdelegation_allowed,
    )
    evidence = PAIEvidence(
        sources=sources or [],
        tool_calls=tool_calls or [],
        confidence=confidence,
        human_reviewed=human_reviewed,
        reviewer_id=reviewer_id,
    )
    audit = PAIAudit(
        destination=destination,
        previous_receipt=previous_receipt,
        signature=signature,
    )
    origin = PAIOrigin(
        producer_type=producer_type,
        producer_id=producer_id,
        organ=organ,
        model_id=model_id,
        tool_id=tool_id,
    )
    receipt = PAIReceipt(
        object_id=object_id,
        origin=origin,
        authority=authority,
        intent=intent,
        evidence=evidence,
        audit=audit,
    )
    # Finalize: compute receipt_hash
    receipt.audit.receipt_hash = content_hash(receipt.model_dump(exclude={"audit"}))
    return receipt


def verify_pai_receipt(
    receipt: dict[str, Any] | PAIReceipt,
    *,
    expected_organ: Optional[Organ] = None,
    expected_action: Optional[IntentAction] = None,
    min_tier: Optional[Tier] = None,
    require_human_root: bool = True,
    require_888_signature: bool = False,
) -> dict[str, Any]:
    """Verify a PAI Receipt against the canonical rules.

    Returns a verdict dict:
      {
        "verdict": "SEAL" | "HOLD" | "VOID",
        "tier": Tier,
        "reasons": [str, ...],
        "checks": { ... per-check pass/fail ... },
      }

    Rules:
      - receipt_type must equal PAI_RECEIPT_TYPE (else VOID)
      - object_id must be non-empty (else VOID)
      - authority.human_root must equal CANONICAL_HUMAN_ROOT if require_human_root
      - tier must be >= min_tier (else HOLD)
      - if tier == ATOMIC, signature must be present and require_888_signature
      - if expected_organ, receipt.organ must match
      - if expected_action, receipt.action must match
    """
    reasons: list[str] = []
    checks: dict[str, bool] = {}

    # Normalize
    if isinstance(receipt, PAIReceipt):
        r = receipt.model_dump()
    else:
        r = receipt

    # 1. receipt_type
    checks["receipt_type_valid"] = r.get("receipt_type") == PAI_RECEIPT_TYPE
    if not checks["receipt_type_valid"]:
        reasons.append(
            f"VOID: receipt_type must be {PAI_RECEIPT_TYPE!r}, got {r.get('receipt_type')!r}"
        )
        return {"verdict": "VOID", "tier": None, "reasons": reasons, "checks": checks}

    # 2. object_id
    checks["object_id_present"] = bool(r.get("object_id"))
    if not checks["object_id_present"]:
        reasons.append("VOID: object_id missing")

    # 3. organ match
    if expected_organ is not None:
        organ = r.get("origin", {}).get("organ")
        checks["organ_match"] = organ == expected_organ.value
        if not checks["organ_match"]:
            reasons.append(f"HOLD: organ mismatch — expected {expected_organ.value}, got {organ!r}")
    else:
        checks["organ_match"] = True

    # 4. action match
    if expected_action is not None:
        action = r.get("intent", {}).get("action")
        checks["action_match"] = action == expected_action.value
        if not checks["action_match"]:
            reasons.append(
                f"HOLD: action mismatch — expected {expected_action.value}, got {action!r}"
            )
    else:
        checks["action_match"] = True

    # 5. human root
    if require_human_root:
        hr = r.get("authority", {}).get("human_root")
        checks["human_root_valid"] = hr == CANONICAL_HUMAN_ROOT
        if not checks["human_root_valid"]:
            reasons.append(f"HOLD: human_root must be {CANONICAL_HUMAN_ROOT!r}, got {hr!r}")
    else:
        checks["human_root_valid"] = True

    # 6. tier check
    try:
        t = tier_of(r)
        tier_value = t.value
    except Exception as e:
        reasons.append(f"HOLD: tier derivation failed — {e}")
        tier_value = None
        checks["tier_derivable"] = False
    else:
        checks["tier_derivable"] = True

    if min_tier is not None and tier_value is not None:
        tier_order = [tier.value for tier in Tier]
        try:
            ok = tier_order.index(tier_value) >= tier_order.index(min_tier.value)
        except ValueError:
            ok = False
        checks["tier_meets_minimum"] = ok
        if not ok:
            reasons.append(f"HOLD: tier {tier_value!r} below required minimum {min_tier.value!r}")
    else:
        checks["tier_meets_minimum"] = True

    # 7. ATOMIC requires 888 signature
    if tier_value == Tier.ATOMIC.value:
        sig = r.get("audit", {}).get("signature")
        if require_888_signature and not sig:
            reasons.append("HOLD: ATOMIC tier requires 888 HOLD signature in audit.signature")
            checks["atomic_signature_present"] = False
        else:
            checks["atomic_signature_present"] = bool(sig) or not require_888_signature
    else:
        checks["atomic_signature_present"] = True

    # Decide
    if any(v is False for v in checks.values() if v in (False,)):
        if any("VOID" in reason for reason in reasons):
            verdict = "VOID"
        else:
            verdict = "HOLD"
    else:
        verdict = "SEAL"

    return {
        "verdict": verdict,
        "tier": tier_value,
        "reasons": reasons,
        "checks": checks,
        "object_id": r.get("object_id"),
        "organ": r.get("origin", {}).get("organ"),
        "action": r.get("intent", {}).get("action"),
        "risk_class": r.get("intent", {}).get("risk_class"),
        "human_root": r.get("authority", {}).get("human_root"),
        "external_effect": r.get("intent", {}).get("external_effect"),
        "reversibility": r.get("intent", {}).get("reversibility"),
    }


def attach_pai_to_payload(
    payload: dict[str, Any],
    receipt: PAIReceipt,
) -> dict[str, Any]:
    """Attach a PAI Receipt to a tool's output payload.

    The returned dict has a `_pai_receipt` key carrying the receipt. The rest
    of the payload is preserved unchanged. This is the standard envelope
    injection point for all 4 organs.
    """
    out = dict(payload)
    out["_pai_receipt"] = receipt.model_dump()
    return out


def required_minimum_tier(action: IntentAction) -> Tier:
    """Return the minimum tier required for a given action."""
    return INTENT_MIN_TIER[action]


__all__ = [
    # Constants
    "PAI_RECEIPT_TYPE",
    "CANONICAL_HUMAN_ROOT",
    "RISK_TO_TIER",
    "INTENT_MIN_TIER",
    # Enums
    "ProducerType",
    "Organ",
    "IntentAction",
    "RiskClass",
    "Reversibility",
    "Tier",
    # Models
    "PAIOrigin",
    "PAIAuthority",
    "PAIIntent",
    "PAIEvidence",
    "PAIAudit",
    "PAIReceipt",
    # Functions
    "tier_of",
    "content_hash",
    "mint_pai_receipt",
    "verify_pai_receipt",
    "attach_pai_to_payload",
    "required_minimum_tier",
]
