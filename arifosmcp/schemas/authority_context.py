"""
arifosmcp/schemas/authority_context.py — CANONICAL AUTHORITY CONTEXT (P1)
═══════════════════════════════════════════════════════════════════════

Single immutable authority token — issued once at arif_init, read everywhere.
Replaces 48 scattered authority/identity modules.

Forged: 2026-07-26 under Arif's P1 directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any, Literal

AuthorityLevel = Literal[
    "SOVEREIGN",
    "TRUSTED_AGENT",
    "EXECUTOR",
    "OBSERVER",
    "ANONYMOUS",
    "OBSERVE_ONLY",
]

RiskCeiling = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

ProofMethod = Literal["ed25519", "session_token", "sct_v1", "anon"]


@dataclass(frozen=True)
class AuthorityContext:
    """Immutable authority snapshot — read-only after creation.

    One canonical answer to "who may do what?" No module recomputes sovereignty.
    """

    actor_id: str
    session_id: str
    proof_method: ProofMethod = "session_token"
    authority_level: AuthorityLevel = "OBSERVE_ONLY"
    actor_verified: bool = False
    capability_scope: tuple[str, ...] = field(default_factory=tuple)
    risk_ceiling: RiskCeiling = "MEDIUM"
    sovereign_required: bool = False
    sovereign_acknowledged: bool = False
    issued_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str | None = None
    receipt_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capability_scope"] = list(self.capability_scope)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthorityContext:
        return cls(
            actor_id=data.get("actor_id", "anonymous"),
            session_id=data.get("session_id", ""),
            proof_method=data.get("proof_method", "session_token"),
            authority_level=data.get("authority_level", "OBSERVE_ONLY"),
            actor_verified=data.get("actor_verified", False),
            capability_scope=tuple(data.get("capability_scope", ())),
            risk_ceiling=data.get("risk_ceiling", "MEDIUM"),
            sovereign_required=data.get("sovereign_required", False),
            sovereign_acknowledged=data.get("sovereign_acknowledged", False),
            issued_at=data.get("issued_at", ""),
            expires_at=data.get("expires_at"),
            receipt_ref=data.get("receipt_ref"),
        )

    @classmethod
    def anonymous(cls, session_id: str = "") -> AuthorityContext:
        """Create a minimal authority context for anonymous/read-only access."""
        return cls(
            actor_id="anonymous",
            session_id=session_id,
            authority_level="ANONYMOUS",
            proof_method="anon",
        )

    def can_mutate(self) -> bool:
        """F1 AMANAH gate: mutation only at EXECUTOR or above."""
        return self.actor_verified and self.authority_level in (
            "SOVEREIGN",
            "TRUSTED_AGENT",
            "EXECUTOR",
        )

    def can_observe(self) -> bool:
        """Any level can observe."""
        return True

    def can_judge(self) -> bool:
        """Judgment requires TRUSTED_AGENT or SOVEREIGN."""
        return self.actor_verified and self.authority_level in (
            "SOVEREIGN",
            "TRUSTED_AGENT",
        )

    def can_seal(self) -> bool:
        """Sealing requires SOVEREIGN authority."""
        return self.authority_level == "SOVEREIGN" and self.actor_verified

    def requires_sovereign(self) -> bool:
        """True if F13 acknowledgment is pending."""
        return self.sovereign_required and not self.sovereign_acknowledged

    def is_valid(self) -> bool:
        """Check if this authority has not expired."""
        if self.expires_at:
            try:
                expiry = datetime.fromisoformat(self.expires_at)
                if datetime.now(UTC) > expiry.astimezone(UTC):
                    return False
            except (ValueError, TypeError):
                pass
        return bool(self.actor_id) and bool(self.session_id)

    def __repr__(self) -> str:
        scope = ",".join(self.capability_scope[:3])
        more = "+" if len(self.capability_scope) > 3 else ""
        return (
            f"AuthorityContext({self.actor_id}/{self.session_id[:12]}... "
            f"level={self.authority_level} verified={self.actor_verified} "
            f"scope=[{scope}{more}] mut={self.can_mutate()})"
        )
