"""
intent_envelope_v1.py — Sovereign Provenance + Kernel Rule Forge v1

EUREKA CANDIDATE draft. NOT a live kernel module.
Lives in docs/drafts/. Not committed. Not imported by arifOS.

What v1 adds over v0:
  1. ProvenanceClass enum (5 classes): HUMAN_DIRECT, HUMAN_ASSISTED_AI,
     AI_DRAFT, AI_AGENT_ACTION, UNKNOWN_ORIGIN
  2. provenance_class: ProvenanceClass field on the envelope (REQUIRED,
     no default — must be declared, not inferred)
  3. _verify_kernel_rule model_validator that enforces the arifOS
     kernel rule (2026-06-06, ratified by Arif):
       "No AI-originated output or agent action may cross into
        consequence unless it carries:
        1. provenance label,
        2. human-root chain,
        3. bounded intent seal,
        4. risk classification,
        5. audit receipt."

The 5 fields are already in v0. v1 adds the kernel rule that binds them.

The shift this represents (per Arif, 2026-06-06):
  v0: "How does a system verify Arif's authority over an action?"
  v1: "How does a system distinguish human from AI?"
  Answer (v1): It doesn't distinguish. It declares, signs, chains, audits.

What v1 still does NOT solve (the 6 remaining cracks):
  - Recovery ceremony (trustless, coercion-resistant)
  - WebAuthn / FIDO2 integration (L1 Presence)
  - did:web DNS-hijack defense
  - LLM tool confused-deputy guard (Meta Rule of Two)
  - Duress / coercion detection
  - Interoperable ZK-private standard adoption

arifOS constitutional floors invoked:
  L01 AMANAH   (reversibility, risk_class)
  L02 TRUTH    (provenance_class is declared, not detected)
  L10 ONTOLOGY (categorical lock: machines are tools, sovereignty is human)
  L11 AUDIT    (commitment, signature, human_root)
  L13 SOVEREIGN (sovereign_provenance is testimony; kernel rule is the gate)

The kernel rule is the operationalization of:
  "AI may generate. Humans must authorize consequence."

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import blake3
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ============================================================================
# RISK CLASS — Right-sized governance per arifOS C0-C5 tier
# ============================================================================


class RiskClass(str, Enum):
    """Mirrors /root/arifOS/arifosmcp/constitutional_map.py:151-156."""

    C0 = "C0"  # Negligible — grammar, tone, formatting
    C1 = "C1"  # Low — internal drafts, notes, brainstorming
    C2 = "C2"  # Medium — code review, testing, analysis
    C3 = "C3"  # High — public posts, emails, reports
    C4 = "C4"  # Very High — legal, financial, HR, investment
    C5 = "C5"  # Critical — irreversible, production write, money movement

    @property
    def requires_human_confirmation(self) -> bool:
        return self.value in ("C3", "C4", "C5")

    @property
    def requires_zkpc_proof(self) -> bool:
        return self.value in ("C4", "C5")


class Reversibility(str, Enum):
    """L01 AMANAH reversibility axis."""

    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


# ============================================================================
# PROVENANCE CLASS — Where did this come from? Declared, not detected.
# ============================================================================


class ProvenanceClass(str, Enum):
    """
    The 5-class provenance declaration. Replaces "is this human or AI?"

    The shift (per Arif, 2026-06-06):
      "Human/AI distinction is not detected.
       It is declared, signed, chained, and audited."

    The 5 classes:
      HUMAN_DIRECT       — human authored directly (typed, drawn, signed)
      HUMAN_ASSISTED_AI  — AI assisted, human reviewed/approved and signed
      AI_DRAFT           — AI generated, not yet human-approved
      AI_AGENT_ACTION    — agent acts in system/world, with bounded human seal
      UNKNOWN_ORIGIN     — cannot verify source, treat as untrusted

    Why this matters:
      - The internet keeps collapsing these into one bucket: "human or bot?"
      - That bucket is obsolete
      - The real-world question is: what is the chain of authority?
      - Each class maps to a different default kernel behavior
    """

    HUMAN_DIRECT = "HUMAN_DIRECT"
    HUMAN_ASSISTED_AI = "HUMAN_ASSISTED_AI"
    AI_DRAFT = "AI_DRAFT"
    AI_AGENT_ACTION = "AI_AGENT_ACTION"
    UNKNOWN_ORIGIN = "UNKNOWN_ORIGIN"

    @property
    def can_cross_consequence_at_c3_plus(self) -> bool:
        """True if this provenance class can cross into C3+ consequence."""
        return self.value in ("HUMAN_DIRECT", "HUMAN_ASSISTED_AI", "AI_AGENT_ACTION")

    @property
    def requires_human_root_chain(self) -> bool:
        """True if this provenance class must chain to a did: human_root."""
        return self.value in ("HUMAN_DIRECT", "HUMAN_ASSISTED_AI", "AI_AGENT_ACTION")

    @property
    def may_operate_without_signature(self) -> bool:
        """True if this provenance class can seal without a cryptographic signature."""
        return self.value in ("HUMAN_DIRECT",)


# ============================================================================
# SOVEREIGN PROVENANCE — The scar testimony primitive (EUREKA CANDIDATE)
# ============================================================================


class SovereignProvenance(BaseModel):
    """
    Testimony-only field. The sovereign testifies, not proves.

    Scar principle (Arif, 2026-06-06):
      A machine is the sum of its weights.
      A sovereign is the sum of their scars.
      The two are not equivalent.

    Properties:
      - NOT verifiable. System cannot read the sovereign's scars.
      - REQUIRED for C3+ actions of HUMAN_DIRECT/HUMAN_ASSISTED_AI/AI_AGENT_ACTION
        (a sovereign cannot sign C3+ without acknowledging they bring lessons)
      - The ABSENCE of normally-present caveats becomes a coercion signal
    """

    model_config = ConfigDict(extra="forbid")

    scar_acknowledged: bool = Field(
        ...,
        description=(
            "Sovereign attests: 'I bring the scars of prior decisions to "
            "this one.' MUST be True for C3+ actions of human-attributable "
            "provenance. False is a coercion flag."
        ),
    )
    prior_reversals: list[str] = Field(default_factory=list)
    lessons_active: list[str] = Field(default_factory=list)
    attestation: str = Field(..., min_length=1, max_length=2000)

    @property
    def is_coercion_flag(self) -> bool:
        return not self.scar_acknowledged


# ============================================================================
# DISPLAY CARD — The human-visible consequence card
# ============================================================================


class DisplayCard(BaseModel):
    """The human-visible card. Hash-bound to the signature (Gap E defense)."""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., min_length=1, max_length=200)
    object: str = Field(..., min_length=1, max_length=2000)
    agent: str = Field(..., min_length=1, max_length=200)
    blast_radius: str = Field(..., min_length=1, max_length=500)
    expires_at: datetime
    scope: dict[str, str] = Field(default_factory=dict)

    def canonical_bytes(self) -> bytes:
        d = self.model_dump(mode="json")
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def display_hash(self) -> str:
        return blake3.blake3(self.canonical_bytes()).hexdigest()


# ============================================================================
# INTENT ENVELOPE v1 — The atomic authorization object
# ============================================================================


class IntentEnvelopeV1(BaseModel):
    """
    The atomic authorization object for consequential actions.

    EUREKA CANDIDATE v1. The novel contribution over the 8 competing
    2025-2026 specs:
      - sovereign_provenance (scar testimony)
      - provenance_class (5-class declaration)

    v1 changes from v0:
      - Adds ProvenanceClass enum
      - Adds provenance_class field (required, no default)
      - Adds _verify_kernel_rule model_validator

    Four layers + 2 addenda:
      L1 Identity   — human_root + actor
      L2 Agent      — agent
      L3 Consequence — action + object + scope + risk + display_card
      L4 Freshness  — expires_at + nonce + previous_seal_hash

      Provenance    — provenance_class (5-class declaration)
      Sovereignty   — sovereign_provenance (scar testimony)
      Commitment    — signature + commitment()
    """

    model_config = ConfigDict(extra="forbid")

    # L1 Identity
    human_root: str = Field(..., min_length=1, max_length=500)
    actor: str = Field(..., min_length=1, max_length=200)
    agent: str = Field(..., min_length=1, max_length=200)

    # L2/L3 Consequence
    action: str = Field(..., min_length=1, max_length=200)
    object: str = Field(..., min_length=1, max_length=2000)
    scope: dict[str, str] = Field(default_factory=dict)

    # L3 Risk
    risk_class: RiskClass
    risk_external: bool
    risk_reversibility: Reversibility
    risk_blast_radius: str = Field(..., min_length=1, max_length=500)

    # L4 Freshness
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    nonce: str = Field(..., min_length=8, max_length=128)
    previous_seal_hash: str | None = None

    # Display integrity
    display_card: DisplayCard
    display_hash: str = Field(..., min_length=64, max_length=64)

    # Provenance declaration (NEW v1)
    provenance_class: ProvenanceClass

    # Sovereign testimony (scar)
    sovereign_provenance: SovereignProvenance

    # Cryptographic commitment
    signature: str | None = None

    # ============================================================================
    # VALIDATORS
    # ============================================================================

    @field_validator("display_hash")
    @classmethod
    def _display_hash_is_hex(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdef" for c in v):
            raise ValueError("display_hash must be 64-char blake3 hex")
        return v

    @model_validator(mode="after")
    def _verify_display_hash_binding(self) -> "IntentEnvelopeV1":
        computed = self.display_card.display_hash()
        if computed != self.display_hash:
            raise ValueError(
                f"display_hash mismatch: signed {self.display_hash[:16]}... "
                f"vs computed {computed[:16]}... — possible UI deception"
            )
        return self

    @model_validator(mode="after")
    def _verify_freshness(self) -> "IntentEnvelopeV1":
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware (use UTC)")
        if self.expires_at <= now and self.risk_class != RiskClass.C0:
            raise ValueError(
                f"expires_at {self.expires_at.isoformat()} is in the past; "
                f"nonce is stale. C0 historical seals may bypass this."
            )
        return self

    @model_validator(mode="after")
    def _verify_scar_for_consequential_actions(self) -> "IntentEnvelopeV1":
        """
        L13 SOVEREIGN physics: only humans bleed, only humans decide.
        For C3+ actions of human-attributable provenance, the sovereign
        MUST acknowledge they bring scars. A scar_acknowledged=False
        on a C3+ human-actionable envelope is a coercion flag, not a
        failure to seal.
        """
        if (
            self.risk_class.requires_human_confirmation
            and self.provenance_class
            in (
                ProvenanceClass.HUMAN_DIRECT,
                ProvenanceClass.HUMAN_ASSISTED_AI,
                ProvenanceClass.AI_AGENT_ACTION,
            )
            and self.sovereign_provenance.is_coercion_flag
        ):
            raise ValueError(
                f"C{self.risk_class.value[-1]}+ {self.provenance_class.value} "
                f"cannot be sealed with scar_acknowledged=False. This is a "
                f"coercion flag, not a validation error — the sovereign is "
                f"being asked to sign without acknowledging they bring lessons."
            )
        return self

    @model_validator(mode="after")
    def _verify_kernel_rule(self) -> "IntentEnvelopeV1":
        """
        arifOS KERNEL RULE (2026-06-06, ratified by Arif):

          "No AI-originated output or agent action may cross into
           consequence unless it carries:
           1. provenance label,
           2. human-root chain,
           3. bounded intent seal,
           4. risk classification,
           5. audit receipt."

        Operationalization:
          - UNKNOWN_ORIGIN is fail-secure: cannot cross C1+ (HOLD)
          - AI_DRAFT at C3+ cannot cross into consequence (HOLD)
          - AI_AGENT_ACTION at C4+ requires signature (F1_AMANAH_ZKPC)
          - HUMAN_DIRECT/HUMAN_ASSISTED_AI/AI_AGENT_ACTION must chain to did: human_root
        """
        # Rule 1: UNKNOWN_ORIGIN is fail-secure — cannot cross at all
        if self.provenance_class == ProvenanceClass.UNKNOWN_ORIGIN:
            if self.risk_class != RiskClass.C0:
                raise ValueError(
                    f"KERNEL RULE: UNKNOWN_ORIGIN is fail-secure. Cannot "
                    f"cross into C{self.risk_class.value[-1]}. Must declare "
                    f"provenance (HUMAN_DIRECT, HUMAN_ASSISTED_AI, AI_DRAFT, "
                    f"or AI_AGENT_ACTION) or downgrade to C0 (no consequence)."
                )

        # Rule 2: AI_DRAFT at C3+ cannot cross into consequence
        if self.provenance_class == ProvenanceClass.AI_DRAFT:
            if self.risk_class.requires_human_confirmation:
                raise ValueError(
                    f"KERNEL RULE: AI_DRAFT at C{self.risk_class.value[-1]}+ "
                    f"cannot cross into consequence. Must upgrade to "
                    f"HUMAN_DIRECT, HUMAN_ASSISTED_AI, or AI_AGENT_ACTION "
                    f"with bounded human intent seal. "
                    f"(Arif, 2026-06-06: 'AI may generate. "
                    f"Humans must authorize consequence.')"
                )

        # Rule 3: AI_AGENT_ACTION at C4+ requires signature
        if self.provenance_class == ProvenanceClass.AI_AGENT_ACTION:
            if self.risk_class.requires_zkpc_proof and not self.signature:
                raise ValueError(
                    f"KERNEL RULE: AI_AGENT_ACTION at C{self.risk_class.value[-1]}+ "
                    f"requires cryptographic signature (F1_AMANAH_ZKPC path). "
                    f"Agent acting without human signature cannot cross into "
                    f"high-stakes consequence."
                )

        # Rule 4: human-attributable provenance must chain to a did: human_root
        if self.provenance_class.requires_human_root_chain:
            if not self.human_root or not self.human_root.startswith("did:"):
                raise ValueError(
                    f"KERNEL RULE: {self.provenance_class.value} must chain "
                    f"to a did: human_root. Provenance without human attribution "
                    f"is fabrication."
                )

        return self

    # ============================================================================
    # CANONICALIZATION + COMMITMENT
    # ============================================================================

    def canonical_bytes(self) -> bytes:
        d = self.model_dump(mode="json", exclude={"signature"})
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def commitment(self) -> str:
        """Blake3 commitment, matching v1-alpha ZKPC in core/shared/crypto.py."""
        return blake3.blake3(self.canonical_bytes()).hexdigest()

    def summary(self) -> dict[str, Any]:
        return {
            "provenance_class": self.provenance_class.value,
            "human_root": self.human_root,
            "actor": self.actor,
            "agent": self.agent,
            "action": self.action,
            "object": self.object,
            "risk_class": self.risk_class.value,
            "risk_external": self.risk_external,
            "risk_reversibility": self.risk_reversibility.value,
            "blast_radius": self.risk_blast_radius,
            "expires_at": self.expires_at.isoformat(),
            "nonce": self.nonce[:12] + "...",
            "scar_acknowledged": self.sovereign_provenance.scar_acknowledged,
            "lessons_active_count": len(self.sovereign_provenance.lessons_active),
            "has_signature": self.signature is not None,
            "commitment": self.commitment()[:16] + "...",
            "display_hash_matches": self.display_card.display_hash() == self.display_hash,
        }


# ============================================================================
# DEMO
# ============================================================================


if __name__ == "__main__":
    from datetime import timedelta

    print("=" * 78)
    print("INTENT ENVELOPE v1 — DEMO (HUMAN_ASSISTED_AI, C3, with scar)")
    print("=" * 78)
    card = DisplayCard(
        action="publish_report",
        object="kelantan-block-a-summary.pdf",
        agent="GEOX-Agent-07",
        blast_radius="public_reputation",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        scope={"spend_limit": "RM0", "network": "publish-only"},
    )
    env = IntentEnvelopeV1(
        human_root="did:web:arif-fazil.com",
        actor="Muhammad Arif bin Fazil",
        agent="GEOX-Agent-07",
        action="publish_report",
        object="kelantan-block-a-summary.pdf",
        scope={"spend_limit": "RM0", "network": "publish-only"},
        risk_class=RiskClass.C3,
        risk_external=True,
        risk_reversibility=Reversibility.PARTIAL,
        risk_blast_radius="public_reputation",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        nonce="abc123def456",
        display_card=card,
        display_hash=card.display_hash(),
        provenance_class=ProvenanceClass.HUMAN_ASSISTED_AI,
        sovereign_provenance=SovereignProvenance(
            scar_acknowledged=True,
            prior_reversals=[
                "refused to publish a claim without QC verified in 2024-Q3",
            ],
            lessons_active=[
                "verify downstream effect before authorizing external publish",
                "always check display_hash equals what I actually saw",
            ],
            attestation=(
                "I have read the display card. I am aware this is a "
                "HUMAN_ASSISTED_AI C3 public publish with partial "
                "reversibility. I bring the lessons of 2024-Q3 and 2026-06-05. "
                "I sign with that awareness present."
            ),
        ),
    )
    import pprint

    pprint.pprint(env.summary())
    print()
    print(f"commitment   : {env.commitment()}")
    print(f"kernel rule  : PASS (HUMAN_ASSISTED_AI + C3 with scar)")
    print()
    print("AI may generate. Humans must authorize consequence.")
    print("DITEMPA BUKAN DIBERI.")
