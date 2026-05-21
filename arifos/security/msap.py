from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from nacl.signing import VerifyKey

# ─────────────────────────────────────────────────────────────────────────────
# MSAP Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SovereignAckChallenge:
    challenge_id: str
    nonce: str
    issued_at: float
    expires_at: float
    actor_id: str
    session_id: str
    payload_hash: str
    judge_state_hash: str
    constitutional_chain_id: str
    used: bool = False


@dataclass
class SovereignAckPacket:
    protocol: str = "MSAP"
    version: str = "0.1"
    actor_id: str = ""
    session_id: str = ""
    constitutional_chain_id: str = ""
    action: str = "VAULT_SEAL"
    irreversibility_class: str = "F1_AMANAH"
    human_intent: str = ""
    payload_hash: str = ""
    judge_state_hash: str = ""
    nonce: str = ""
    nonce_issued_at: str = ""
    expires_at: str = ""
    actor_public_key_id: str = ""
    signature_alg: str = "Ed25519"
    signature: str = ""
    continuity: dict = field(default_factory=dict)


@dataclass
class SovereignAckVerificationResult:
    signed_ack_valid: bool
    reason: str
    zkpc_level: int
    zkpc_mode: str = "MSAP_v0_1_PRE_ZKPC"
    personhood_verified: bool = False
    continuity_mode: str = "pre_zkpc_key_continuity"
    ack_id: Optional[str] = None
    payload_hash: Optional[str] = None
    judge_state_hash: Optional[str] = None
    actor_id: Optional[str] = None
    session_id: Optional[str] = None
    nonce_hash: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Nonce Store (In-memory for v0.1)
# ─────────────────────────────────────────────────────────────────────────────

_NONCE_DB: Dict[str, SovereignAckChallenge] = {}


def create_challenge(
    actor_id: str,
    session_id: str,
    payload_hash: str,
    judge_state_hash: str,
    constitutional_chain_id: str,
    action: str = "VAULT_SEAL",
    ttl_seconds: int = 300,
) -> SovereignAckChallenge:
    nonce = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    now = time.time()
    challenge_id = f"ACKCHAL-{nonce[:8]}"

    challenge = SovereignAckChallenge(
        challenge_id=challenge_id,
        nonce=nonce,
        issued_at=now,
        expires_at=now + ttl_seconds,
        actor_id=actor_id,
        session_id=session_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_state_hash,
        constitutional_chain_id=constitutional_chain_id,
    )

    _NONCE_DB[nonce] = challenge
    return challenge


# ─────────────────────────────────────────────────────────────────────────────
# MSAP Verification Logic
# ─────────────────────────────────────────────────────────────────────────────


def get_canonical_digest_string(packet: SovereignAckPacket) -> str:
    parts = [
        f"MSAP:{packet.version}",
        f"actor_id={packet.actor_id}",
        f"session_id={packet.session_id}",
        f"constitutional_chain_id={packet.constitutional_chain_id}",
        f"action={packet.action}",
        f"irreversibility_class={packet.irreversibility_class}",
        f"payload_hash={packet.payload_hash}",
        f"judge_state_hash={packet.judge_state_hash}",
        f"nonce={packet.nonce}",
        f"expires_at={packet.expires_at}",
    ]
    return "\n".join(parts)


def verify_sovereign_ack(
    packet_dict: dict,
    registered_public_keys: Dict[str, str],
) -> SovereignAckVerificationResult:
    """
    Verify an MSAP v0.1 ACK packet.
    """
    try:
        packet = SovereignAckPacket(**packet_dict)
    except Exception as e:
        return SovereignAckVerificationResult(False, f"MALFORMED_PACKET: {e}", 0)

    # 1. Basic Protocol Checks
    if packet.protocol != "MSAP":
        return SovereignAckVerificationResult(False, "INVALID_PROTOCOL", 0)
    if packet.version != "0.1":
        return SovereignAckVerificationResult(False, "UNSUPPORTED_VERSION", 0)

    # 2. Nonce Check
    challenge = _NONCE_DB.get(packet.nonce)
    if not challenge:
        return SovereignAckVerificationResult(False, "NONCE_NOT_FOUND", 0)
    if challenge.used:
        return SovereignAckVerificationResult(False, "REPLAY_ATTEMPT", 0)
    if time.time() > challenge.expires_at:
        return SovereignAckVerificationResult(False, "NONCE_EXPIRED", 0)

    # 3. Binding Checks
    if packet.actor_id != challenge.actor_id:
        return SovereignAckVerificationResult(False, "ACTOR_MISMATCH", 0)
    if packet.session_id != challenge.session_id:
        return SovereignAckVerificationResult(False, "SESSION_MISMATCH", 0)
    if packet.payload_hash != challenge.payload_hash:
        return SovereignAckVerificationResult(False, "PAYLOAD_HASH_MISMATCH", 0)
    if packet.judge_state_hash != challenge.judge_state_hash:
        return SovereignAckVerificationResult(False, "JUDGE_HASH_MISMATCH", 0)
    if packet.constitutional_chain_id != challenge.constitutional_chain_id:
        return SovereignAckVerificationResult(False, "CHAIN_MISMATCH", 0)

    # 4. Signature Verification
    pubkey_b64 = registered_public_keys.get(packet.actor_id)
    if not pubkey_b64:
        return SovereignAckVerificationResult(False, "UNKNOWN_ACTOR_KEY", 0)

    try:
        # Decode public key (standard b64 or b64url)
        try:
            vk_bytes = base64.urlsafe_b64decode(pubkey_b64 + "==")
        except Exception:
            vk_bytes = base64.b64decode(pubkey_b64)

        vk = VerifyKey(vk_bytes)

        canonical_str = get_canonical_digest_string(packet)
        digest = hashlib.sha256(canonical_str.encode("utf-8")).digest()

        sig_bytes = base64.urlsafe_b64decode(packet.signature + "==")
        vk.verify(digest, sig_bytes)
    except Exception as e:
        return SovereignAckVerificationResult(False, f"SIGNATURE_INVALID: {e}", 0)

    # Mark nonce used
    challenge.used = True

    # Calculate ZKPC Level
    # Phase 0: Respect circuit quarantine. If toy circuit is quarantined,
    # NEVER promote to level 2 regardless of dev override.
    zkpc_quarantined = os.getenv("ARIFOS_ZKPC_CIRCUIT_MODE", "TOY_QUARANTINED").upper() in (
        "TOY_QUARANTINED",
        "DISABLED",
    )
    zkpc_level = 1
    dev_override = os.getenv("ARIFOS_DEV_ALLOW_MSAP_LEVEL2", "false").lower() == "true"

    if dev_override and not zkpc_quarantined:
        zkpc_level = 2
    elif dev_override and zkpc_quarantined:
        # Dev override requested but circuit is quarantined — stay at 1
        pass

    reason = "ACK_OK"
    if zkpc_quarantined:
        reason = "ACK_OK_BUT_ZKPC_QUARANTINED_TOY_CIRCUIT_NO_AUTHORITY"
    elif dev_override:
        reason = "DEV_ONLY_MSAP_PROMOTED_TO_LEVEL2_NOT_TRUE_PERSONHOOD"

    return SovereignAckVerificationResult(
        signed_ack_valid=True,
        reason=reason,
        zkpc_level=zkpc_level,
        ack_id=f"ACK-{packet.nonce[:12]}",
        payload_hash=packet.payload_hash,
        judge_state_hash=packet.judge_state_hash,
        actor_id=packet.actor_id,
        session_id=packet.session_id,
        nonce_hash=hashlib.sha256(packet.nonce.encode()).hexdigest(),
    )
