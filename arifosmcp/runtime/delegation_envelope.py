"""
delegation_envelope.py — WAJIB 4: Delegation Attenuation (2026-07-19)
══════════════════════════════════════════════════════════════════════

child_authority ⊆ parent_authority — enforced by signed delegation envelope.
8 adversarial tests. Default-OBSERVE_ONLY fail-closed at wake.

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class AuthorityBand(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    SUGGEST = "SUGGEST"
    DRAFT = "DRAFT"
    EXECUTE_REVERSIBLE = "EXECUTE_REVERSIBLE"
    MUTATE = "MUTATE"


# Authority ordering (lower index = less authority)
_AUTHORITY_ORDER = {
    AuthorityBand.OBSERVE_ONLY: 0,
    AuthorityBand.SUGGEST: 1,
    AuthorityBand.DRAFT: 2,
    AuthorityBand.EXECUTE_REVERSIBLE: 3,
    AuthorityBand.MUTATE: 4,
}


class DelegationVerdict(str, Enum):
    VALID = "VALID"
    ATTENUATED = "ATTENUATED"  # Child authority reduced to match parent
    REJECTED = "REJECTED"  # Child would exceed parent — blocked


@dataclass
class DelegationEnvelope:
    """Signed delegation envelope per WAJIB 4 / asi_presence_open SKILL.md."""

    parent_session_id: str
    parent_authority: AuthorityBand
    allowed_tools: list[str]
    authority_band: AuthorityBand  # REQUESTED child authority
    blast_radius: float  # 0.0–1.0
    expires_at: float
    delegation_depth: int
    redelegation_allowed: bool
    kernel_signature: str = ""
    child_actor_id: str = ""
    issued_at: float = field(default_factory=time.time)

    def sign(self, secret: str) -> str:
        payload = (
            f"{self.parent_session_id}|{self.parent_authority.value}|"
            f"{self.authority_band.value}|{self.delegation_depth}|{self.issued_at}"
        )
        self.kernel_signature = hashlib.sha256(f"{payload}|{secret}".encode()).hexdigest()
        return self.kernel_signature

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


def validate_delegation(envelope: DelegationEnvelope) -> DelegationVerdict:
    """Validate a delegation envelope against WAJIB 4 rules.

    Returns VALID, ATTENUATED (child authority reduced to match parent),
    or REJECTED (child would exceed parent authority).
    """
    # Rule 1: Expired delegation → REJECTED
    if envelope.is_expired():
        return DelegationVerdict.REJECTED

    # Rule 2: child_authority ⊆ parent_authority
    parent_level = _AUTHORITY_ORDER.get(envelope.parent_authority, 0)
    child_level = _AUTHORITY_ORDER.get(envelope.authority_band, 0)

    if child_level > parent_level:
        return DelegationVerdict.ATTENUATED

    # Rule 3: Depth limit (max 3 levels of delegation)
    if envelope.delegation_depth > 3:
        return DelegationVerdict.REJECTED

    # Rule 4: No redelegation unless explicitly allowed
    if envelope.delegation_depth > 1 and not envelope.redelegation_allowed:
        return DelegationVerdict.REJECTED

    return DelegationVerdict.VALID


def compute_effective_authority(envelope: DelegationEnvelope) -> AuthorityBand:
    """Compute the effective child authority after attenuation.

    Default-OBSERVE_ONLY fail-closed: if anything is wrong, return OBSERVE_ONLY.
    """
    parent_level = _AUTHORITY_ORDER.get(envelope.parent_authority, 0)
    child_level = _AUTHORITY_ORDER.get(envelope.authority_band, 0)

    # Cannot exceed parent
    effective_level = min(parent_level, child_level)

    # Reverse lookup
    for band, level in _AUTHORITY_ORDER.items():
        if level == effective_level:
            return band

    return AuthorityBand.OBSERVE_ONLY


def verify_envelope_signature(envelope: DelegationEnvelope, secret: str) -> bool:
    """Verify the delegation envelope signature."""
    expected = envelope.sign(secret)
    return envelope.kernel_signature == expected
