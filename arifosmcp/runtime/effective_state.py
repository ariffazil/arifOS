"""
effective_state.py — WAJIB 3: Kernel State Normalization (2026-07-19)
══════════════════════════════════════════════════════════════════════

Single canonical effective_state — all authority-bearing fields derive
from this single source. Eliminates the 8-field dual-source problem
documented in session.py:554-568.

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AuthorityBand(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    SUGGEST = "SUGGEST"
    DRAFT = "DRAFT"
    EXECUTE_REVERSIBLE = "EXECUTE_REVERSIBLE"
    LIMITED_MUTATE = "LIMITED_MUTATE"
    MUTATE = "MUTATE"
    SOVEREIGN = "SOVEREIGN"


class EffectiveVerdict(str, Enum):
    FULL = "FULL"
    LIMITED = "LIMITED"
    HOLD = "HOLD"
    DENIED = "DENIED"


@dataclass
class EffectiveState:
    """Single canonical authority state per WAJIB 3.

    All authority-bearing fields (session_birth.authority_mode,
    session_birth.verdict, session_birth.mutation_allowed,
    clarity_contract.authority_band, actor.authority_state, etc.)
    MUST derive from this single source or be removed.
    """

    actor_verified: bool = False
    authority_band: AuthorityBand = AuthorityBand.OBSERVE_ONLY
    mutation_allowed: bool = False
    seal_allowed: bool = False
    verdict: EffectiveVerdict = EffectiveVerdict.HOLD
    reason: str = "ACTOR_NOT_VERIFIED"
    derived_from: str = "session_capability_token_v1"
    computed_at: float = field(default_factory=time.time)


def compute_effective_state(
    actor_verified: bool = False,
    session_token_present: bool = False,
    lease_valid: bool = False,
    requested_authority: str = "OBSERVE_ONLY",
    actor_role: str = "anonymous",
) -> EffectiveState:
    """Compute the single canonical effective_state from input signals.

    This replaces the 8-field dual-source problem documented in WAJIB 3.
    All downstream authority fields must derive from this single source.

    Args:
        actor_verified: Has the actor been identity-verified?
        session_token_present: Is a valid SCT present?
        lease_valid: Is there a valid lease for mutation?
        requested_authority: What the caller asked for
        actor_role: Actor's declared role
    """
    state = EffectiveState(actor_verified=actor_verified)

    # ── Compute authority band ──────────────────────────────────────
    if actor_role == "sovereign" and actor_verified:
        state.authority_band = AuthorityBand.SOVEREIGN
        state.verdict = EffectiveVerdict.FULL
        state.mutation_allowed = True
        state.seal_allowed = True
        state.reason = "SOVEREIGN_VERIFIED"
    elif actor_verified and lease_valid:
        try:
            band = AuthorityBand(requested_authority)
            if band in (AuthorityBand.MUTATE, AuthorityBand.SOVEREIGN):
                state.authority_band = AuthorityBand.MUTATE
                state.seal_allowed = True
            else:
                state.authority_band = band
                state.seal_allowed = False
        except ValueError:
            state.authority_band = AuthorityBand.OBSERVE_ONLY
            state.seal_allowed = False
        state.verdict = EffectiveVerdict.FULL
        state.mutation_allowed = True
        state.reason = "LEASE_AUTHORIZED"
    elif actor_verified and session_token_present:
        state.authority_band = AuthorityBand.OBSERVE_ONLY
        state.verdict = EffectiveVerdict.LIMITED
        state.mutation_allowed = False
        state.seal_allowed = False
        state.reason = "OBSERVE_ONLY_SESSION"
    elif session_token_present:
        state.authority_band = AuthorityBand.OBSERVE_ONLY
        state.verdict = EffectiveVerdict.HOLD
        state.mutation_allowed = False
        state.seal_allowed = False
        state.reason = "UNVERIFIED_SESSION"
    else:
        state.authority_band = AuthorityBand.OBSERVE_ONLY
        state.verdict = EffectiveVerdict.HOLD
        state.mutation_allowed = False
        state.seal_allowed = False
        state.reason = "ANONYMOUS"

    return state


def is_self_contradictory(state: EffectiveState) -> bool:
    """WAJIB 3 conformance check: detect contradictory authority states.

    Returns True if the state contains contradictions that would
    have been possible under the old 8-field dual-source system.
    """
    contradictions = []

    # mutation_allowed without authority
    if state.mutation_allowed and state.authority_band == AuthorityBand.OBSERVE_ONLY:
        contradictions.append("mutation_allowed=True but OBSERVE_ONLY")

    # seal_allowed without SOVEREIGN or FULL
    if state.seal_allowed and state.authority_band not in (AuthorityBand.SOVEREIGN, AuthorityBand.MUTATE):
        contradictions.append("seal_allowed=True but not SOVEREIGN or FULL")

    # FULL verdict without verification
    if state.verdict == EffectiveVerdict.FULL and not state.actor_verified:
        contradictions.append("verdict=FULL but actor not verified")

    return len(contradictions) > 0


def to_dict(state: EffectiveState) -> dict[str, Any]:
    """Serialize the effective state to the canonical JSON format."""
    return {
        "actor_verified": state.actor_verified,
        "authority_band": state.authority_band.value,
        "mutation_allowed": state.mutation_allowed,
        "seal_allowed": state.seal_allowed,
        "verdict": state.verdict.value,
        "reason": state.reason,
        "derived_from": state.derived_from,
        "computed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(state.computed_at)),
    }
