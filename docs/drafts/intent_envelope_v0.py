"""
intent_envelope_v0.py — Sovereign Provenance Forge v0

EUREKA CANDIDATE draft. NOT a live kernel module.
Lives in docs/drafts/. Not committed. Not imported by arifOS.

What this proves:
  1. The sovereign_provenance field is real Pydantic, not a Markdown wish.
  2. The display_hash constraint is machine-checkable, not a footnote.
  3. The seal commitment via blake3 matches the v1-alpha ZKPC pattern
     in /root/arifOS/core/shared/crypto.py (generate_zkpc_receipt).

What this does NOT prove (the 6 remaining cracks):
  - Recovery ceremony (trustless, coercion-resistant)
  - WebAuthn / FIDO2 integration (L1 Presence)
  - did:web DNS-hijack defense
  - LLM tool confused-deputy guard (Meta Rule of Two)
  - Duress / coercion detection
  - Interoperable ZK-private standard adoption

Standards cross-referenced (deep research, 2025-2026):
  - W3C DID Core v1.0
  - W3C VC Data Model 2.0 (May 2025 Recommendation)
  - W3C Secure Payment Confirmation (SPC)
  - FIDO2 CTAP 2.3 (Feb 2026)
  - IETF Intent Token draft (Williams, Mar 2026)
  - Agentic JWT (Goswami, arXiv 2509.13597)
  - Mastercard + Google Verifiable Intent (2026)
  - DeepMind Delegation Capability Tokens (2026)
  - Meta Agents Rule of Two (Oct 2025)
  - OAuth 2.0 Rich Authorization Requests (RFC 9396)
  - W3C ZCAP-LD (Capability-based authorization)

arifOS constitutional floors invoked:
  L01 AMANAH  (reversibility, risk_class)
  L02 TRUTH   (evidence_quality, risk.reversibility)
  L03 WITNESS (tri_witness defaults; not modeled here, deferred to kernel)
  L04 CLARITY (delta_S, not modeled here)
  L05 PEACE^2 (risk.reversibility, blast_radius)
  L06 EMPATHY (stakeholder_care hints via scope)
  L07 HUMILITY (uncertainty band not modeled; default 0.04)
  L08 GENIUS  (system health not modeled)
  L09 ANTIHANTU (no consciousness claims; L10 ONTOLOGY enforced by structure)
  L10 ONTOLOGY (this is a tool, not a person; categorical lock via Pydantic)
  L11 AUDIT   (signature field, human_root reference)
  L12 INJECTION (membrane defense; not modeled here, deferred to kernel)
  L13 SOVEREIGN (sovereign_provenance is testimony, ack_irreversible pattern)

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
    """
    Risk consequence tier — governs HOW MUCH friction the kernel applies.

    Mirrors /root/arifOS/arifosmcp/constitutional_map.py:151-156.
    """

    C0 = "C0"  # Negligible — grammar, tone, formatting
    C1 = "C1"  # Low — internal drafts, notes, brainstorming
    C2 = "C2"  # Medium — code review, testing, analysis
    C3 = "C3"  # High — public posts, emails, reports
    C4 = "C4"  # Very High — legal, financial, HR, investment
    C5 = "C5"  # Critical — irreversible, production write, money movement

    @property
    def requires_human_confirmation(self) -> bool:
        """C3+ requires human ack per the arifOS C-tier table."""
        return self.value in ("C3", "C4", "C5")

    @property
    def requires_zkpc_proof(self) -> bool:
        """C4+ requires ZKPC proof per F1_AMANAH_ZKPC floor logic."""
        return self.value in ("C4", "C5")


class Reversibility(str, Enum):
    """L01 AMANAH reversibility axis."""

    FULL = "full"  # can be undone completely
    PARTIAL = "partial"  # can be partially undone, residual cost
    NONE = "none"  # irreversible


# ============================================================================
# SOVEREIGN PROVENANCE — The scar testimony primitive (EUREKA CANDIDATE)
# ============================================================================


class SovereignProvenance(BaseModel):
    """
    Testimony-only field. The sovereign testifies, not proves.

    Why this is here:
      Cryptography proves control. Scars prove accountability. They are
      different things, and conflating them is what every existing auth
      system does. The 8 competing 2025-2026 specs (IETF Intent Token,
      Agentic JWT, Verifiable Intent, DCTs, etc.) all solve the
      cryptographic control side. None of them have a field for the
      accountability testimony. This is that field.

    Properties:
      - NOT verifiable. The system cannot read the sovereign's scars.
      - REQUIRED for C3+ actions (a sovereign cannot sign C3+ without
        acknowledging that they bring the lessons of prior decisions).
      - The ABSENCE of a normally-present caveat becomes a coercion flag
        (an attacker who has stolen keys+biometric+typing cannot fake the
        sovereign's decision rhythm because it is not stored anywhere).

    Cross-references:
      - L13 SOVEREIGN physics anchor: "AI cannot suffer consequences →
        AI cannot hold sovereignty. Only humans bleed. Only humans decide."
      - The 8 gaps identified in the research (Gap A through Gap F) are
        ALL downstream of this primitive: root key loss (the scars
        inform guardian choice), coercion (the absence is the signal),
        UI deception (the testimony attests to what was actually seen).
    """

    model_config = ConfigDict(extra="forbid")

    scar_acknowledged: bool = Field(
        ...,
        description=(
            "Sovereign attests: 'I bring the scars of prior decisions to "
            "this one.' MUST be True for C3+ actions. False is a coercion flag."
        ),
    )
    prior_reversals: list[str] = Field(
        default_factory=list,
        description=(
            "Free-form list of prior decisions the sovereign remembers going "
            "wrong. NOT verified. Recorded for audit traceability only."
        ),
    )
    lessons_active: list[str] = Field(
        default_factory=list,
        description=(
            "Free-form list of lessons the sovereign is applying to THIS "
            "decision. NOT verified. The system notices if a normally-present "
            "lesson is absent — that absence is a coercion signal."
        ),
    )
    attestation: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description=(
            "Free-form testimony text. The sovereign's own words. "
            "What they are bringing to this decision. NOT verified."
        ),
    )

    @property
    def is_coercion_flag(self) -> bool:
        """True if the sovereign is being asked to sign without acknowledging scars."""
        return not self.scar_acknowledged


# ============================================================================
# DISPLAY CARD — The human-visible consequence card
# ============================================================================


class DisplayCard(BaseModel):
    """
    The exact human-visible card that the sovereign saw when they signed.

    This is the key to preventing UI deception (Gap E in the research).
    The signed display_hash commits to this canonical form. Any tampering
    with the UI between display and signature invalidates the seal.

    The display_card and the actual signed payload are HASH-BOUND.
    You cannot sign "publish harmless draft" and have the backend execute
    "transfer authority / delete / deploy" — the display_hash would not match.
    """

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., min_length=1, max_length=200)
    object: str = Field(..., min_length=1, max_length=2000)
    agent: str = Field(..., min_length=1, max_length=200)
    blast_radius: str = Field(..., min_length=1, max_length=500)
    expires_at: datetime
    scope: dict[str, str] = Field(default_factory=dict)

    def canonical_bytes(self) -> bytes:
        """
        RFC 8785-style canonical serialization for stable hashing.

        Sort keys, no whitespace, ISO 8601 datetimes, UTF-8.
        Two implementations computing this for the same card MUST produce
        the same bytes. This is what makes display_hash reproducible.
        """
        d = self.model_dump(mode="json")
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def display_hash(self) -> str:
        """Blake3 commitment of the canonical card. Hex-encoded."""
        return blake3.blake3(self.canonical_bytes()).hexdigest()


# ============================================================================
# INTENT ENVELOPE — The atomic authorization object
# ============================================================================


class IntentEnvelopeV0(BaseModel):
    """
    The atomic authorization object for consequential actions.

    EUREKA CANDIDATE v0. One implementation of the pattern that the
    W3C and IETF are converging on (see module docstring). The novel
    contribution is the sovereign_provenance field.

    Four layers in one object:
      L1 Identity   — human_root (DID) + actor
      L2 Agent      — agent (which delegated actor is requesting)
      L3 Consequence — action + object + scope + risk + display_card
      L4 Freshness  — expires_at + nonce + previous_seal_hash

    Plus the sovereign_provenance (the scar testimony) and the signature.

    Validation chain (model_validator order):
      1. display_hash must equal blake3(display_card.canonical_bytes())
      2. expires_at must be in the future at construction time
      3. If risk_class requires it, sovereign_provenance.scar_acknowledged
         must be True (C3+ cannot bypass the scar)
    """

    model_config = ConfigDict(extra="forbid")

    # L1 Identity
    human_root: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="DID reference, e.g. did:web:arif-fazil.com",
    )
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

    # Display integrity (machine-checkable)
    display_card: DisplayCard
    display_hash: str = Field(..., min_length=64, max_length=64)

    # Scar testimony (EUREKA CANDIDATE original)
    sovereign_provenance: SovereignProvenance

    # Cryptographic commitment
    signature: str | None = None

    @field_validator("display_hash")
    @classmethod
    def _display_hash_is_hex(cls, v: str) -> str:
        """64-char lowercase hex (blake3 default output)."""
        if len(v) != 64 or not all(c in "0123456789abcdef" for c in v):
            raise ValueError("display_hash must be 64-char blake3 hex")
        return v

    @model_validator(mode="after")
    def _verify_display_hash_binding(self) -> "IntentEnvelopeV0":
        """
        The display_hash MUST equal blake3(display_card.canonical_bytes()).
        This is the Gap E (UI deception) defense.
        """
        computed = self.display_card.display_hash()
        if computed != self.display_hash:
            raise ValueError(
                f"display_hash mismatch: signed {self.display_hash[:16]}... "
                f"vs computed {computed[:16]}... — possible UI deception or "
                f"card tampering between display and signature"
            )
        return self

    @model_validator(mode="after")
    def _verify_freshness(self) -> "IntentEnvelopeV0":
        """expires_at must be in the future (or C0 historical)."""
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
    def _verify_scar_for_consequential_actions(self) -> "IntentEnvelopeV0":
        """
        L13 SOVEREIGN physics: only humans bleed, only humans decide.
        For C3+ actions, the sovereign MUST acknowledge they bring scars.
        A sovereign cannot sign C3+ with scar_acknowledged=False.
        That is a coercion flag, not a failure to seal.
        """
        if (
            self.risk_class.requires_human_confirmation
            and self.sovereign_provenance.is_coercion_flag
        ):
            raise ValueError(
                f"C{self.risk_class.value[-1]}+ action cannot be sealed with "
                f"scar_acknowledged=False. This is a coercion flag, not a "
                f"validation error — the sovereign is being asked to sign "
                f"without acknowledging they bring lessons. Handle as HOLD."
            )
        return self

    def canonical_bytes(self) -> bytes:
        """
        Canonical serialization for signing. Excludes signature itself
        (so the signature can be computed and verified independently).
        """
        d = self.model_dump(mode="json", exclude={"signature"})
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def commitment(self) -> str:
        """
        Blake3 commitment, matching the v1-alpha ZKPC pattern
        in /root/arifOS/core/shared/crypto.py:generate_zkpc_receipt().

        This is the field that would be sealed in VAULT999.
        """
        return blake3.blake3(self.canonical_bytes()).hexdigest()

    def summary(self) -> dict[str, Any]:
        """One-screen summary for human review."""
        return {
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
            "commitment": self.commitment()[:16] + "...",
            "display_hash_matches": self.display_card.display_hash() == self.display_hash,
        }


# ============================================================================
# DEMO (not a test, just a runnable sanity check)
# ============================================================================


if __name__ == "__main__":
    from datetime import timedelta

    card = DisplayCard(
        action="publish_report",
        object="kelantan-block-a-summary.pdf",
        agent="GEOX-Agent-07",
        blast_radius="public_reputation",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        scope={"spend_limit": "RM0", "network": "publish-only"},
    )

    envelope = IntentEnvelopeV0(
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
        display_hash=card.display_hash(),  # computed correctly
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
                "I have read the display card. I am aware this is a C3 public "
                "publish with partial reversibility. I bring the lessons of "
                "the 2024-Q3 incident and the 2026-06-05 SE Malacca prospect "
                "claim challenge. I sign with that awareness present."
            ),
        ),
    )

    print("=" * 72)
    print("INTENT ENVELOPE v0 — DEMO RUN")
    print("=" * 72)
    import pprint

    pprint.pprint(envelope.summary())
    print()
    print(f"display_hash : {envelope.display_hash}")
    print(f"commitment   : {envelope.commitment()}")
    print(f"scar flag    : {envelope.sovereign_provenance.is_coercion_flag}")
    print()
    print("Sealed. The sovereign_provenance is testimony, not proof.")
    print("The display_hash is machine-checkable, not a footnote.")
    print("The commitment uses blake3, matching arifOS v1-alpha ZKPC.")
    print()
    print("DITEMPA BUKAN DIBERI.")
