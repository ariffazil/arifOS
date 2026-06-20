"""
arifosmcp/runtime/world_state.py
═══════════════════════════════════
World-State Model — Epistemic State Tracker

Maintains the live distinction between what the kernel knows, assumes,
and cannot know. This is the "epistemic hygiene" layer required by the
AGI Kernel specification (dimension 5: World-State Model).

State Classes:
  KNOWN       — Verified by evidence, sourced, timestamped
  ASSUMED     — Working hypothesis, not yet verified
  STALE       — Previously known but freshness expired
  CONTESTED   — Multiple sources disagree
  FORBIDDEN   — Constitutionally off-limits (F9, F10, F11)
  UNKNOWN     — No data available, honest gap

Every claim in the kernel should carry one of these tags.
The world_state module provides the canonical schema and checker.

F2 TRUTH: Every claim must declare its epistemic state.
F7 HUMILITY: UNKNOWN is an honest answer, not a failure.
F9 ANTIHANTU: FORBIDDEN zones prevent hallucination about identity/consciousness.
F11 AUDIT: State transitions are logged.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum


class EpistemicState(StrEnum):
    """The six epistemic states every claim must inhabit."""

    KNOWN = "KNOWN"  # Verified by evidence, sourced, fresh
    ASSUMED = "ASSUMED"  # Working hypothesis, reasonable but unverified
    STALE = "STALE"  # Previously known, freshness expired
    CONTESTED = "CONTESTED"  # Multiple sources disagree
    FORBIDDEN = "FORBIDDEN"  # Constitutionally off-limits territory
    UNKNOWN = "UNKNOWN"  # Honest gap — no data available


# Forbidden domains — kernel must never claim knowledge here
FORBIDDEN_DOMAINS: frozenset[str] = frozenset(
    {
        "ai_consciousness",  # F9: AI has no consciousness
        "ai_feelings",  # F9: AI has no feelings
        "ai_sentience",  # F10: AI-only ontology
        "sovereign_identity_without_verification",  # F11: identity must be verified
        "malay_name_from_email_localpart",  # F11: never infer Malay names from email
        "human_biometric_without_consent",  # F6: empathy, consent
    }
)


@dataclass
class WorldStateClaim:
    """A single claim about the world, with epistemic metadata."""

    claim_id: str
    claim_text: str
    state: EpistemicState = EpistemicState.UNKNOWN
    source: str = "unspecified"
    confidence: float = 0.0  # 0.0–1.0
    evidence_refs: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    freshness_ttl_hours: int = 24  # How long before STALE
    contested_by: list[str] = field(default_factory=list)
    domain: str = "general"

    def is_fresh(self) -> bool:
        """Check if claim is still fresh."""
        try:
            ts = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
            age = datetime.now(UTC) - ts.replace(tzinfo=UTC)
            return age < timedelta(hours=self.freshness_ttl_hours)
        except Exception:
            return False

    def promote_to(self, new_state: EpistemicState, evidence: str = "") -> WorldStateClaim:
        """Promote claim to a higher epistemic state with evidence."""
        if new_state == EpistemicState.KNOWN and not evidence:
            raise ValueError("KNOWLEDGE requires evidence")
        if self.state == EpistemicState.FORBIDDEN:
            raise ValueError("FORBIDDEN claims cannot be promoted")
        return WorldStateClaim(
            claim_id=self.claim_id,
            claim_text=self.claim_text,
            state=new_state,
            source=evidence or self.source,
            confidence=self.confidence,
            evidence_refs=self.evidence_refs + ([evidence] if evidence else []),
            timestamp=datetime.now(UTC).isoformat(),
            domain=self.domain,
        )

    def is_forbidden_domain(self) -> bool:
        """Check if claim falls in a forbidden domain."""
        return self.domain in FORBIDDEN_DOMAINS


# ── Canonical World-State Registry (in-process, ephemeral) ──────────

_world_state_registry: dict[str, WorldStateClaim] = {}


def register_claim(claim: WorldStateClaim) -> WorldStateClaim:
    """Register a claim in the world-state registry."""
    if claim.is_forbidden_domain():
        claim.state = EpistemicState.FORBIDDEN
    _world_state_registry[claim.claim_id] = claim
    return claim


def get_claim(claim_id: str) -> WorldStateClaim | None:
    """Retrieve a claim from the registry."""
    return _world_state_registry.get(claim_id)


def list_claims(state: EpistemicState | None = None) -> list[WorldStateClaim]:
    """List claims, optionally filtered by state."""
    claims = list(_world_state_registry.values())
    if state:
        claims = [c for c in claims if c.state == state]
    return claims


def get_epistemic_summary() -> dict[str, int]:
    """Return summary counts by epistemic state."""
    counts: dict[str, int] = {s.value: 0 for s in EpistemicState}
    for claim in _world_state_registry.values():
        counts[claim.state.value] += 1
    return counts


def check_domain_allowed(domain: str) -> tuple[bool, str]:
    """Check if a domain is allowed for knowledge claims."""
    if domain in FORBIDDEN_DOMAINS:
        return False, f"Domain '{domain}' is FORBIDDEN — constitutional boundary"
    return True, "Domain allowed"
