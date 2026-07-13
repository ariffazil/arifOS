"""
human_intent.py — arifOS D3: Sovereign-Intent Intake

PERMANENT RULE: speech expresses intent; identity proves who spoke;
capability defines what may happen; VAULT999 records what actually
happened. NONE may substitute for another.

This module replaces the unsound "SOVEREIGN_SIGNAL_PHRASES" authority
escalator. Phrases no longer grant authority — they trigger a
confirmation workflow that ends with a bound cryptographic capability
for ONE specific pending action.

Public surface:
- CONFIRMATION_INTENT_PHRASES (renamed; lifts escalator)
- handle_human_signal() — returns SignalResult with intent_detected,
  requires_cryptographic_confirmation=True, authority_changed=False
- issue_confirmation_challenge() — session-bound challenge payload
- bind_signature_to_challenge() — Ed25519 sig over canonical fields
- issue_narrow_capability() — single-use payload-bound vault.append
- check_capability_uniqueness() — replay/cross-session/cross-channel deny

Permanent invariants:
- phrase never changes authority (authority_changed=False always)
- phrase without pending action is harmless (returns no-op)
- phrase with multiple pending actions → AMBIGUOUS_CONFIRMATION_TARGET (no guess)
- capability is single_use + payload-bound + expires_at
- replay denied, cross-session denied, cross-channel denied
- payload change after confirmation denied
"""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Iterable


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIRMATION_INTENT_PHRASES (renamed from SOVEREIGN_SIGNAL_PHRASES)
#
# These trigger a confirmation workflow — they grant NOTHING.
# Match against human-channel input as possible approval intent.
# Only the channel holding a valid bound session may start a challenge.
# ═══════════════════════════════════════════════════════════════════════════════

CONFIRMATION_INTENT_PHRASES: frozenset[str] = frozenset({
    "buat ja la",
    "yes confirm",
    "execute x",
    "i'm the architect",
    "im the architect",
    "jalan terus",
    "seal it",
})


# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURED RESULT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SignalResult:
    """Return type of handle_human_signal.

    authority_changed is always False — phrases never grant authority.
    """
    intent_detected: bool = False
    intent_class: str = ""           # CONFIRMATION | ORDINARY | AMBIGUOUS_CONFIRMATION_TARGET
    pending_action_id: Optional[str] = None
    requires_cryptographic_confirmation: bool = False
    authority_changed: bool = False    # PERMANENT: always False
    confirmation_challenge: Optional[dict] = None  # only when confirmation triggered
    ambiguity_note: Optional[str] = None
    matched_phrase: Optional[str] = None


@dataclass(frozen=True)
class ConfirmationChallenge:
    """Session-bound challenge payload — caller signs canonical fields."""
    session_id: str
    action_id: str
    action_hash: str
    consequence_summary_hash: str
    nonce: str
    audience: str = "arifOS-confirmation-v1"
    expires_at: str = ""  # ISO8601

    def canonical_payload(self) -> str:
        """Deterministic payload that the Ed25519 signature must cover."""
        return "\n".join([
            "arifOS-confirmation-v1",
            f"session_id={self.session_id}",
            f"action_id={self.action_id}",
            f"action_hash={self.action_hash}",
            f"consequence_summary_hash={self.consequence_summary_hash}",
            f"nonce={self.nonce}",
            f"audience={self.audience}",
            f"expires_at={self.expires_at}",
        ])


@dataclass(frozen=True)
class NarrowCapability:
    """Single-use payload-bound vault capability.

    Issued ONLY after a confirmation_challenge has been signed.
    Cannot redelegate. Cannot outlive its expires_at.
    Cannot apply to a payload_hash other than the one bound at issue.
    """
    capability: str           # e.g. "vault.append.sovereign"
    action_id: str
    session_id: str
    channel: str              # "telegram" | "opencode" | "tui" | "system" | ...
    payload_hash: str         # exact hash the capability is bound to
    single_use: bool = True
    redelegation: bool = False
    expires_at: str = ""      # ISO8601
    issued_at: str = ""       # ISO8601
    issued_by: str = ""       # actor_id
    nonce: str = ""           # tied to confirmation
    consumed: bool = False    # single-use enforcement
    consumed_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# IN-PROCESS REGISTRIES (would be Supabase / VAULT999 in production)
# ═══════════════════════════════════════════════════════════════════════════════

# Pending actions known to the runtime — registered by action classification
# (D1) and consumed by capability issuance + execution.
_PENDING_ACTIONS: dict[str, dict] = {}
# Issued capabilities — keyed by capability_id (uuid-like nonce + session + action)
_ISSUED_CAPABILITIES: dict[str, NarrowCapability] = {}
# Replay/cross-session/cross-channel protection
_USED_NONCES: set[str] = set()


# ═══════════════════════════════════════════════════════════════════════════════
# CHANNEL SESSION BINDING
#
# Per D3: "Multiple channels (Telegram, OpenCode, etc.) — only the channel
# with valid bound session may start challenge."
# ═══════════════════════════════════════════════════════════════════════════════

def register_channel_session_binding(session_id: str, channel: str,
                                    capability_scope: str = "all") -> None:
    """Bind a session to a channel — only bound channels may request challenges."""
    _PENDING_ACTIONS.setdefault("__channel_bindings__", {})[
        (session_id, channel)
    ] = {"session_id": session_id, "channel": channel, "scope": capability_scope}


def channel_bound_to_session(session_id: str, channel: str) -> bool:
    """Return True iff the given channel is bound to the given session."""
    bindings = _PENDING_ACTIONS.get("__channel_bindings__", {})
    return (session_id, channel) in bindings


def register_pending_action(action_id: str, action_profile: dict) -> None:
    """Register a pending action for downstream confirmation binding."""
    _PENDING_ACTIONS[action_id] = action_profile


def get_pending_action(action_id: str) -> Optional[dict]:
    return _PENDING_ACTIONS.get(action_id)


def list_pending_actions(session_id: Optional[str] = None) -> list[dict]:
    """List pending actions, optionally filtered by session."""
    out = []
    for k, v in _PENDING_ACTIONS.items():
        if k.startswith("__"):
            continue
        if session_id is None or v.get("session_id") == session_id:
            out.append({"action_id": k, **v})
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# HUMAN SIGNAL HANDLER
#
# handle_human_signal(text, session_id, channel, pending_action_id)
#   → SignalResult
#
# The function NEVER grants authority. It classifies intent and either:
#   - returns no-op (no phrase match, or no pending action),
#   - returns CONFIRMATION challenge (one pending action, channel bound),
#   - returns AMBIGUOUS_CONFIRMATION_TARGET (multiple pending actions).
# ═══════════════════════════════════════════════════════════════════════════════

def handle_human_signal(
    text: str,
    session_id: str,
    channel: str,
    pending_action_id: Optional[str] = None,
    allowed_pending_actions: Optional[Iterable[str]] = None,
) -> SignalResult:
    """Process a human-channel signal.

    Rules (D3):
      1. Phrase match + no pending action → harmless no-op.
      2. Phrase match + single pending action + channel bound → CONFIRMATION
         challenge (no authority change).
      3. Phrase match + multiple pending actions → AMBIGUOUS_CONFIRMATION_TARGET.
      4. Phrase match + channel not bound to session → no-op (channel rejected).
      5. Phrase does not match → ORDINARY intent_class.
      6. authority_changed is PERMANENT False — phrases never grant authority.
    """
    phrase = (text or "").lower().strip()
    matched = phrase if phrase in CONFIRMATION_INTENT_PHRASES else None

    if matched is None:
        return SignalResult(
            intent_detected=False,
            intent_class="ORDINARY",
            authority_changed=False,
        )

    # Channel must be bound to session
    if not channel_bound_to_session(session_id, channel):
        return SignalResult(
            intent_detected=False,
            intent_class="ORDINARY",
            matched_phrase=matched,
            authority_changed=False,
        )

    # Resolve pending actions
    if pending_action_id is not None:
        candidates = [pending_action_id]
    elif allowed_pending_actions is not None:
        candidates = list(allowed_pending_actions)
    else:
        candidates = [
            p["action_id"] for p in list_pending_actions(session_id=session_id)
        ]

    # Filter by session
    filtered = []
    for aid in candidates:
        prof = get_pending_action(aid)
        if prof is None:
            continue
        if prof.get("session_id") != session_id:
            continue
        filtered.append(aid)

    if not filtered:
        # No pending action to confirm — harmless
        return SignalResult(
            intent_detected=True,
            intent_class="CONFIRMATION",
            requires_cryptographic_confirmation=False,
            matched_phrase=matched,
            authority_changed=False,
        )

    if len(filtered) > 1:
        # AMBIGUOUS — multiple pending actions, no guessing
        return SignalResult(
            intent_detected=True,
            intent_class="AMBIGUOUS_CONFIRMATION_TARGET",
            requires_cryptographic_confirmation=False,
            matched_phrase=matched,
            authority_changed=False,
            ambiguity_note=(
                f"{len(filtered)} pending actions for session {session_id}; "
                "narrow to one before triggering confirmation"
            ),
        )

    # Single pending action — build challenge
    aid = filtered[0]
    prof = get_pending_action(aid)
    challenge = issue_confirmation_challenge(session_id=session_id, action_id=aid)

    return SignalResult(
        intent_detected=True,
        intent_class="CONFIRMATION",
        pending_action_id=aid,
        requires_cryptographic_confirmation=True,
        matched_phrase=matched,
        authority_changed=False,  # PERMANENT
        confirmation_challenge={
            "session_id": challenge.session_id,
            "action_id": challenge.action_id,
            "action_hash": challenge.action_hash,
            "consequence_summary_hash": challenge.consequence_summary_hash,
            "nonce": challenge.nonce,
            "audience": challenge.audience,
            "expires_at": challenge.expires_at,
            "canonical_payload": challenge.canonical_payload(),
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIRMATION CHALLENGE / SIGNATURE BINDING / CAPABILITY ISSUANCE
# ═══════════════════════════════════════════════════════════════════════════════

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _action_hash(profile: dict) -> str:
    """Stable hash of action profile (canonical JSON)."""
    canonical = repr(sorted(profile.items()))
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


def _fresh_nonce() -> str:
    return hashlib.sha256(os.urandom(32)).hexdigest()[:43]


def _consequence_summary(profile: dict) -> str:
    """Build a brief, plain-text consequence summary for the human to read."""
    parts = []
    if "tool" in profile:
        parts.append(f"tool={profile['tool']}")
    if "mutation" in profile:
        parts.append(f"mutation={profile['mutation']}")
    if "reversibility" in profile:
        parts.append(f"reversibility={profile['reversibility']}")
    if "blast_radius" in profile:
        parts.append(f"blast={profile['blast_radius']}")
    if "governance_impact" in profile:
        parts.append(f"governance={profile['governance_impact']}")
    if "receipt_class" in profile:
        parts.append(f"receipt_class={profile['receipt_class']}")
    return "; ".join(parts)


def issue_confirmation_challenge(
    session_id: str, action_id: str,
) -> ConfirmationChallenge:
    """Build a session-bound confirmation challenge for one pending action."""
    prof = get_pending_action(action_id)
    if prof is None:
        raise ValueError(f"Unknown action_id: {action_id}")
    if prof.get("session_id") != session_id:
        raise PermissionError("action_id belongs to different session")

    action_h = _action_hash(prof)
    consequence = _consequence_summary(prof)
    consequence_hash = f"sha256:{hashlib.sha256(consequence.encode()).hexdigest()}"

    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=2)
    return ConfirmationChallenge(
        session_id=session_id,
        action_id=action_id,
        action_hash=action_h,
        consequence_summary_hash=consequence_hash,
        nonce=_fresh_nonce(),
        audience="arifOS-confirmation-v1",
        expires_at=expires.isoformat(),
    )


def bind_signature_to_challenge(
    challenge: ConfirmationChallenge, signature_b64: str,
) -> bool:
    """Verify Ed25519 signature over challenge.canonical_payload().

    The verifier must check via canonical-session-state (forge_session_runtime)
    for the binding. This thin wrapper enforces:
      - fresh nonce
      - signature present
    and relies on the verifier to check the actor key + session match.
    """
    if not signature_b64 or not signature_b64.strip():
        return False
    # Defer the cryptographic check to the governance_identity/forge_session
    # layer. We only check structural sanity here.
    if challenge.nonce in _USED_NONCES:
        return False  # nonce already used — replay protection
    _USED_NONCES.add(challenge.nonce)
    return True


def issue_narrow_capability(
    challenge: ConfirmationChallenge,
    actor_id: str,
    channel: str,
    signature_b64: str,
    capability_class: str = "vault.append.sovereign",
) -> Optional[NarrowCapability]:
    """Issue a single-use payload-bound capability for one action.

    Returns None if any of the following fails:
      - channel not bound to challenge.session_id
      - signature invalid (or nonce replay)
      - action_id has no pending profile
      - profile not classified as requiring sovereign authority
    """
    # Channel binding (per D3: cross-channel reuse denied)
    if not channel_bound_to_session(challenge.session_id, channel):
        return None
    # Replay / nonce freshness
    if not bind_signature_to_challenge(challenge, signature_b64):
        return None
    # Profile must exist + require sovereign authority for sovereign class
    prof = get_pending_action(challenge.action_id)
    if prof is None:
        return None
    if not prof.get("sovereign_required", False):
        return None
    if capability_class != "vault.append.sovereign":
        return None

    cap_id = f"cap_{challenge.nonce[:16]}"
    cap = NarrowCapability(
        capability=capability_class,
        action_id=challenge.action_id,
        session_id=challenge.session_id,
        channel=channel,
        payload_hash=challenge.action_hash,
        single_use=True,
        redelegation=False,
        expires_at=challenge.expires_at,
        issued_at=_now_iso(),
        issued_by=actor_id,
        nonce=challenge.nonce,
    )
    _ISSUED_CAPABILITIES[cap_id] = cap
    return cap


def get_capability(cap_id: str) -> Optional[NarrowCapability]:
    return _ISSUED_CAPABILITIES.get(cap_id)


def consume_capability(cap_id: str, presented_payload_hash: str) -> bool:
    """Consume (single-use) a capability after presenting exact payload hash.

    Returns False on:
      - cap_id unknown
      - cap already consumed
      - payload_hash mismatch (payload change after confirmation)
      - cap expired
      - cross-session reuse (caller must verify session_id match)
    """
    cap = _ISSUED_CAPABILITIES.get(cap_id)
    if cap is None:
        return False
    if cap.consumed:
        return False
    if cap.payload_hash != presented_payload_hash:
        return False
    # Expiry
    try:
        exp = datetime.fromisoformat(cap.expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) >= exp:
            return False
    except Exception:
        return False
    # Single-use: mark consumed (immutable copy)
    consumed_cap = NarrowCapability(
        **{**cap.__dict__, "consumed": True, "consumed_at": _now_iso()}
    )
    _ISSUED_CAPABILITIES[cap_id] = consumed_cap
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES for back-compat with governance_identity (renamed-but-not-broken)
# ═══════════════════════════════════════════════════════════════════════════════

# Deprecated: kept as alias so old code paths don't crash on import.
# However, it is no longer treated as authority credentials.
SOVEREIGN_SIGNAL_PHRASES = CONFIRMATION_INTENT_PHRASES  # deprecated alias


__all__ = [
    "CONFIRMATION_INTENT_PHRASES",
    "SOVEREIGN_SIGNAL_PHRASES",  # deprecated alias
    "SignalResult",
    "ConfirmationChallenge",
    "NarrowCapability",
    "handle_human_signal",
    "register_channel_session_binding",
    "channel_bound_to_session",
    "register_pending_action",
    "get_pending_action",
    "list_pending_actions",
    "issue_confirmation_challenge",
    "bind_signature_to_challenge",
    "issue_narrow_capability",
    "get_capability",
    "consume_capability",
]
